import logging
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands
from pathlib import Path

import exceptions
from db import check_blacklist


# stable / dev
bot_mode = 'dev'
bot_version = '2.0'
bot_ready_at = datetime.utcnow()
bot_guilds = [
	discord.Object(id=724380436775567440),
	discord.Object(id=716165191238287361)
]
owner_id = 337029735144226825

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logging_file = f'{Path().resolve().parent}\\logs\\{datetime.today().date()}_{bot_mode}.log'
handler = logging.FileHandler(filename=logging_file, encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

default_prefix = {'stable':'l!', 'dev':'ld!'}[bot_mode]
prefix_table = {'stable':"PREFIXES", 'dev':"DEVPREFIXES"}[bot_mode]

error_logging_channel = 725390426780991531

check_emoji = '<:check:873788609398968370>'
cross_emoji = '<:x_:873229915170947132>'
circle_emoji = '<:o_:873229913518383126>'
empty_emoji = '<:empty:873754002427359252>'

first_emoji = '<:first_button:1023679433019764857>'
back_emoji = '<:back_button:1023673076023578766>'
next_emoji = '<:next_button:1023675221489750036>'
last_emoji = '<:last_button:1023677003733422130>'
search_emoji = '<:search_button:1023680974879465503>'

eval_returned_value = None

colors = {
	'random':discord.Colour.default(),
	'teal':discord.Colour.teal(),
	'dark teal':discord.Colour.dark_teal(),
	'green':discord.Colour.green(),
	'dark green':discord.Colour.dark_green(),
	'blue':discord.Colour.blue(),
	'dark blue':discord.Colour.dark_blue(),
	'purple':discord.Colour.purple(),
	'dark purple':discord.Colour.dark_purple(),
	'magenta':discord.Colour.magenta(),
	'dark magenta':discord.Colour.dark_magenta(),
	'gold':discord.Colour.gold(),
	'dark gold':discord.Colour.dark_gold(),
	'orange':discord.Colour.orange(),
	'dark orange':discord.Colour.dark_orange(),
	'red':discord.Colour.red(),
	'dark red':discord.Colour.dark_red(),
	'lighter grey':discord.Colour.lighter_grey(),
	'light grey':discord.Colour.light_grey(),
	'dark grey':discord.Colour.dark_grey(),
	'darker grey':discord.Colour.darker_grey(),
	'blurple':discord.Colour.blurple(),
	'greyple':discord.Colour.greyple()
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
	'greyple': 'Greyple'
}

bucket_types = {
	commands.BucketType.default: 'global',
	commands.BucketType.user: 'usuario',
	commands.BucketType.guild: 'servidor',
	commands.BucketType.channel: 'canal',
	commands.BucketType.member: 'miembro',
	commands.BucketType.category: 'categoría',
	commands.BucketType.role: 'rol'
}

bools = {True: 'Sí', False: 'No'}

links = {
	'Invítame a un servidor': 'https://discord.com/oauth2/authorize?client_id=582009564724199434&scope=bot&permissions=-9',
	'Mi página de top.gg': 'https://top.gg/bot/582009564724199434',
	'Vota por mí': 'https://top.gg/bot/582009564724199434/vote'
}


async def sync_tree(bot: commands.Bot) -> None:
	logger.info('Syncing command tree...')
	for guild in bot_guilds:
		await bot.tree.sync(guild=guild)
	logger.info('Command tree synced')


def owner_only():
	def predicate(interaction: discord.Interaction) -> bool:
		if interaction.user.id == owner_id:
			return True
		else:
			raise exceptions.NotOwner()
	return app_commands.check(predicate)


def config_commands(bot: commands.Bot) -> None:
	for command in bot.tree.get_commands(guild=bot_guilds[0]):
		if isinstance(command, app_commands.Group):
			for subcommand in command.commands:
				subcommand.add_check(check_blacklist)
		else:
			command.add_check(check_blacklist)


def fix_delta(delta: timedelta, *, ms=False, limit=3, compact=True) -> str:
	years = delta.days // 365
	days = delta.days - years * 365
	hours = delta.seconds // 3600
	minutes = (delta.seconds - hours * 3600) // 60
	seconds = (delta.seconds - minutes * 60 - hours * 3600)
	seconds += float(str(delta.microseconds / 1000000)[:3]) if ms and seconds < 10 else 0
	measures = {
		'años': years,
		'días': days,
		'horas': hours,
		'minutos': minutes,
		'segundos': seconds
	}
	for key in tuple(filter(lambda x: measures[x] == 0, measures)):
		measures.pop(key)
	for key in tuple(filter(lambda x: tuple(measures).index(x)+1 > limit, measures)):
		measures.pop(key)

	if compact:
		return ' '.join((f'{measures[measure]}{measure[0]}' for measure in measures))
	else:
		return ' '.join((f'{measures[measure]} {measure if measures[measure] != 1 else measure[:-1]}' for measure in measures))


def fix_date(date: datetime, *, elapsed=False, newline=False) -> str:
	result = f'{date.day}/{date.month}/{date.year} {date.hour}:{date.minute}:{date.second} UTC'
	if elapsed:
		delta = fix_delta(datetime.now(timezone.utc) - date)
		result += ('\n' if newline else ' ') + f'(Hace {delta})'
	return result


def add_fields(embed: discord.Embed, data_dict: dict, *, inline=None, inline_char='~') -> discord.Embed:
	inline_char = '' if inline_char is None else inline_char
	for data in data_dict:
		if data_dict[data] not in (None, ''):
			if inline is not None:
				embed.add_field(name=data, value=str(data_dict[data]), inline=inline)
			elif inline_char != '':
				embed.add_field(name=data.replace(inline_char, ''), value=str(data_dict[data]), inline=not data.endswith(inline_char))
			else:
				embed.add_field(name=data, value=str(data_dict[data]), inline=False)
	return embed


def embed_author(embed: discord.Embed, user: discord.User) -> discord.Embed:
	return embed.set_author(name=user.name, icon_url=user.avatar.url)



class Confirm(discord.ui.View):
	def __init__(
		self, interaction: discord.Interaction,
		user: discord.User,
		*,
		timeout: float = 180
	):
		super().__init__()
		self._interaction = interaction
		self.user = user
		self.timeout = timeout
		self.value: bool | None = None
		self.last_interaction: discord.Interaction | None = None

	async def interaction_check(self, interaction: discord.Interaction) -> bool:
		return interaction.user.id == self.user.id

	async def on_timeout(self) -> None:
		for child in self.children:
			child.disabled = True
		await self._interaction.edit_original_response(view=self)
		
	@discord.ui.button(label='Sí', emoji=check_emoji, style=discord.ButtonStyle.green)
	async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
		self.respond(interaction, True)

	@discord.ui.button(label='No', emoji=cross_emoji, style=discord.ButtonStyle.red)
	async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
		self.respond(interaction, False)

	def respond(self, interaction: discord.Interaction, value: bool) -> None:
		self.value = value
		self.last_interaction = interaction
		for child in self.children:
			child.disabled = True
		self.stop()


class Warning:
	@staticmethod
	def success(text: str, unicode=False) -> str:
		return Warning.emoji_warning((':white_check_mark:', u'\U00002705'), text, unicode)

	@staticmethod
	def cancel(text: str, unicode=False) -> str:
		return Warning.emoji_warning((':negative_squared_cross_mark:', u'\U0000274e'), text, unicode)

	@staticmethod
	def error(text: str, unicode=False) -> str:
		return Warning.emoji_warning((':warning:', u'\U000026a0'), text, unicode)

	@staticmethod
	def question(text: str, unicode=False) -> str:
		return Warning.emoji_warning((':grey_question:', u'\U00002754'), text, unicode)

	@staticmethod
	def info(text: str, unicode=False) -> str:
		return Warning.emoji_warning((':information_source:', u'\U00002139'), text, unicode)

	@staticmethod
	def loading(text: str, unicode=False) -> str:
		return Warning.emoji_warning((':arrows_counterclockwise:', u'\U0001f504'), text, unicode)

	@staticmethod
	def searching(text: str, unicode=False) -> str:
		return Warning.emoji_warning((':mag:', u'\U0001f50d'), text, unicode)

	@staticmethod
	def emoji_warning(emoji: tuple[str, str], text: str, unicode: bool) -> str:
		return f'{emoji[int(unicode)]} {text}'
