import logging
import os
import tomllib
from collections.abc import Callable, Generator
from datetime import datetime, timedelta, timezone
from typing import Any, TypedDict

import discord
from discord import app_commands
from discord.ext import commands

import db
import exceptions

# If the current working directory is ./src/
# change it to its parent, the git root directory
os.chdir(os.getcwd().removesuffix('src'))

Missing = discord.utils._MissingSentinel

CONF_DIR = './bot_conf.toml'

if not os.path.isfile(CONF_DIR):
    print("The configuration file wasn't found. Create one by running setup.py")
    exit(1)


class ConfToken(TypedDict):
    stable: str
    dev: str


class ConfPresence(TypedDict):
    status: int
    activity: int
    name: str


class ConfLinks(TypedDict):
    topgg: str
    bot_invite: str
    guild_invite: str
    vote: str


class ConfEmoji(TypedDict):
    check: str
    cross: str
    circle: str
    empty: str
    first: str
    back: str
    next: str
    last: str
    search: str


class BotConf(TypedDict):
    dev_mode: bool
    guilds: list[int]
    error_channel_id: int
    presence: ConfPresence
    links: ConfLinks
    emoji: ConfEmoji


class BotConfPlus(BotConf):
    token: ConfToken


with open(CONF_DIR, 'rb') as f:
    conf: BotConf = tomllib.load(f)  # type: ignore

# For security reasons, tokens are not accesible from core.conf
# and have to be loaded independently
if 'token' in conf:
    del conf['token']

# stable / dev
bot_mode = 'dev' if conf['dev_mode'] else 'stable'
bot_version = '2.0.1'
bot_ready_at = datetime.now(timezone.utc)
bot_guilds: list[discord.Object] | Missing
if conf['dev_mode']:
    bot_guilds = [discord.Object(id=guild_id) for guild_id in conf['guilds']]
else:
    bot_guilds = discord.utils.MISSING

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
LOG_DIR = './logs/'
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
logging_file = f'{LOG_DIR}{datetime.today().date()}_{bot_mode}.log'
handler = logging.FileHandler(filename=logging_file, encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

error_logging_channel = conf['error_channel_id']

check_emoji = conf['emoji']['check']
cross_emoji = conf['emoji']['cross']
circle_emoji = conf['emoji']['circle']
empty_emoji = conf['emoji']['empty']

first_emoji = conf['emoji']['first']
back_emoji = conf['emoji']['back']
next_emoji = conf['emoji']['next']
last_emoji = conf['emoji']['last']
search_emoji = conf['emoji']['search']

eval_returned_value: Any = None

hidden = 'WHERE hidden=0 ' if bot_mode == 'stable' else ''
sql = 'SELECT version FROM changelog {}ORDER BY version DESC'.format(hidden)
db.cursor.execute(sql)
db_version_data: list[tuple[str]] = db.cursor.fetchall()
cached_versions = [version[0] for version in db_version_data]

colors = {
    'random': discord.Colour.default(),
    'teal': discord.Colour.teal(),
    'dark teal': discord.Colour.dark_teal(),
    'green': discord.Colour.green(),
    'dark green': discord.Colour.dark_green(),
    'blue': discord.Colour.blue(),
    'dark blue': discord.Colour.dark_blue(),
    'purple': discord.Colour.purple(),
    'dark purple': discord.Colour.dark_purple(),
    'magenta': discord.Colour.magenta(),
    'dark magenta': discord.Colour.dark_magenta(),
    'gold': discord.Colour.gold(),
    'dark gold': discord.Colour.dark_gold(),
    'orange': discord.Colour.orange(),
    'dark orange': discord.Colour.dark_orange(),
    'red': discord.Colour.red(),
    'dark red': discord.Colour.dark_red(),
    'lighter grey': discord.Colour.lighter_grey(),
    'light grey': discord.Colour.light_grey(),
    'dark grey': discord.Colour.dark_grey(),
    'darker grey': discord.Colour.darker_grey(),
    'blurple': discord.Colour.blurple(),
    'greyple': discord.Colour.greyple(),
}

colors_display = {
    'random': 'Aleatorio',
    'teal': 'Verde azulado',
    'dark teal': 'Verde azulado oscuro',
    'green': 'Verde',
    'dark green': 'Verde oscuro',
    'blue': 'Azul',
    'dark blue': 'Azul oscuro',
    'purple': 'Morado',
    'dark purple': 'Morado oscuro',
    'magenta': 'Magenta',
    'dark magenta': 'Magenta oscuro',
    'gold': 'Dorado',
    'dark gold': 'Dorado oscuro',
    'orange': 'Naranja',
    'dark orange': 'Naranja oscuro',
    'red': 'Rojo',
    'dark red': 'Rojo oscuro',
    'lighter grey': 'Gris más claro',
    'light grey': 'Gris claro',
    'dark grey': 'Gris oscuro',
    'darker grey': 'Gris más oscuro',
    'blurple': 'Blurple',
    'greyple': 'Greyple',
}

bucket_types = {
    commands.BucketType.default: 'global',
    commands.BucketType.user: 'usuario',
    commands.BucketType.guild: 'servidor',
    commands.BucketType.channel: 'canal',
    commands.BucketType.member: 'miembro',
    commands.BucketType.category: 'categoría',
    commands.BucketType.role: 'rol',
}

bools = {True: 'Sí', False: 'No'}

links = {
    'Invítame a un servidor': conf['links']['bot_invite'],
    'Mi servidor': conf['links']['guild_invite'],
    'Mi página de top.gg': conf['links']['topgg'],
    'Vota por mí': conf['links']['vote'],
}
assert len(links) <= 5  # Button rows can't go past 5 buttons


async def sync_tree(bot: commands.Bot) -> None:
    """Sync the command tree globally or per guild according to bot_mode."""
    logger.info('Syncing command tree...')
    if isinstance(bot_guilds, Missing):
        await bot.tree.sync()
    else:
        for guild in bot_guilds:
            await bot.tree.sync(guild=guild)
    logger.info('Command tree synced')


def get_bot_guild(interaction: discord.Interaction) -> discord.Guild | None:
    """Return None in stable mode and interaction.guild in dev mode."""
    if not conf['dev_mode']:
        return None

    return interaction.guild


def owner_only():
    """Raise NotOwnerError if interaction.user is not the owner."""

    def predicate(interaction: discord.Interaction) -> bool:
        app = interaction.client.application
        if app is None or interaction.user != app.owner:
            raise exceptions.NotOwnerError
        return True

    return app_commands.check(predicate)


def for_each_app_command(
    func: Callable[[app_commands.Command | app_commands.ContextMenu], None],
    command: app_commands.Command | app_commands.Group | app_commands.ContextMenu,
    *,
    ignore_ctx_menu=False,
) -> None:
    """Call func recursively for each app command in the command tree."""
    # We do a little DFS
    if isinstance(command, app_commands.Group):
        for subcommand in command.commands:
            for_each_app_command(func, subcommand)
        return

    if ignore_ctx_menu and isinstance(command, app_commands.ContextMenu):
        return

    func(command)


def config_commands(bot: commands.Bot) -> None:
    """Add blacklist check to every command."""
    if isinstance(bot_guilds, Missing):
        guild = None
    else:
        if not bot_guilds:
            return
        guild = bot_guilds[0]

    for command in bot.tree.get_commands(guild=guild):
        for_each_app_command(lambda cmd: cmd.add_check(db.check_blacklist), command)


async def fetch_app_command(
    interaction: discord.Interaction[commands.Bot],
    command: str,
) -> app_commands.AppCommand | app_commands.AppCommandGroup:
    """Return an app command from Discord's API."""
    names = command.split(' ')
    commands = await interaction.client.tree.fetch_commands(guild=get_bot_guild(interaction))

    subcmd = None
    curr_cmds = commands
    for name in names:
        for subcmd in curr_cmds:
            if isinstance(subcmd, app_commands.Argument):
                raise KeyError(f'Parent command of "{subcmd.name}" is not a command group')
            if subcmd.name == name:
                curr_cmds = subcmd.options
                break
        else:
            subcmd = None

    if subcmd is None:
        raise KeyError(f'Command "{command}" not found')
    return subcmd


def fix_delta(
    delta: timedelta,
    *,
    ms=False,
    limit: int | None = 3,
    compact=True,
) -> str:
    """Return a pretty version of a timedelta."""
    years = delta.days // 365
    days = delta.days - years * 365
    hours = delta.seconds // 3600
    minutes = (delta.seconds - hours * 3600) // 60
    seconds = delta.seconds - minutes * 60 - hours * 3600
    seconds += float(str(delta.microseconds / 1e6)[:3]) if ms and seconds < 10 else 0

    timings: list[float] = [years, days, hours, minutes, seconds]
    units = ['año', 'día', 'hora', 'minuto', 'segundo']

    if compact:
        # Only show the first letter
        units = [u[0] for u in units]
    else:
        # Add spaces to words and make them plural if needed
        units = [f' {u}s' if t != 1 else f' {u}'
                 for t, u in zip(timings, units)]

    # Ignore timings equal to 0 or past the limit
    measures: list[str] = []
    for t, u in zip(timings, units):
        if t:
            measures.append(f'{t}{u}')
    measures = measures[:limit]

    return ' '.join(measures)


def fix_date(date: datetime, *, elapsed=False, newline=False) -> str:
    """Return a pretty version of a datetime"""
    result = f'{date.day}/{date.month}/{date.year} {date.hour}:{date.minute}:{date.second} UTC'
    if elapsed:
        delta = fix_delta(datetime.now(timezone.utc) - date)
        result += ('\n' if newline else ' ') + f'(Hace {delta})'
    return result


def add_fields(
    embed: discord.Embed,
    data_dict: dict,
    *,
    inline=None,
    inline_char='~',
) -> discord.Embed:
    """Add fields to an embed.

    This is a bad and useless function, don't use it.
    """
    inline_char = '' if inline_char is None else inline_char
    for data in data_dict:
        if data_dict[data] not in (None, ''):
            if inline is not None:
                embed.add_field(
                    name=data,
                    value=str(data_dict[data]),
                    inline=inline,
                )
            elif inline_char != '':
                embed.add_field(
                    name=data.replace(inline_char, ''),
                    value=str(data_dict[data]),
                    inline=not data.endswith(inline_char),
                )
            else:
                embed.add_field(
                    name=data,
                    value=str(data_dict[data]),
                    inline=False,
                )
    return embed


def embed_author(embed: discord.Embed, user: discord.abc.User) -> discord.Embed:
    """Set author to embed with user's name an icon."""
    return embed.set_author(name=user.name, icon_url=user.display_avatar.url)


def split_list[T](lst: list[T], n: int) -> Generator[list[T], None, None]:
    """Return a generator that splits the list in chunks of size n."""
    for i in range(0, len(lst), n):
        yield lst[i : i+n]


class Confirm(discord.ui.View):
    """View that contains Yes/No buttons.

    You can access the response value with View.value after the View
    stops waiting. View.value is None if the user didn't answer, True
    if answered yes, and False if answered no.
    """

    def __init__(
        self,
        interaction: discord.Interaction,
        user: discord.abc.User,
        *,
        timeout: float = 180,
    ):
        super().__init__()
        self._interaction = interaction
        self.user = user
        self.timeout = timeout
        self.value: bool | None = None
        self.children: list[discord.ui.Button]  # type: ignore [no-def]

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self._interaction.edit_original_response(view=self)

    @discord.ui.button(label='Sí', emoji=check_emoji, style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        self.respond(interaction, True)

    @discord.ui.button(label='No', emoji=cross_emoji, style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        self.respond(interaction, False)

    def respond(self, interaction: discord.Interaction, value: bool) -> None:
        self.value = value
        self.last_interaction = interaction
        for child in self.children:
            child.disabled = True
        self.stop()


class Warning:
    """A class with functions that add emoji to your messages."""

    @classmethod
    def success(cls, text: str, unicode=False) -> str:
        return cls.emoji_warning((':white_check_mark:', '\U00002705'), text, unicode)

    @classmethod
    def cancel(cls, text: str, unicode=False) -> str:
        return cls.emoji_warning((':negative_squared_cross_mark:', '\U0000274e'), text, unicode)

    @classmethod
    def error(cls, text: str, unicode=False) -> str:
        return cls.emoji_warning((':warning:', '\U000026a0'), text, unicode)

    @classmethod
    def question(cls, text: str, unicode=False) -> str:
        return cls.emoji_warning((':grey_question:', '\U00002754'), text, unicode)

    @classmethod
    def info(cls, text: str, unicode=False) -> str:
        return cls.emoji_warning((':information_source:', '\U00002139'), text, unicode)

    @classmethod
    def loading(cls, text: str, unicode=False) -> str:
        return cls.emoji_warning((':arrows_counterclockwise:', '\U0001f504'), text, unicode)

    @classmethod
    def searching(cls, text: str, unicode=False) -> str:
        return cls.emoji_warning((':mag:', '\U0001f50d'), text, unicode)

    @staticmethod
    def emoji_warning(emoji: tuple[str, str], text: str, unicode: bool) -> str:
        return f'{emoji[int(unicode)]} {text}'
