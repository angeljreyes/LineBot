import asyncio
import tomllib
import os
from traceback import format_exc

# If the current working directory is ./src/
# change it to its parent, the git root directory
os.chdir(os.getcwd().removesuffix('src'))

from icecream import install
install() # Set up icecream
import discord
from discord.ext import commands

if not os.path.isfile('./line.db'):
    print('The database wasn\'t found. Create a databse by running setup.py')
    exit(1)
import core


# Create the bot client
class LineBot(commands.Bot):
    async def setup_hook(self) -> None:
        # Load the extensions which contain commands and utilities
        for extension in (
            'listeners',
            'bot',
            'modtxt',
            'util',
            'tag',
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
intents.message_content = False

bot = LineBot(command_prefix=[], help_command=None, intents=intents)

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
            token: str | None = (
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
