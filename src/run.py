import asyncio
import tomllib
from os.path import isfile
from traceback import format_exc

from icecream import install
install() # Set up icecream
import discord
from discord import app_commands
from discord.ext import commands

if not isfile('../line.db'):
    print('The database wasn\'t found. Create a databse by running setup.py')
    exit(1)
import core
import tictactoe as ttt


# Create the bot client
class LineBot(commands.Bot):
    async def setup_hook(self) -> None:
        # Load the extensions which contain commands and utilities
        for extension in (
            'listeners',
            'bot',
            'modtxt',
            'util',
            'fun',
            'owner',
            'image'
        ):
            await bot.load_extension('extensions.' + extension)

        # Add descriptions to the commands from the core.descs dict and syncs the commands
        core.config_commands(self)
        if not isinstance(core.bot_guilds, core.Missing):
            for guild in core.bot_guilds:
                await self.tree.sync(guild=guild)

# Set the intents
intents = discord.Intents.all()
intents.bans = False
intents.integrations = False
intents.webhooks = False
intents.invites = False
intents.voice_states = False
intents.message_content = False

bot = LineBot(command_prefix=[], help_command=None, intents=intents)

@bot.tree.context_menu(name='Tic Tac Toe', guilds=core.bot_guilds) # type: ignore
@app_commands.checks.cooldown(1, 15)
async def tictactoe_context(interaction: discord.Interaction, user: discord.Member) -> None:
    if not user.bot:
        ask_view = core.Confirm(interaction, user)
        if user == interaction.user:
            ask_string = '¿Estás tratando de jugar contra ti mismo?'
        else:
            ask_string = f'{user.mention} ¿Quieres unirte a la partida de Tic Tac Toe de **{interaction.user.name}**?'
        await interaction.response.send_message(ask_string, view=ask_view)
        await ask_view.wait()
        
        if ask_view.value is None:
            await interaction.edit_original_response(view=ask_view)
            return
            
        if not ask_view.value:
            await ask_view.last_interaction.response.edit_message(content=core.Warning.cancel('La partida fue rechazada'), view=ask_view)
            return

        await ask_view.last_interaction.response.defer()

    game = ttt.TicTacToe(interaction, interaction.user, user)
    if interaction.response.is_done():
        await interaction.edit_original_response(content=game.get_content(), view=game)
    else:
        await interaction.response.send_message(content=game.get_content(), view=game)

async def main() -> None:
    # Create the event that catches any unknown errors and logs them
    @bot.event
    async def on_error(event: str, *args, **kwargs) -> None:
        log = f'An error has ocurred. Event: "{event}"\nargs: {args}\nkwargs: {kwargs}'
        core.logger.error(f'{log}\n{format_exc()}')

        if core.error_logging_channel:
            error_channel = bot.get_channel(core.error_logging_channel)
            invalid_channels = (
                discord.ForumChannel,
                discord.CategoryChannel,
                discord.abc.PrivateChannel
            )

            if (error_channel is None
                or isinstance(error_channel, invalid_channels)):
                core.logger.error(f'error_logging_channel is not a valid channel')
                return

            if bot.application:
                await error_channel.send(bot.application.owner.mention, delete_after=30)


    # Start the bot
    async with bot:
        with open(core.CONF_DIR, 'rb') as f:
            token = (
                tomllib.load(f)
                    .get('token', {})
                    .get(core.bot_mode, None)
            )

        if not token:
            print('No token for the selected mode was found in bot_conf.toml')
            exit(1)

        await bot.start(token)


if __name__ == '__main__':
    asyncio.run(main())
