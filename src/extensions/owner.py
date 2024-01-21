from collections.abc import Awaitable, Callable, Sequence
from math import floor
from re import findall
from time import perf_counter
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

import core
import db
from exceptions import EvalReturn


evalcmd: Callable[[discord.Interaction], Awaitable[Any]] | None = None


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    # die
    @app_commands.command()
    @core.owner_only()
    async def die(self, interaction: discord.Interaction):
        """Apaga el bot"""
        await interaction.response.send_message(u'\U0001f480', ephemeral=True)
        core.logging.info('Trying to end execution through /die command')
        try:
            await self.bot.close()
        except RuntimeError:
            pass


    # getmsg
    @app_commands.command()
    @core.owner_only()
    async def getmsg(self, interaction: discord.Interaction, id: str):
        """Obtiene los datos de un mensaje"""
        if not isinstance(interaction.channel, discord.abc.Messageable):
            return

        msg = await interaction.channel.fetch_message(int(id))
        await interaction.response.send_message(f'```py\n{msg}\n```', ephemeral=True)


    # eval
    @app_commands.command(name='eval')
    @core.owner_only()
    async def eval_(
        self,
        interaction: discord.Interaction[commands.Bot],
        ephemeral: bool = False,
        silent: bool = False,
        expression: bool = True
    ):
        """Ejecuta código"""
        global evalcmd
        global _return
        INDENT = ' ' * 4
        def _return(value: Any) -> None:
            raise EvalReturn(value)

        class CodeModal(discord.ui.Modal, title='Eval'):
            answer = discord.ui.TextInput(label='Código', style=discord.TextStyle.paragraph)

            def __init__(self, bot: commands.Bot):
                super().__init__()
                self.bot = bot

            async def on_submit(self, sub_interaction: discord.Interaction):
                global evalcmd
                global _return
                return_value: Any | None = None
                await sub_interaction.response.defer(ephemeral=ephemeral or silent, thinking=True)

                code = self.answer.value
                code_lines = [INDENT + line for line in code.splitlines()]
                if not silent and expression:
                    return_line = code_lines.pop()
                    whitespace: str = findall(r'^\s+', return_line)[0]
                    code_lines.append(f'{whitespace}_return({return_line.strip()})')
                code = '\n'.join(code_lines)

                code = ('global evalcmd\n'
                        'async def evalcmd(interaction):\n'
                        f'{INDENT}global _return\n'
                        f'{code}')

                start = perf_counter()
                try:
                    exec(code)
                    await evalcmd(sub_interaction) # type: ignore
                except EvalReturn as e:
                    return_value = e.value
                except Exception as e:
                    return_value = e
                end = perf_counter()

                if silent:
                    await sub_interaction.followup.send(u'\U00002705')
                    return

                types = ''
                sub_value = return_value
                if not silent:
                    while True:
                        types += str(type(sub_value))
                        if (isinstance(sub_value, Sequence)
                            and not isinstance(sub_value, str)
                            and len(sub_value)):
                            sub_value = sub_value[0]
                            continue
                        break

                embed = discord.Embed(
                    title='Resultados del eval',
                    description=(
                        f'Tipo de dato y resultado:\n'
                        f'```py\n{types}\n```'
                        f'\n```py\n{return_value}\n```'
                    ),
                    colour=db.default_color(sub_interaction)
                ).set_footer(text=f'Ejecutado en {floor((end - start) * 1000)}ms')
                await sub_interaction.followup.send(embed=embed)

        await interaction.response.send_modal(CodeModal(self.bot))


    # reload
    @app_commands.command()
    @core.owner_only()
    async def reload(self, interaction: discord.Interaction, extension: str, sync: bool = False):
        """Recarga un módulo"""
        await interaction.response.defer(ephemeral=True, thinking=True)
        await self.bot.reload_extension('extensions.' + extension)
        core.config_commands(self.bot)
        core.logger.info(f'"{extension}" extension reloaded')
        if sync:
            await core.sync_tree(self.bot)
        await interaction.followup.send(u'\U00002705')


    # unload
    @app_commands.command()
    @core.owner_only()
    async def unload(self, interaction: discord.Interaction, extension: str, sync: bool = False):
        """Descarga un módulo"""
        await interaction.response.defer(ephemeral=True, thinking=True)
        await self.bot.unload_extension('extensions.' + extension)
        core.config_commands(self.bot)
        core.logger.info(f'"{extension}" extension unloaded')
        if sync:
            await core.sync_tree(self.bot)
        await interaction.followup.send(u'\U00002705')


    # load
    @app_commands.command()
    @core.owner_only()
    async def load(self, interaction: discord.Interaction, extension: str, sync: bool = False):
        """Carga un módulo"""
        await interaction.response.defer(ephemeral=True, thinking=True)
        await self.bot.load_extension('extensions.' + extension)
        core.config_commands(self.bot)
        core.logger.info(f'"{extension}" extension unloaded')
        if sync:
            await core.sync_tree(self.bot)
        await interaction.followup.send(u'\U00002705')


    # blacklist
    @app_commands.command()
    @core.owner_only()
    async def blacklist(self, interaction: discord.Interaction, user: discord.User):
        """Mete o saca a un usuario de la blacklist"""
        if db.check_blacklist(interaction, user, False):
            db.cursor.execute("INSERT INTO blacklist VALUES(?)", (user.id,))
            await interaction.response.send_message(u'\U00002935', ephemeral=True)
        
        else:
            db.cursor.execute("DELETE FROM blacklist WHERE user=?", (user.id,))
            await interaction.response.send_message(u'\U00002934', ephemeral=True)

        db.conn.commit()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Owner(bot), guilds=core.bot_guilds) # type: ignore
