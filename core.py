import asyncio
from datetime import datetime, timedelta

import exceptions
from random import choice
from re import fullmatch
from sqlite3 import connect
from requests import head
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

import logging

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

conn = connect(f'{Path().resolve().parent}\\data.sqlite3')
cursor = conn.cursor()

eval_returned_value = None

cursor.execute("SELECT COMMAND FROM COMMANDSTATS")
commandstats_commands = [command[0] for command in cursor.fetchall()]
conn.commit

descs = {
	'ping': 'Muestra en milisegundos lo que tarda el bot en enviar un mensaje desde que mandaste el comando',
	'soy': 'Descubre quién eres',
	'say': 'Haz que el bot diga algo',
	'emojitext': 'Devuelve el texto transformado en emojis',
	'replace': 'Reemplaza el texto del primer parámetro por el segundo parametro en un tercer parámetro',
	'spacedtext': 'Devuelve el texto enviado con cada letra espaciada el número de veces indicado',
	'vaporwave': 'Devuelve el texto en vaporwave',
	'choose': 'Devuelve una de las opciones dadas, o "Si" o "No" si no le das opciones. Las opciones se separan por comas',
	'poll': 'Crea encuestas de manera sencilla. Los emojis se separan por espacios poniendo `-e` delante, si no se epecifican emojis e usaran :+1: y :-1:',
	'kao': 'Devuelve una lista de kaomojis o un kaomoji específico',
	'avatar': 'Obtiene tú foto de perfil o la de otro usuario',
	'defemoji': 'Envia emojis en el estado por defecto de tu dispositivo: \\😂. Si el emoji es personalizado de un server, se enviará su ID',
	'sarcastic': 'ConVIeRtE el TEXtO a SarcAStiCO',
	'iq': 'Calcula tu IQ o el de otra persona',
	'tag': 'Añade o usa tags tuyos o de otras personas',
	'links': 'Obtén los links oficiales del bot',
	'someone': 'Menciona a alguien aleatorio del server',
	'ocr': 'Transcribe el texto de la última imagen enviada en el chat]',
	'joke': 'Envia un chiste que da menos risa que los de Siri',
	'nothing': 'Literalmente no hace nada',
	'gay': 'Detecta como de homosexual eres',
	'changelog': 'Revisa el registro de cambios de la última versión del bot o de una especificada',
	'color': 'Cambia el color de los embeds del bot',
	'wiktionary': 'Busca una palabra en inglés en el diccionario de Wiktionary',
	'dle': 'Busca una palabra en español en el Diccionario de la lengua española',
	'die': 'Apaga el bot',
	'getmsg': 'Obtiene los datos de un mensaje',
	'eval': 'Ejecuta código',
	'reload': 'Recarga un módulo',
	'unload': 'Descarga un módulo',
	'load': 'Carga un módulo',
	'binary': 'Codifica o decodifica código binario',
	'morse': 'Codifica o decodifica código morse',
	'hackban': 'Banea a un usuario sin necesidad de que esté en el server',
	'userinfo': 'Obtiene información de un usuario. Habrá más información si este usuario se encuentra en este servidor',
	'roleinfo': 'Obtiene información de un rol',
	'channelinfo': 'Obtiene la información de un canal de cualquier tipo o una categoría',
	'serverinfo': 'Obtiene la información de este servidor',
	'blacklist': 'Mete o saca a un usuario de la blacklist',
	'uppercase': 'Convierte un texto a mayúsculas',
	'lowercase': 'Convierte un texto a minúsculas',
	'swapcase': 'Intercambia las minúsculas y las mayúsculas de un texto',
	'capitalize': 'Convierte la primera letra de cada palabra a mayúsculas',
	'count': 'Cuenta cuantas veces hay una letra o palabra dentro de otro texto. Recuerda que puedes usar comillas para usar espacios en el primer texto. Puedes pasar comillas vacías ("") para contar caracteres y palabras en general en un texto',
	'stats': 'Muestra información sobre el bot',
	'tictactoe': 'Juega una partida de Tic Tac Toe contra la maquina o contra un amigo',
	'reverse': 'Revierte un texto',
	'randomnumber': 'Obtiene un número aleatorio entre el intervalo especificado. Puedes usar número negativos',
	'8ball': 'Preguntale algo el bot para que te responda',
	'didyoumean': 'Escribe un texto que te corrija Google a otro. Separa los 2 textos por punto y coma entre espacios: ` ; `',
	'drake': 'Haz un meme con la plantilla de drake. Separa los 2 textos por punto y coma entre espacios: ` ; `',
	'bad': 'Ta mal',
	'amiajoke': 'Am I a joke to you?',
	'jokeoverhead': 'El que no entendía la broma',
	'salty': 'El ardido',
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
	'mcskin': 'Busca una skin de Minecraft según el nombre del usuario que pases',
	'percentencoding': 'Codifica o decodifica código porcentaje o código URL'
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


async def changelog_autocomplete(interaction: discord.Interaction, current: str):
	sql = {'stable':"SELECT VERSION FROM CHANGELOG WHERE HIDDEN=0", 'dev':"SELECT VERSION FROM CHANGELOG"}[bot_mode]
	cursor.execute(sql)
	db_version_data = cursor.fetchall()
	conn.commit()
	db_version_data.reverse()
	versions = [version[0] for version in db_version_data]
	versions = list(filter(lambda x: x.startswith(current), versions))
	if len(versions) > 25:
		versions = db_version_data[0: 24]
	versions = [app_commands.Choice(name=version, value=version) for version in versions]
	versions.append(app_commands.Choice(name='Ver todo', value='list'))
	return versions


async def color_autocomplete(interaction: discord.Interaction, current: str):
	color_options = list(filter(lambda x: x.startswith(current), list(colors_display)))
	color_options = [app_commands.Choice(name=colors_display[color], value=color) for color in colors]
	color_options.append(app_commands.Choice(name='Color por defecto', value='default'))
	return color_options


async def commandstats_command_autocomplete(interaction:discord.Interaction, current:str):
	commands = sorted(list(filter(lambda x: x.startswith(current), commandstats_commands)))[:7]
	commands = [app_commands.Choice(name=command, value=command) for command in commands]
	return commands


def default_color(interaction):
	# Check the color of the user in the database
	cursor.execute(f"SELECT VALUE FROM COLORS WHERE ID={interaction.user.id}")
	color = cursor.fetchall()
	if interaction.guild == None and color == []:
		return discord.Colour.blue()
	elif color == []:
		try:
			return interaction.guild.me.color
		except AttributeError:
			return discord.Color.blue()
	else:
		# If the color value is 0, return a random color
		if color[0][0] == 0:
			return colors[choice(tuple(colors)[1:])].value
		return int(color[0][0])


# async def askyn(ctx, message:str, timeout=12.0, user=None):
# 	class View(discord.ui.View):
# 		result = None
# 		def check(self, button, interaction):
# 			if interaction.user == ctx.author:
# 				result = button.custom_id == 'yes'

# 		@discord.ui.button(custom_id='yes', style=discord.ButtonStyle.green, emoji=check_emoji)
# 		async def yes_callback(self, button, interaction):
# 			return self.check(button, interaction)

# 		@discord.ui.button(custom_id='no', style=discord.ButtonStyle.red, emoji=cross_emoji)
# 		async def no_callback(self, button, interaction):
# 			return self.check(button, interaction)

# 		async def on_timeout(self):
# 			for child in self.children:
# 				child.disabled = True
# 			await question.edit(view=view)
# 			return None

# 	user = ctx.author if user == None else user
# 	await ctx.bot.get_cog('GlobalCog').send(ctx, Warning.question(message), view=View())
	# //////////
	# def check(interaction, button):
	# 	return interaction.message.id == question.id and interaction.author.id == user.id
	# try:
	# 	interaction, button = await ctx.bot.wait_for('button_click', timeout=timeout, check=check)
	# except asyncio.TimeoutError:
		# for i in range(len(view[0])):
		# 	view[0][i].disabled = True
		# await question.edit(view=view)
		# return None
	# await interaction.defer()
	# return button.custom_id == 'yes'


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


def check_blacklist(interaction, user=None, raises=True):
	user = interaction.user if user == None else user
	cursor.execute(f"SELECT USER FROM BLACKLIST WHERE USER={user.id}")
	check = cursor.fetchall()
	conn.commit()
	if check == []:
		return True
	if raises:
		raise exceptions.BlacklistUserError('This user is in the blacklist')
	else:
		return False


def config_commands(bot):
	for command in bot.tree.get_commands(guild=bot_guilds[0]):
		if command.name in descs:
			command.description = descs[command.name]
			command.add_check(check_blacklist)


def fix_delta(delta:timedelta, *, ms=False, limit=3):
	years = delta.days // 365
	days = delta.days - years * 365
	hours = delta.seconds // 3600
	minutes = (delta.seconds - hours * 3600) // 60
	seconds = (delta.seconds - minutes * 60 - hours * 3600)
	seconds += float(str(delta.microseconds / 1000000)[:3]) if ms and seconds < 10 else 0
	measures = {
		'y': years,
		'd': days,
		'h': hours,
		'm': minutes,
		's': seconds
	}
	for key in tuple(filter(lambda x: measures[x] == 0, measures)):
		measures.pop(key)
	for key in tuple(filter(lambda x: tuple(measures).index(x)+1 > limit, measures)):
		measures.pop(key)
	return ' '.join((f'{measures[measure]}{measure}' for measure in measures))


def fix_date(date:datetime, elapsed=False, newline=False):
	result = f'{date.day}/{date.month}/{date.year} {date.hour}:{date.minute}:{date.second} UTC'
	if elapsed:
		delta = fix_delta(datetime.utcnow() - date)
		result += ('\n' if newline else ' ') + f'(Hace {delta})'
	return result


def add_fields(embed:discord.Embed, data_dict:dict, *, inline=None, inline_char='~'):
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



class Page:
	__slots__ = ('content', 'embed')

	def __init__(self, content: str=None, *, embed: discord.Embed=None):
		self.content = content
		self.embed = embed

	@staticmethod
	def from_list(interaction, title:str, iterable: list, *, colour=None):
		formated = []
		count = 0
		if colour == None:
			colour = default_color(interaction)
		for i in iterable:
			count += 1
			formated.append(f'{count}. {i}')

		pages = []
		for i in range(int((len(formated) - 1)//20 + 1)):
			pages.append(Page(embed=discord.Embed(
				title=title,
				description='\n'.join(formated[i*20:i*20+20]),
				colour=colour
			)))
		return pages



class Paginator(discord.ui.View):
	def __init__(self, interaction:discord.Interaction, *, pages:list=[], entries:int=None, timeout:float=180.0):
		super().__init__(timeout=timeout)
		self.interaction = interaction
		self.page_num = 1
		self.page = None
		self.pages = []
		self.entries = entries
		self.add_pages(pages)


	def add_pages(self, pages:list):
		count = 0
		for page in pages:
			count += 1
			if page.embed != None:
				page.embed.set_footer(text=(f'Página {len(self.pages)+count} de {len(pages) + len(self.pages)}' if len(self.pages)+len(pages) > 1 else '') + f'{(str(" ("+str(self.entries)+" resultados)")) if self.entries != None else ""}' + (f' | {page.embed.footer.text}' if page.embed.footer.text != None else ""))
		self.pages += pages


	async def interaction_check(self, interaction: discord.Interaction):
		return self.interaction.user.id == interaction.user.id


	@discord.ui.button(emoji=first_emoji, style=discord.ButtonStyle.blurple, disabled=True)
	async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.set_page(interaction, button, 1)

	@discord.ui.button(emoji=back_emoji, style=discord.ButtonStyle.blurple, disabled=True)
	async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.set_page(interaction, button, self.page_num - 1)

	@discord.ui.button(emoji=next_emoji, style=discord.ButtonStyle.blurple)
	async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.set_page(interaction, button, self.page_num + 1)

	@discord.ui.button(emoji=last_emoji, style=discord.ButtonStyle.blurple)
	async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.set_page(interaction, button, len(self.pages))

	@discord.ui.button(emoji=search_emoji, style=discord.ButtonStyle.blurple)
	async def search(self, interaction: discord.Interaction, button: discord.ui.Button):
		total_pages = len(self.pages)

		class SearchModal(discord.ui.Modal, title='Escribe un número de página'):
			answer = discord.ui.TextInput(
				label=f'Escribe un número de página (1-{total_pages})',
				required=True,
				min_length=1,
				max_length=len(str(total_pages))
			)

		async def on_submit(modal):
			async def func(interaction: discord.Interaction):
				try:
					value = int(modal.answer.value)
					if 0 < value <= total_pages:
						await self.set_page(interaction, button, value)
					else:
						await interaction.response.send_message(Warning.error(f'Escribe un número entre el 1 y el {total_pages}'), ephemeral=True)
				except ValueError:
					await interaction.response.send_message(Warning.error('Valor incorrecto. Escribe un número'), ephemeral=True)
			return func

		modal = SearchModal()
		modal.timeout = self.timeout
		modal.on_submit = await on_submit(modal)
		await interaction.response.send_modal(modal)

	
	async def on_timeout(self):
		self.children[0].disabled = True
		self.children[1].disabled = True
		self.children[2].disabled = True
		self.children[3].disabled = True
		self.children[4].disabled = True
		await self.interaction.edit_original_response(view=self)


	async def set_page(self, interaction:discord.Interaction, button:discord.ui.Button, page:int, interact=True):
		self.page = self.pages[page-1]
		self.page_num = page
		self.children[0].disabled = self.page_num == 1
		self.children[1].disabled = self.page_num == 1
		self.children[2].disabled = self.page_num == len(self.pages)
		self.children[3].disabled = self.page_num == len(self.pages)
		await interaction.response.defer()
		await self.interaction.edit_original_response(content=self.page.content, embed=self.page.embed, view=self)



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
	def emoji_warning(emoji, text, unicode):
		return f'{emoji[int(unicode)]} {text}.'



class Tag:
	__slots__ = ('ctx', 'guild', 'user', 'name', 'content', 'img', 'nsfw')

	def __init__(self, ctx, guild_id:int, user_id:int, name:str, content:str, img:bool, nsfw:bool):
		self.ctx = ctx
		self.guild = ctx.bot.get_guild(guild_id)
		self.user = ctx.bot.get_user(user_id)
		self.name = name
		self.content = content
		self.img = img
		self.nsfw = nsfw

	def __str__(self):
		return self.name

	def gift(self, user:discord.Member):
		cursor.execute(f"UPDATE TAGS2 SET USER={user.id} WHERE GUILD={self.guild.id} AND NAME=?", (self.name,))
		conn.commit()
		self.user = user

	def rename(self, name:str):
		cursor.execute(f"UPDATE TAGS2 SET NAME=? WHERE GUILD={self.guild.id} AND NAME=?", (name, self.name))
		conn.commit()
		self.name = name

	def edit(self, content:str, img:bool, nsfw:bool):
		self.content = content
		self.img = img
		self.nsfw = nsfw
		cursor.execute(f"UPDATE TAGS2 SET CONTENT=?, IMG={int(self.img)}, NSFW={int(self.nsfw)} WHERE GUILD={self.guild.id} AND NAME=?", (self.content, self.name))
		conn.commit()

	def delete(self):
		cursor.execute(f"DELETE FROM TAGS2 WHERE GUILD={self.guild.id} AND NAME=?", (self.name,))
		conn.commit()
