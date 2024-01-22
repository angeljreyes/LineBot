import discord
from discord.ext import commands
from discord import app_commands

import db
import core
import pagination
import exceptions
from tags import TagSafeInteraction, TagContext


@app_commands.guild_only()
class TagsCog(
        commands.GroupCog,
        group_name='tag',
        description='Añade o usa tags tuyos o de otros usuarios'
    ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    # tag show
    @app_commands.command(name='show')
    @app_commands.rename(tag_name='tag')
    async def tag_show(
            self,
            interaction: discord.Interaction[commands.Bot],
            tag_name: app_commands.Range[str, 1, 32]
        ):
        """Muestra el contenido de un tag

        tag_name
            Nombre de un tag
        """
        tag_ctx = TagContext(interaction)
        tag = tag_ctx.get_tag(tag_name)
        if tag_ctx.channel.is_nsfw() or not bool(tag.nsfw):
            ctx = await self.bot.get_context(interaction)
            await interaction.response.send_message(
                await commands.clean_content().convert(ctx, tag.content))
        else:
            await interaction.response.send_message(
                core.Warning.error('Este tag solo puede mostrarse en canales NSFW'),
                ephemeral=True
            )


    # tag toggle
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.guild_id)
    @app_commands.command(name='toggle')
    async def tag_toggle(self, interaction: discord.Interaction[commands.Bot]):
        """Activa los tags en el servidor"""
        tag_interaction = TagSafeInteraction(interaction)
        if not tag_interaction.channel.permissions_for(tag_interaction.member).manage_guild:
            await interaction.response.send_message(
                core.Warning.error(
                    'Necesitas permiso de gestionar el '
                    'servidor para activar o desactivar los tags'
                ),
                ephemeral=True
            )
            return

        db.cursor.execute(
            "SELECT guild FROM tagsenabled WHERE guild=?",
            (tag_interaction.guild_id,)
        )
        check: tuple[int] | None = db.cursor.fetchone()
        if check is None:
            confirmation = core.Confirm(interaction, interaction.user)
            await interaction.response.send_message(
                core.Warning.question(
                    'Los tags en este servidor están '
                    'desactivados. ¿Quieres activarlos?'
                ),
                view=confirmation,
                ephemeral=True
            )
            await confirmation.wait()

            if confirmation.value is None:
                return

            confirmation.clear_items()

            if confirmation.value:
                db.cursor.execute(
                    "INSERT INTO tagsenabled VALUES(?)",
                    (tag_interaction.guild_id,)
                )
                content = core.Warning.success(
                    'Se activaron los tags en este servidor'
                ),

            else:
                content = core.Warning.cancel(
                    'No se activarán los tags en este servidor'
                )


        else:
            confirmation = core.Confirm(interaction, interaction.user)
            await interaction.response.send_message(
                core.Warning.question(
                    'Los tags en este servidor están activados. '
                    '¿Quieres desactivarlos?'
                ),
                view=confirmation,
                ephemeral=True
            )
            await confirmation.wait()

            if confirmation.value is None:
                return

            confirmation.clear_items()

            if confirmation.value:
                db.cursor.execute(
                    "DELETE FROM tagsenabled WHERE guild=?",
                    (tag_interaction.guild_id,)
                )
                content = core.Warning.success(
                    'Se desactivaron los tags en este servidor'
                )

            else:
                content = core.Warning.cancel(
                        'No se desactivarán los tags en este servidor'
                    )

        await confirmation.last_interaction.response.edit_message(
            content=content,
            view=confirmation
        )
        
        db.conn.commit()


    # tag add
    @app_commands.checks.cooldown(1, 10)
    @app_commands.command(name='add')
    @app_commands.rename(tag_name='nombre', tag_content='contenido')
    async def tag_add(
            self,
            interaction: discord.Interaction[commands.Bot],
            tag_name: app_commands.Range[str, 1, 32], 
            tag_content: str,
            nsfw: bool = False
        ):
        """Crea un tag

        tag_name
            Nombre del tag que quieres crear
        tag_content
            Contenido del tag que quieres crear
        nsfw
            Determina si el tag puede mostrarse únicamente en canales NSFW
        """
        tag_ctx = TagContext(interaction)
        tag_ctx.check_name(tag_name)
        if tag_ctx.channel.is_nsfw():
            nsfw = True
        tag_ctx.add_tag(tag_name, tag_content, nsfw)
        ctx = await self.bot.get_context(interaction)
        clean_name = await commands.clean_content().convert(ctx, tag_name)
        await interaction.response.send_message(core.Warning.success(
            f'Se agregó el tag **{clean_name}**'
        ))


    # tag gift
    @app_commands.checks.cooldown(1, 10)
    @app_commands.command(name='gift')
    @app_commands.rename(tag_name='tag', user='usuario')
    async def tag_gift(
            self,
            interaction: discord.Interaction[commands.Bot], 
            tag_name: app_commands.Range[str, 1, 32],
            user: discord.Member
        ):
        """Regala un tag a otro usuario"""
        tag_ctx = TagContext(interaction)
        if user == tag_ctx.member:
            await interaction.response.send_message(
                core.Warning.error('No puedes regalarte un tag a ti mismo'),
                ephemeral=True
            )
            return
        if user.bot:
            await interaction.response.send_message(
                core.Warning.error('No puedes regalarle un tag a un bot'),
                ephemeral=True
            )
            return

        tag = tag_ctx.get_tag(tag_name)
        if tag.user != interaction.user:
            await interaction.response.send_message(
                core.Warning.error('No puedes regalar el tag de otra persona'),
                ephemeral=True
            )
            return

        gift_permission = core.Confirm(interaction, user)
        ctx = await self.bot.get_context(interaction)
        clean_tag_name = await commands.clean_content().convert(ctx, tag.name)
        await interaction.response.send_message(
            core.Warning.question(
                f'{user.mention} ¿Quieres aceptar el tag '
                f'**{clean_tag_name}** por parte de {interaction.user.name}?'
            ),
            view=gift_permission
        )
        await gift_permission.wait()

        if gift_permission.value is None:
            return
        
        gift_permission = gift_permission.clear_items()

        if gift_permission.value:
            tag.gift(user)
            ctx = await self.bot.get_context(interaction)
            content = core.Warning.success(
                f'El tag **{await commands.clean_content().convert(ctx, tag.name)}** '
                'ha sido regalado a {tag.user.name} por parte de {interaction.user.name}'
            )

        else:
            content = core.Warning.cancel(
                f'{interaction.user.mention} El regalo fue rechazado'
            )

        await gift_permission.last_interaction.response.edit_message(content=content, view=gift_permission)


    # tag rename
    @app_commands.checks.cooldown(1, 5)
    @app_commands.command(name='rename')
    @app_commands.rename(old_name='tag', new_name='nuevo')
    async def tag_rename(
            self,
            interaction: discord.Interaction[commands.Bot],
            old_name: app_commands.Range[str, 1, 32],
            new_name: app_commands.Range[str, 1, 32]
        ):
        """Cambia el nombre de uno de tus tags"""
        tag_ctx = TagContext(interaction)
        tag_ctx.check_name(new_name)
        tag = tag_ctx.get_tag(old_name)

        if tag.user != tag_ctx.member:
            await interaction.response.send_message(
                core.Warning.error('No puedes renombarar el tag de otro usuario'),
                ephemeral=True
            )
            return

        if tag.name == new_name:
            await interaction.response.send_message(
                core.Warning.error('No puedes ponerle el mismo nombre a un tag'),
                ephemeral=True
            )
            return

        tag.rename(new_name)
        ctx = await self.bot.get_context(interaction)
        clean_old_name = await commands.clean_content().convert(ctx, old_name)
        clean_new_name = await commands.clean_content().convert(ctx, new_name)
        await interaction.response.send_message(core.Warning.success(
            f'El nombre del tag **{clean_old_name}** ha sido'
            f'cambiado a **{clean_new_name}**'
        ))


    # tag edit
    @app_commands.checks.cooldown(1, 10)
    @app_commands.command(name='edit')
    @app_commands.rename(tag_name='tag', tag_content='contenido')
    async def tag_edit(
            self,
            interaction: discord.Interaction[commands.Bot],
            tag_name: app_commands.Range[str, 1, 32],
            tag_content: str,
            nsfw: bool = False
        ):
        """Edita el contenido de uno de tus tags

        tag_name
            Nombre del tag que quieres editar
        tag_content
            Nuevo contenido del tag
        nsfw
            Determina si el tag puede mostrarse únicamente en canales NSFW
        """
        tag_ctx = TagContext(interaction)
        tag = tag_ctx.get_tag(tag_name)
        if interaction.user != tag.user:
            await interaction.response.send_message(core.Warning.error('No puedes editar tags de otros usuarios'), ephemeral=True)
            return

        if tag_ctx.channel.is_nsfw():
            nsfw = True

        tag.edit(tag_content, nsfw)
        ctx = await self.bot.get_context(interaction)
        clean_tag_name = await commands.clean_content().convert(ctx, tag_name)
        await interaction.response.send_message(core.Warning.success(
            f'Se editó el tag **{clean_tag_name}**'
        ))
        


    # tag delete
    @app_commands.checks.cooldown(1, 5)
    @app_commands.command(name='delete')
    @app_commands.rename(tag_name='tag')
    async def tag_delete(
            self,
            interaction: discord.Interaction[commands.Bot],
            tag_name: app_commands.Range[str, 1, 32]
        ):
        """Elimina uno de tus tags"""
        tag_ctx = TagContext(interaction)
        tag = tag_ctx.get_tag(tag_name)
        if interaction.user != tag.user:
            await interaction.response.send_message(core.Warning.error(
                'No puedes eliminar tags de otros usuarios'
            ), ephemeral=True)
            return

        confirmation = core.Confirm(interaction, interaction.user)
        ctx = await self.bot.get_context(interaction)
        clean_tag_name = await commands.clean_content().convert(ctx, tag_name)
        await interaction.response.send_message(core.Warning.question(
            f'¿Quieres eliminar el tag **{clean_tag_name}**?'
        ), view=confirmation)
        await confirmation.wait()
        
        if confirmation.value is None:
            return
        
        confirmation = confirmation.clear_items()

        if confirmation.value:
            tag.delete()
            await confirmation.last_interaction.response.edit_message(
                content=core.Warning.success(
                    f'El tag **{clean_tag_name}** ha sido eliminado'
                ),
                view=confirmation
            )
        
        else:
            await confirmation.last_interaction.response.edit_message(
                content=core.Warning.cancel(f'El tag no será eliminado'),
                view=confirmation
            )


    # tag forcedelete
    @app_commands.command(name='forcedelete')
    @core.owner_only()
    async def forcedelete(
            self,
            interaction: discord.Interaction[commands.Bot],
            tag_name: app_commands.Range[str, 1, 32],
            guild_id: str | None,
            silent: bool = False
        ):
        """Reservado"""
        tag_ctx = TagContext(interaction, bypass=True)
        guild = interaction.guild if guild_id is None else self.bot.get_guild(int(guild_id))

        if guild is None:
            await interaction.response.send_message(
                core.Warning.error('No se encontró el servidor')
            )
            return

        tag = tag_ctx.get_tag(tag_name, guild.id)
        tag.delete()
        ctx = await self.bot.get_context(interaction)
        clean_tag_name = await commands.clean_content().convert(ctx, tag_name)
        await interaction.response.send_message(core.Warning.success(
            f'El tag **{clean_tag_name}** ha sido eliminado'
        ), ephemeral=silent)


    # tag owner
    @app_commands.checks.cooldown(1, 3)
    @app_commands.command(name='owner')
    @app_commands.rename(tag_name='tag')
    async def tag_owner(
            self,
            interaction: discord.Interaction[commands.Bot],
            tag_name: app_commands.Range[str, 1, 32]
        ):
        """Muestra el propietario de un tag"""
        tag_ctx = TagContext(interaction)
        tag = tag_ctx.get_tag(tag_name)
        ctx = await self.bot.get_context(interaction)
        clean_tag_name = await commands.clean_content().convert(ctx, tag.name)
        await interaction.response.send_message(core.Warning.info(
            f'El dueño del tag **{clean_tag_name}** es `{str(tag.user)}`'))


    # tag list
    @app_commands.checks.cooldown(1, 10)
    @app_commands.command(name='list')
    @app_commands.rename(user='usuario')
    async def tag_list(
            self,
            interaction: discord.Interaction[commands.Bot],
            user: discord.Member | None
        ):
        """Muestra una lista de tus tags o de los tags de otro usuario"""
        tag_ctx = TagContext(interaction)
        user = user or tag_ctx.member
        tag_list = [f'"{tag}"' for tag in tag_ctx.get_member_tags(user)]
        if not tag_list:
            raise exceptions.NonExistentTagError('This user does not have any tags', ctx=tag_ctx)
        pages = pagination.Page.from_list(
            interaction,
            f'Tags de {user.name}',
            tag_list
        )
        paginator = pagination.Paginator.optional(
            interaction,
            pages=pages,
            entries=len(tag_list)
        )
        await interaction.response.send_message(embed=pages[0].embed, view=paginator) # type: ignore


    # tag serverlist
    @app_commands.checks.cooldown(1, 20)
    @app_commands.command(name='serverlist')
    async def tag_serverlist(self, interaction: discord.Interaction[commands.Bot]):
        """Muestra los tags de todo el servidor"""
        tag_ctx = TagContext(interaction)
        tag_list = [f'"{tag}"' for tag in tag_ctx.get_guild_tags()]
        if not tag_list:
            raise exceptions.NonExistentTagError('This server does not have any tags', ctx=tag_ctx)
        pages = pagination.Page.from_list(interaction, f'Tags de {interaction.guild}', tag_list)
        paginator = pagination.Paginator.optional(
            interaction,
            pages=pages,
            entries=len(tag_list)
        )
        await interaction.response.send_message(embed=pages[0].embed, view=paginator) # type: ignore


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TagsCog(bot), guilds=core.bot_guilds) # type: ignore
