from typing import Self, cast

import discord
from discord.ext import commands
from discord import app_commands

import db
import exceptions
import core


type RawTag = tuple[int, int, str, str, int]


class Tag:
    __slots__ = ('interaction', 'guild', 'user', 'name', 'content', 'nsfw')

    def __init__(self, interaction: discord.Interaction, guild_id: int, user_id: int, name: str, content: str, nsfw: bool):
        self.interaction = interaction

        guild = interaction.client.get_guild(guild_id)
        if guild is None:
            raise KeyError('Invalid guild')
        self.guild = guild

        user = interaction.client.get_user(user_id)
        if user is None:
            raise KeyError('Invalid user')
        self.user = user

        self.name = name
        self.content = content
        self.nsfw = bool(nsfw)

    def __str__(self) -> str:
        return self.name

    def gift(self, user: discord.Member) -> None:
        db.cursor.execute("UPDATE tags SET user=? WHERE guild=? AND name=?", (user.id, self.guild.id, self.name))
        db.conn.commit()
        self.user = user

    def rename(self, name: str) -> None:
        db.cursor.execute("UPDATE tags SET name=? WHERE guild=? AND name=?", (name, self.guild.id, self.name))
        db.conn.commit()
        self.name = name

    def edit(self, content: str, nsfw: bool) -> None:
        self.content = content
        self.nsfw = nsfw
        db.cursor.execute("UPDATE tags SET content=?, nsfw=? WHERE guild=? AND name=?", (self.content, int(self.nsfw), self.guild.id, self.name))
        db.conn.commit()

    def delete(self) -> None:
        db.cursor.execute("DELETE FROM tags WHERE guild=? AND name=?", (self.guild.id, self.name,))
        db.conn.commit()

    @classmethod
    def from_db(cls, interaction: discord.Interaction, data: RawTag) -> Self:
        return cls(
            interaction,
            guild_id=data[0],
            user_id=data[1],
            name=data[2],
            content=data[3],
            nsfw=bool(data[4])
        )


async def tag_check(interaction: discord.Interaction[commands.Bot]) -> None:
    if interaction.guild is None:
        raise Exception('The developer missed a guild_only check :(')
    
    db.cursor.execute("SELECT guild FROM tagsenabled WHERE guild=?", (interaction.guild.id,))
    check: tuple[int] | None = db.cursor.fetchone()

    if check is None:
        if interaction.channel is None:
            raise exceptions.DisabledTagsError('Invalid channel')

        member = cast(discord.Member, interaction.user)
        has_permission = interaction.channel.permissions_for(member).manage_guild
        toggle_command = await core.fetch_app_command(interaction, 'tag toggle')

        if toggle_command is not None:
            await interaction.response.send_message(core.Warning.info(
                'Los tags están desactivados en este servidor. ' +
                ('Actívalos ' if has_permission else 'Pídele a un administrador que los active ') +
                f'con el comando {toggle_command.mention}'
            ))

        raise exceptions.DisabledTagsError('Tags are not enabled on this guild')


def add_tag(interaction: discord.Interaction, name: str, content: str, nsfw: bool) -> None:
    if interaction.guild is None:
        raise Exception('The developer missed a guild_only check :(')
        
    db.cursor.execute("INSERT INTO tags VALUES(?,?,?,?,?)", (interaction.guild.id, interaction.user.id, name, content, int(nsfw)))
    db.conn.commit()


def check_tag_name(interaction: discord.Interaction, tag_name: str) -> None:
    for char in tag_name:
        if char in (' ', '_', '~', '*', '`', '|', ''):
            raise ValueError('Invalid characters detected')
    if tag_name in [tag.name for tag in get_guild_tags(interaction)]:
        raise exceptions.ExistentTagError(f'Tag "{tag_name}" already exists')


def get_tag(
        interaction: discord.Interaction,
        name: str,
        guild: discord.Guild | None = None,
        *,
        raises=True
    ) -> Tag | None:
    guild_id = interaction.guild_id if guild is None else guild.id
    db.cursor.execute("SELECT * FROM tags WHERE guild=? AND name=?", (guild_id, name))
    tag: RawTag | None = db.cursor.fetchone()
    if tag is not None:
        return Tag.from_db(interaction, tag)

    if raises:
        raise exceptions.NonExistentTagError('This tag does not exist')
    
    return None


def get_member_tags(interaction: discord.Interaction, user: discord.Member, *, raises=False) -> list[Tag]:
    if interaction.guild is None:
        raise Exception('The developer missed a guild_only check :(')
        
    db.cursor.execute("SELECT * FROM tags WHERE guild=? AND user=?", (interaction.guild.id, user.id))
    tags: list[RawTag] = db.cursor.fetchall()
    if tags:
        return [Tag.from_db(interaction, tag) for tag in tags]

    if raises:
        raise exceptions.NonExistentTagError('This user doesn\'t have tags')

    return []


def get_guild_tags(interaction: discord.Interaction, *, raises=False) -> list[Tag]:
    if interaction.guild is None:
        raise Exception('The developer missed a guild_only check :(')
        
    db.cursor.execute("SELECT * FROM tags WHERE guild=?", (interaction.guild.id,))
    tags: list[RawTag] = db.cursor.fetchall()

    if tags:
        return [Tag.from_db(interaction, tag) for tag in tags]

    if raises:
        raise exceptions.NonExistentTagError('This server doesn\'t have tags')

    return []


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
    async def tag_show(self, interaction: discord.Interaction, tag_name: app_commands.Range[str, 1, 32]):
        """Muestra el contenido de un tag

        tag_name
            Nombre de un tag
        """
        await tag_check(interaction)
        tag = get_tag(interaction, tag_name)
        if not (not interaction.channel.is_nsfw() and bool(tag.nsfw)):
            await interaction.response.send_message(await commands.clean_content().convert(interaction, tag.content))
        else:
            await interaction.response.send_message(core.Warning.error('Este tag solo puede mostrarse en canales NSFW'), ephemeral=True)


    # tag toggle
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.guild_id)
    @app_commands.command(name='toggle')
    async def tag_toggle(self, interaction: discord.Interaction):
        """Activa los tags en el servidor"""
        if interaction.channel.permissions_for(interaction.user).manage_guild:
            db.cursor.execute("SELECT guild FROM tagsenabled WHERE guild=?", (interaction.guild_id,))
            check: tuple[int] | None = db.cursor.fetchone()
            if check is None:
                confirmation = core.Confirm(interaction, interaction.user)
                await interaction.response.send_message(core.Warning.question('Los tags en este servidor están desactivados. ¿Quieres activarlos?'), view=confirmation, ephemeral=True)
                await confirmation.wait()

                if confirmation.value is None:
                    return

                confirmation.clear_items()

                if confirmation.value:
                    db.cursor.execute("INSERT INTO tagsenabled VALUES(?)", (interaction.guild_id,))
                    await confirmation.last_interaction.response.edit_message(content=core.Warning.success('Se activaron los tags en este servidor'), view=confirmation)

                else:
                    await confirmation.last_interaction.response.edit_message(content=core.Warning.cancel('No se activaran los tags en este servidor'), view=confirmation)

            else:
                confirmation = core.Confirm(interaction, interaction.user)
                await interaction.response.send_message(core.Warning.question('Los tags en este servidor están activados. ¿Quieres desactivarlos?'), view=confirmation, ephemeral=True)
                await confirmation.wait()

                if confirmation.value is None:
                    return

                confirmation.clear_items()

                if confirmation.value:
                    db.cursor.execute("DELETE FROM tagsenabled WHERE guild=?", (interaction.guild_id,))
                    await confirmation.last_interaction.response.edit_message(content=core.Warning.success('Se desactivaron los tags en este servidor'), view=confirmation)

                else:
                    await confirmation.last_interaction.response.edit_message(content=core.Warning.cancel('No se desactivarán los tags en este servidor'), view=confirmation)
            
            db.conn.commit()

        else:
            await interaction.response.send_message(core.Warning.error('Necesitas permiso de gestionar servidor para activar o desactivar los tags'), ephemeral=True)


    # tag add
    @app_commands.checks.cooldown(1, 10)
    @app_commands.command(name='add')
    @app_commands.rename(tag_name='nombre', tag_content='contenido')
    async def tag_add(
            self,
            interaction: discord.Interaction, 
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
        await tag_check(interaction)
        check_tag_name(interaction, tag_name)
        if interaction.channel.nsfw:
            nsfw = True
        add_tag(interaction, tag_name, tag_content, nsfw)
        await interaction.response.send_message(core.Warning.success(f'Se agregó el tag **{await commands.clean_content().convert(interaction, tag_name)}**'))


    # tag gift
    @app_commands.checks.cooldown(1, 10)
    @app_commands.command(name='gift')
    @app_commands.rename(tag_name='tag', user='usuario')
    async def tag_gift(
            self,
            interaction: discord.Interaction, 
            tag_name: app_commands.Range[str, 1, 32],
            user: discord.Member
        ):
        """Regala un tag a otro usuario"""
        await tag_check(interaction)
        if user == interaction.user:
            await interaction.response.send_message(core.Warning.error('No puedes regalarte un tag a ti mismo'), ephemeral=True)
        elif user.bot:
            await interaction.response.send_message(core.Warning.error('No puedes regalarle un tag a un bot'), ephemeral=True)
        else:
            tag: Tag = get_tag(interaction, tag_name)
            if tag.user.id != interaction.user.id:
                await interaction.response.send_message(core.Warning.error('No puedes regalar el tag de otra persona'), ephemeral=True)
                return
            gift_permission = core.Confirm(interaction, user)
            await interaction.response.send_message(core.Warning.question(f'{user.mention} ¿Quieres aceptar el tag **{await commands.clean_content().convert(interaction, tag.name)}** por parte de {interaction.user.name}?'), view=gift_permission)
            await gift_permission.wait()

            if gift_permission.value is None:
                return
            
            gift_permission = gift_permission.clear_items()

            if gift_permission.value:
                tag.gift(user)
                await gift_permission.last_interaction.response.edit_message(content=core.Warning.success(f'El tag **{await commands.clean_content().convert(interaction, tag.name)}** fue regalado a {await commands.clean_content().convert(interaction, tag.user.name)} por parte de {await commands.clean_content().convert(interaction, interaction.user.name)}'), view=gift_permission)

            elif not gift_permission.value:
                await gift_permission.last_interaction.response.edit_message(content=core.Warning.cancel(f'{interaction.user.mention} El regalo fue rechazado'), view=gift_permission)


    # tag rename
    @app_commands.checks.cooldown(1, 5)
    @app_commands.command(name='rename')
    @app_commands.rename(old_name='tag', new_name='nuevo')
    async def tag_rename(
            self,
            interaction: discord.Interaction,
            old_name: app_commands.Range[str, 1, 32],
            new_name: app_commands.Range[str, 1, 32]
        ):
        """Cambia el nombre de uno de tus tags"""
        await tag_check(interaction)
        check_tag_name(interaction, new_name)
        tag = get_tag(interaction, old_name)
        if tag.user.id == interaction.user.id:
            if tag.name == new_name:
                await interaction.response.send_message(core.Warning.error('No puedes ponerle el mismo nombre a un tag'), ephemeral=True)
            else:
                tag.rename(new_name)
                await interaction.response.send_message(core.Warning.success(f'El nombre del tag **{await commands.clean_content().convert(interaction, old_name)}** se ha cambiado a **{await commands.clean_content().convert(interaction, new_name)}**'))

        else:
            await interaction.response.send_message(core.Warning.error('No puedes renombarar el tag de otro usuario'), ephemeral=True)


    # tag edit
    @app_commands.checks.cooldown(1, 10)
    @app_commands.command(name='edit')
    @app_commands.rename(tag_name='tag', tag_content='contenido')
    async def tag_edit(
            self,
            interaction: discord.Interaction,
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
        await tag_check(interaction)
        tag = get_tag(interaction, tag_name)
        if interaction.user.id == tag.user.id:
            if interaction.channel.nsfw:
                nsfw = True
            tag.edit(tag_content, nsfw)
            await interaction.response.send_message(core.Warning.success(f'Se editó el tag **{await commands.clean_content().convert(interaction, tag_name)}**'))
        
        else:
            await interaction.response.send_message(core.Warning.error('No puedes editar tags de otros usuarios'), ephemeral=True)


    # tag delete
    @app_commands.checks.cooldown(1, 5)
    @app_commands.command(name='delete')
    @app_commands.rename(tag_name='tag')
    async def tag_delete(self, interaction: discord.Interaction, tag_name: app_commands.Range[str, 1, 32]):
        """Elimina uno de tus tags"""
        await tag_check(interaction)
        tag = get_tag(interaction, tag_name)
        if interaction.user.id == tag.user.id:
            confirmation = core.Confirm(interaction, interaction.user)
            await interaction.response.send_message(core.Warning.question(f'¿Quieres eliminar el tag **{await commands.clean_content().convert(interaction, tag_name)}**?'), view=confirmation)
            await confirmation.wait()
            
            if confirmation.value is None:
                return
            
            confirmation = confirmation.clear_items()

            if confirmation.value:
                tag.delete()
                await confirmation.last_interaction.response.edit_message(content=core.Warning.success(f'El tag **{await commands.clean_content().convert(interaction, tag_name)}** ha sido eliminado'), view=confirmation)
            
            elif not confirmation.value:
                await confirmation.last_interaction.response.edit_message(content=core.Warning.cancel(f'El tag no será eliminado'), view=confirmation)

        else: 
            await interaction.response.send_message(core.Warning.error('No puedes eliminar tags de otros usuarios'), ephemeral=True)


    # tag forcedelete
    @app_commands.command(name='forcedelete')
    @core.owner_only()
    async def forcedelete(
            self,
            interaction: discord.Interaction,
            tag_name: app_commands.Range[str, 1, 32],
            guild_id: str | None,
            silent: bool = False
        ):
        """Reservado"""
        guild = interaction.guild if guild_id is None else self.bot.get_guild(int(guild_id))
        tag = get_tag(interaction, tag_name, guild)
        tag.delete()
        await interaction.response.send_message(core.Warning.success(f'El tag **{await commands.clean_content().convert(interaction, tag_name)}** ha sido eliminado'), ephemeral=silent)


    # tag owner
    @app_commands.checks.cooldown(1, 3)
    @app_commands.command(name='owner')
    @app_commands.rename(tag_name='tag')
    async def tag_owner(self, interaction: discord.Interaction, tag_name: app_commands.Range[str, 1, 32]):
        """Muestra el propietario de un tag"""
        await tag_check(interaction)
        tag = get_tag(interaction, tag_name)
        await interaction.response.send_message(core.Warning.info(f'El dueño del tag **{await commands.clean_content().convert(interaction, tag.name)}** es `{await commands.clean_content().convert(interaction, str(tag.user))}`'))


    # tag list
    @app_commands.checks.cooldown(1, 10)
    @app_commands.command(name='list')
    @app_commands.rename(user='usuario')
    async def tag_list(self, interaction: discord.Interaction, user: discord.Member | None):
        """Muestra una lista de tus tags o de los tags de otro usuario"""
        await tag_check(interaction)
        if user is None:
            user = interaction.user
        tag_list = list(map(lambda tag: f'"{tag}"', get_member_tags(interaction, user, raises=True)))
        pages = pagination.Page.from_list(interaction, f'Tags de {user.name}', tag_list)
        paginator = pagination.Paginator.optional(interaction, pages=pages, entries=len(tag_list))
        await interaction.response.send_message(embed=pages[0].embed, view=paginator)


    # tag serverlist
    @app_commands.checks.cooldown(1, 20)
    @app_commands.command(name='serverlist')
    async def tag_serverlist(self, interaction: discord.Interaction):
        """Muestra los tags de todo el servidor"""
        await tag_check(interaction)
        tag_list = list(map(lambda tag: f'{tag.user.name}: "{tag}"', get_guild_tags(interaction, raises=True)))
        pages = pagination.Page.from_list(interaction, f'Tags de {interaction.guild}', tag_list)
        paginator = pagination.Paginator.optional(interaction, pages=pages, entries=len(tag_list))
        await interaction.response.send_message(embed=pages[0].embed, view=paginator)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TagsCog(bot), guilds=core.bot_guilds) # type: ignore
