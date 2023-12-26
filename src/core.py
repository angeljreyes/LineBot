import asyncio
from datetime import datetime, timedelta, timezone

import exceptions
from random import choice
from re import fullmatch
from sqlite3 import connect
from requests import head
from pathlib import Path
from typing import List, Union

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
	'define': 'Busca el significado de una palabra',
	'define spanish': 'Busca el significado de una palabra en español en el Diccionario de la Lengua Española',
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


async def tag_check(interaction: discord.Interaction):
	cursor.execute(f"SELECT GUILD FROM TAGSENABLED WHERE GUILD={interaction.guild.id}")
	check = cursor.fetchall()
	if check == []:
		await interaction.response.send_message(Warning.info(
			f'Los tags están desactivados en este servidor. {"Actívalos" if interaction.channel.permissions_for(interaction.user).manage_guild else "Pídele a un administrador que los active"} con el comando {list(filter(lambda x: x.name == "toggle", list(filter(lambda x: x.name == "tag", await interaction.client.tree.fetch_commands(guild=interaction.guild)))[0].options))[0].mention}'))
		raise exceptions.DisabledTagsError('Tags are not enabled on this guild')


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


class JoinView(discord.ui.View):
	def __init__(self, interaction: discord.Interaction):
		super().__init__()
		self.timeout = 180
		self.user = None
		self.interaction = None
		self._interaction = interaction

	async def on_timeout(self):
		self.children[0].disabled = True
		await self._interaction.edit_original_response(view=self)

	@discord.ui.button(label='Unirse', emoji=u'\U0001f4e5', style=discord.ButtonStyle.blurple)
	async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.user = interaction.user
		self.interaction = interaction
		button.disabled = True
		self.stop()


class TicTacToeButton(discord.ui.Button['TicTacToe']):
	def __init__(self, x: int, y: int):
		# A label is required, but we don't need one so a zero-width space is used
		# The row parameter tells the View which row to place the button under.
		# A View can only contain up to 5 rows -- each row can only have 5 buttons.
		# Since a Tic Tac Toe grid is 3x3 that means we have 3 rows and 3 columns.
		super().__init__(style=discord.ButtonStyle.grey, emoji=empty_emoji, row=y)
		self.x = x
		self.y = y

	async def interaction_check(self, interaction: discord.Interaction):
		if interaction.user.id == self.view.players[self.view.current_player].id:
			return True
		else:
			await interaction.response.defer()


	# This function is called whenever this particular button is pressed
	# This is part of the "meat" of the game logic
	async def callback(self, interaction: discord.Interaction):
		assert self.view is not None
		view: TicTacToe = self.view
		state = view.board[self.y][self.x]
		if state in (view.X, view.O):
			return

		await view.play(interaction, self.x, self.y)


# This is our actual board View
class TicTacToe(discord.ui.View):
	# This tells the IDE or linter that all our children will be TicTacToeButtons
	# This is not required
	children: List[TicTacToeButton]
	X = -1
	O = 1
	Tie = 2

	def __init__(self, interaction: discord.Interaction, playerX: discord.User, playerO: discord.User):
		super().__init__()
		self.interaction = interaction
		self.timeout = 90
		self.current_player = self.X
		self.playerX = playerX
		self.playerO = playerO
		self.players = {
			self.X: self.playerX,
			self.O: self.playerO
		}
		self.board = [
			[0, 0, 0],
			[0, 0, 0],
			[0, 0, 0],
		]
		# Our board is made up of 3 by 3 TicTacToeButtons
		# The TicTacToeButton maintains the callbacks and helps steer
		# the actual game.
		for x in range(3):
			for y in range(3):
				self.add_item(TicTacToeButton(x, y))

	def get_content(self, status=None):
		if status == None:
			status = f':timer: Turno de {self.players[self.current_player].mention}'
		return f'__**Tic Tac Toe**__\n:crossed_swords: **{self.playerX.name}** vs **{self.playerO.name}**\n{status}'

	def get_other_player(self, key=None):
		if key == None:
			key = self.current_player
		return {self.X: self.O, self.O: self.X}[self.current_player]

	async def on_timeout(self):
		for child in self.children:
			child.disabled = True
		self.stop()
		await self.interaction.edit_original_response(content=self.get_content(f':tada: **{self.players[self.current_player].name}** no realizo su jugada a tiempo. ¡**{self.players[self.get_other_player()].name}** ha ganado la partida!'), view=self)
	
	async def play(self, interaction, x, y):
		button = self.children[x*3 + y]
		button.style = {self.X: discord.ButtonStyle.blurple, self.O: discord.ButtonStyle.green}[self.current_player]
		button.emoji = {self.X: cross_emoji, self.O: circle_emoji}[self.current_player]
		button.disabled = True
		self.board[y][x] = self.current_player
		self.current_player = self.get_other_player()

		if self.players[self.current_player].bot:
			for child in self.children:
				child.disabled = True
		
		winner = self.check_board_winner()
		if winner is not None:
			if winner in (self.X, self.O):
				status = f':tada: ¡**{self.players[winner].name}** ha ganado la partida!'
			else:
				status = ':flag_white: La partida terminó en un empate'

			for child in self.children:
				child.disabled = True

			self.stop()
			if interaction.response.is_done():
				await interaction.edit_original_response(content=self.get_content(status), view=self)
			else:
				await interaction.response.edit_message(content=self.get_content(status), view=self)
			return

		if interaction.response.is_done():
			await interaction.edit_original_response(content=self.get_content(), view=self)
		else:
			await interaction.response.edit_message(content=self.get_content(), view=self)

		if self.current_player == self.O and self.players[self.O].bot:
			await asyncio.sleep(1.5)
			available_moves = [[x, y] if self.board[y][x] == 0 else None for x in range(3) for y in range(3)]
			available_moves = list(filter(lambda x: x != None, available_moves))
			button_x, button_y = choice(available_moves)
			for child in self.children:
				if self.board[child.y][child.x] not in (self.X, self.O):
					child.disabled = False
			await self.play(interaction, button_x, button_y)

	# This method checks for the board winner -- it is used by the TicTacToeButton
	def check_board_winner(self):
		for across in self.board:
			value = sum(across)
			if value == 3:
				return self.O
			elif value == -3:
				return self.X

		# Check vertical
		for line in range(3):
			value = self.board[0][line] + self.board[1][line] + self.board[2][line]
			if value == 3:
				return self.O
			elif value == -3:
				return self.X

		# Check diagonals
		diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
		if diag == 3:
			return self.O
		elif diag == -3:
			return self.X

		diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
		if diag == 3:
			return self.O
		elif diag == -3:
			return self.X

		# If we're here, we need to check if a tie was made
		if all(i != 0 for row in self.board for i in row):
			return self.Tie

		return None



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
	def searching(text:str, unicode=False):
		return Warning.emoji_warning((':mag:', u'\U0001f50d'), text, unicode)

	@staticmethod
	def emoji_warning(emoji, text, unicode):
		return f'{emoji[int(unicode)]} {text}'



class Tag:
	__slots__ = ('interaction', 'guild', 'user', 'name', 'content', 'img', 'nsfw')

	def __init__(self, interaction, guild_id:int, user_id:int, name:str, content:str, img:bool, nsfw:bool):
		self.interaction = interaction
		self.guild = interaction.client.get_guild(guild_id)
		self.user = interaction.client.get_user(user_id)
		self.name = name
		self.content = content
		self.img = bool(img)
		self.nsfw = bool(nsfw)

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
