import asyncio
import logging
from datetime import datetime, timedelta, timezone
from random import choice
from typing import Union

import discord
from discord import app_commands
from discord.ext import commands
from requests import head
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


descs = {
	'ping': 'Muestra en milisegundos lo que tarda el bot en enviar un mensaje desde que mandaste el comando',
	'soy': 'Descubre quién eres',
	'say': 'Haz que el bot diga algo',
	'emojitext': 'Devuelve el texto transformado en emojis',
	'replace': 'Reemplaza el texto del primer parámetro por el segundo parametro en un tercer parámetro',
	'spacedtext': 'Devuelve el texto enviado con cada letra espaciada el número de veces indicado',
	'vaporwave': 'Devuelve el texto en vaporwave',
	'choose': 'Devuelve una de las opciones dadas',
	'poll': 'Crea encuestas de manera sencilla',
	'avatar': 'Obtiene tú foto de perfil o la de otro usuario',
	'sarcastic': 'ConVIeRtE el TEXtO a SarcAStiCO',
	'iq': 'Calcula tu IQ o el de otra persona',
	'tag': 'Añade o usa tags tuyos o de otros usuarios',
	'tag show': 'Muestra el contenido de un tag',
	'tag toggle': 'Activa los tags en el servidor',
	'tag add': 'Crea un tag',
	'tag gift': 'Regala un tag a otro usuario',
	'tag rename': 'Cambia el nombre de uno de tus tags',
	'tag edit': 'Edita el contenido de uno de tus tags',
	'tag delete': 'Elimina uno de tus tags',
	'tag forcedelete': 'Reservado',
	'tag owner': 'Muestra el propietario de un tag',
	'tag list': 'Muestra una lista de tus tags o de los tags de otro usuario',
	'tag serverlist': 'Muestra los tags de todo el servidor',
	'links': 'Obtén los links oficiales del bot',
	'someone': 'Menciona a alguien aleatorio del servidor',
	'dadjoke': 'Envia chistes que dan menos risa que los de Siri',
	'nothing': 'Literalmente no hace nada',
	'gay': 'Detecta como de homosexual eres',
	'changelog': 'Revisa el registro de cambios de la última versión del bot o de una especificada',
	'color': 'Cambia el color de los embeds del bot',
	'define': 'Busca el significado de una palabra en Wiktionary',
	'define spanish': 'Busca el significado de una palabra en español en Wiktionary',
	'define english': 'Busca el significado de una palabra en inglés en Wiktionary',
	'die': 'Apaga el bot',
	'getmsg': 'Obtiene los datos de un mensaje',
	'eval': 'Ejecuta código',
	'reload': 'Recarga un módulo',
	'unload': 'Descarga un módulo',
	'load': 'Carga un módulo',
	'binary': 'Codifica o decodifica código binario',
	'binary encode': 'Convierte texto a código binario',
	'binary decode': 'Convierte código binario a texto',
	'morse': 'Codifica o decodifica código morse',
	'morse encode': 'Convierte texto a código morse',
	'morse decode': 'Convierte código morse a texto',
	'percent-encoding': 'Codifica o decodifica código porcentaje o código URL',
	'percent-encoding encode': 'Convierte texto a código porcentaje o código URL',
	'percent-encoding decode': 'Convierte código porcentaje o código URL a texto',
	'hackban': 'Banea a un usuario sin necesidad de que esté en el server',
	'userinfo': 'Obtiene información de un usuario. Habrá más información si el usuario se encuentra en el servidor',
	'roleinfo': 'Obtiene información de un rol',
	'channelinfo': 'Obtiene la información de un canal de cualquier tipo o una categoría',
	'serverinfo': 'Obtiene la información de este servidor',
	'blacklist': 'Mete o saca a un usuario de la blacklist',
	'uppercase': 'Convierte un texto a mayúsculas',
	'lowercase': 'Convierte un texto a minúsculas',
	'swapcase': 'Intercambia las minúsculas y las mayúsculas de un texto',
	'capitalize': 'Convierte la primera letra de cada palabra a mayúsculas',
	'count': 'Cuenta cuantas veces hay una letra o palabra dentro de otro texto',
	'stats': 'Muestra información sobre el bot',
	'tictactoe': 'Juega una partida de Tic Tac Toe contra la máquina o contra otra persona',
	'tictactoe against-machine': 'Juega una partida de Tic Tac Toe contra la máquina',
	'tictactoe against-player': 'Juega una partida de Tic tac Toe contra otra persona',
	'reverse': 'Revierte un texto',
	'randomnumber': 'Obtiene un número aleatorio entre el intervalo especificado. Puedes usar número negativos',
	'8ball': 'Preguntale algo el bot para que te responda',
	'didyoumean': 'Google "quizás quisiste decir"',
	'drake': 'Haz un meme con la plantilla de drake',
	'birb': 'Random birb',
	'dog': 'Imagen random de un perro',
	'cat': 'Imagen random de un gato',
	'sadcat': 'Imagen random de un gato triste',
	'calling': 'Tom llamando hm',
	'captcha': 'Cursed captcha',
	'facts': 'facts',
	'supreme': 'Texto con fuente de Supreme',
	'commandstats': 'Muestra cuáles son los comandos más usados y cuántas veces se han',
	'r34': 'Busca en rule34.xxx. Deja vacío para buscar imagenes aleatorias',
	'mcskin': 'Busca una skin de Minecraft según el nombre del usuario que pases'
}

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


async def sync_tree(bot):
	logger.info('Syncing command tree...')
	for guild in bot_guilds:
		await bot.tree.sync(guild=guild)
	logger.info('Command tree synced')




# async def ask(ctx, message:str, *, timeout=12.0, user=None, regex=None, raises=False):
# 	user = ctx.author if user == None else user
# 	question = await ctx.send(Warning.question(message))
# 	def check(message):
# 		return message.author.id == user.id and (fullmatch(regex, message.content) if regex != None else True) and message.channel.id == ctx.channel.id
# 	try:
# 		message = await ctx.bot.wait_for('message', timeout=timeout, check=check)
# 	except asyncio.TimeoutError:
# 		if raises:
# 			await question.delete()
# 			raise asyncio.TimeoutError
# 		else:
# 			await ctx.bot.get_cog('GlobalCog').send(ctx, Warning.error(f'{user.mention} No respondiste a tiempo'))
# 			return None
# 	await ctx.channel.delete_messages((question, message))
# 	return message.content


async def get_channel_image(ctx):
	async for msg in ctx.history(limit=30):
		if msg.attachments != []:
			return msg.attachments[0].url
		elif msg.embeds != []:
			embed = msg.embeds[0]
			for check in [embed.image.url, embed.thumbnail.url]:
				if check != discord.Embed.Empty:
					return check
	raise exceptions.ImageNotFound('Image not detected in the channel')


def is_url_image(image_url):
	image_formats = ("image/png", "image/jpeg", "image/jpg")
	r = head(image_url)
	if r.headers["content-type"] in image_formats:
		return True
	return False


async def get_user(ctx, arg:str):
	try:
		return await commands.UserConverter().convert(ctx, arg)
	except:
		try:
			return await ctx.bot.fetch_user(int(arg))
		except:
			return await commands.UserConverter().convert(ctx, '0')


def owner_only():
	def predicate(interaction):
		if interaction.user.id == owner_id:
			return True
		else:
			raise exceptions.NotOwner()
	return app_commands.check(predicate)


def config_commands(bot):
	for command in bot.tree.get_commands(guild=bot_guilds[0]):
		if command.qualified_name in descs:
			command.description = descs[command.qualified_name]
			if isinstance(command, app_commands.Group):
				for subcommand in command.commands:
					subcommand.description = descs[subcommand.qualified_name]
					subcommand.add_check(check_blacklist)
			else:
				command.add_check(check_blacklist)


def fix_delta(delta: timedelta, *, ms=False, limit=3, compact=True):
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


def fix_date(date: datetime, *, elapsed=False, newline=False):
	result = f'{date.day}/{date.month}/{date.year} {date.hour}:{date.minute}:{date.second} UTC'
	if elapsed:
		delta = fix_delta(datetime.now(timezone.utc) - date)
		result += ('\n' if newline else ' ') + f'(Hace {delta})'
	return result


def add_fields(embed: discord.Embed, data_dict: dict, *, inline=None, inline_char='~'):
	inline_char = '' if inline_char == None else inline_char
	for data in data_dict:
		if data_dict[data] not in (None, ''):
			if inline != None:
				embed.add_field(name=data, value=str(data_dict[data]), inline=inline)
			elif inline_char != '':
				embed.add_field(name=data.replace(inline_char, ''), value=str(data_dict[data]), inline=not data.endswith(inline_char))
			else:
				embed.add_field(name=data, value=str(data_dict[data]), inline=False)
	return embed


def embed_author(embed:discord.Embed, user:discord.User):
	return embed.set_author(name=user.name, icon_url=user.avatar.url)



class ChannelConverter(commands.Converter):
	async def convert(self, ctx, argument):
		try:
			argument = await commands.TextChannelConverter().convert(ctx, argument)
		except:
			try:
				argument = await commands.VoiceChannelConverter().convert(ctx, argument)
			except:
				try:
					argument = await commands.CategoryChannelConverter().convert(ctx, argument)
				except:
					raise commands.BadArgument(f'Channel "{argument}" not found')

		return argument


class Confirm(discord.ui.View):
	def __init__(self, interaction:discord.Interaction, user: discord.User, *, timeout:Union[int, float]=180):
		super().__init__()
		self._interaction = interaction
		self.user = user
		self.timeout = timeout
		self.value = None
		self.last_interaction = None

	async def interaction_check(self, interaction: discord.Interaction):
		return interaction.user.id == self.user.id

	async def on_timeout(self):
		for child in self.children:
			child.disabled = True
		await self._interaction.edit_original_response(view=self)
		
	@discord.ui.button(label='Sí', emoji=check_emoji, style=discord.ButtonStyle.green)
	async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.respond(interaction, True)

	@discord.ui.button(label='No', emoji=cross_emoji, style=discord.ButtonStyle.red)
	async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.respond(interaction, False)

	def respond(self, interaction: discord.Interaction, value: bool):
		self.value = value
		self.last_interaction = interaction
		for child in self.children:
			child.disabled = True
		self.stop()


class Warning:
	@staticmethod
	def success(text:str, unicode=False):
		return Warning.emoji_warning((':white_check_mark:', u'\U00002705'), text, unicode)

	@staticmethod
	def cancel(text:str, unicode=False):
		return Warning.emoji_warning((':negative_squared_cross_mark:', u'\U0000274e'), text, unicode)

	@staticmethod
	def error(text:str, unicode=False):
		return Warning.emoji_warning((':warning:', u'\U000026a0'), text, unicode)

	@staticmethod
	def question(text:str, unicode=False):
		return Warning.emoji_warning((':grey_question:', u'\U00002754'), text, unicode)

	@staticmethod
	def info(text:str, unicode=False):
		return Warning.emoji_warning((':information_source:', u'\U00002139'), text, unicode)

	@staticmethod
	def loading(text:str, unicode=False):
		return Warning.emoji_warning((':arrows_counterclockwise:', u'\U0001f504'), text, unicode)

	@staticmethod
	def searching(text:str, unicode=False):
		return Warning.emoji_warning((':mag:', u'\U0001f50d'), text, unicode)

	@staticmethod
	def emoji_warning(emoji, text, unicode):
		return f'{emoji[int(unicode)]} {text}'


