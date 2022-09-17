import asyncio
from datetime import datetime, timedelta
from exceptions import BlacklistUserError, ImageNotFound
from random import choice
from re import fullmatch
from sqlite3 import connect
from requests import head
from pathlib import Path

import discord
from discord.ext import commands

import helpsys
import logging

# stable / dev
bot_mode = 'stable'
bot_version = '1.4'

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

conn = connect(f'{Path().resolve().parent}\\data.sqlite3')
cursor = conn.cursor()

returned_value = None

colors = {
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
	'dark grey':discord.Colour.dark_grey(),
	'light grey':discord.Colour.light_grey(),
	'darker grey':discord.Colour.darker_grey(),
	'blurple':discord.Colour.blurple(),
	'greyple':discord.Colour.greyple(),
	'random':discord.Colour.default()
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
	'Mi página de DBL': 'https://top.gg/bot/582009564724199434',
	'Vota por mí': 'https://top.gg/bot/582009564724199434/vote'
}


def get_prefix(bot, message, ignore_mention=False):
	if message.channel.type == discord.ChannelType.private:
		return default_prefix

	else:
		if message.content.replace('!', '').startswith(f'<@{bot.user.id}>') and not ignore_mention:
			return f'<@!{bot.user.id}> ' if message.content.startswith('<@!') else f'<@{bot.user.id}> '
		elif message.guild.id in bot.get_cog('GlobalCog').cached_prefixes:
			return bot.get_cog('GlobalCog').cached_prefixes[message.guild.id]
		else:
			cursor.execute(f"SELECT PREFIX FROM {prefix_table} WHERE ID={message.guild.id}")
			prefix = cursor.fetchall()
			conn.commit()
			prefix = prefix[0][0] if prefix != [] else default_prefix
			bot.get_cog('GlobalCog').cached_prefixes.update({message.guild.id: prefix})
			return prefix


def default_color(ctx):
	cursor.execute(f"SELECT VALUE FROM COLORS WHERE ID={ctx.message.author.id}")
	color = cursor.fetchall()
	if ctx.guild == None:
		return discord.Colour.blue()
	elif color == []:
		try:
			return ctx.guild.me.color
		except AttributeError:
			return discord.Color.blue()
	else:
		if color[0][0] == 0:
			return colors[choice(tuple(colors)[:-1])].value
		return int(color[0][0])


async def askyn(ctx, message:str, timeout=12.0, user=None):
	yes_answers = ('y', 'yes', 's', 'si')
	no_answers = ('n', 'no')
	user = ctx.author if user == None else user
	question = await ctx.send(Warning.question(f'{message} `s/n`'))
	def check(message):
		if message.author == user and message.channel.id == ctx.channel.id:
			return message.content.lower() in yes_answers or message.content.lower() in no_answers
		return False
	try:
		message = await ctx.bot.wait_for('message', timeout=timeout, check=check)
	except asyncio.TimeoutError:
		await ctx.bot.get_cog('GlobalCog').send(ctx, Warning.error(f'{user.mention} No respondiste a tiempo'))
		return None
	answer = message.content.lower()
	await ctx.channel.delete_messages((question, message))
	if answer in yes_answers:
		return True
	elif answer in no_answers:
		return False


async def ask(ctx, message:str, *, timeout=12.0, user=None, regex=None, raises=False):
	user = ctx.author if user == None else user
	question = await ctx.send(Warning.question(message))
	def check(message):
		return message.author.id == user.id and (fullmatch(regex, message.content) if regex != None else True) and message.channel.id == ctx.channel.id
	try:
		message = await ctx.bot.wait_for('message', timeout=timeout, check=check)
	except asyncio.TimeoutError:
		if raises:
			raise asyncio.TimeoutError
		else:
			await ctx.bot.get_cog('GlobalCog').send(ctx, Warning.error(f'{user.mention} No respondiste a tiempo'))
			return None
	await ctx.channel.delete_messages((question, message))
	return message.content


async def get_channel_image(ctx):
	async for msg in ctx.history(limit=30):
		if msg.attachments != []:
			return msg.attachments[0].url
		elif msg.embeds != []:
			embed = msg.embeds[0]
			for check in [embed.image.url, embed.thumbnail.url]:
				if check != discord.Embed.Empty:
					return check
	raise ImageNotFound('Image not detected in the channel')


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


def owner(ctx):
	if ctx.author.id == ctx.bot.owner_id:
		return True
	else:
		raise commands.NotOwner()


def is_owner():
	def predicate(ctx):
		return owner(ctx)
	return commands.check(predicate)


def check_blacklist(ctx, user=None, raises=True):
	user = ctx.author if user == None else user
	cursor.execute(f"SELECT USER FROM BLACKLIST WHERE USER={user.id}")
	check = cursor.fetchall()
	conn.commit()
	if check == []:
		return True
	if raises:
		raise BlacklistUserError('This user is in the blacklist')
	else:
		return False


def config_commands(bot):
	for command in bot.commands:
		if command.name in helpsys.descs:
			command.description = helpsys.descs[command.name]

		if command.cog.qualified_name == 'Owner':
			command.add_check(owner)
			bot.add_check(check_blacklist)


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


def add_fields(embed:discord.Embed, data_dict:dict, *, inline_char='~'):
	inline_char = '' if inline_char == None else inline_char
	for data in data_dict:
		if data_dict[data] not in (None, ''):
			if inline_char != '':
				embed.add_field(name=data.replace(inline_char, ''), value=str(data_dict[data]), inline=not data.endswith(inline_char))
			else:
				embed.add_field(name=data, value=str(data_dict[data]), inline=False)
	return embed


def embed_author(embed:discord.Embed, user:discord.User):
	return embed.set_author(name=user.name, icon_url=user.avatar_url)



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
	def from_list(ctx, title:str, iterable: list, *, colour=None):
		formated = []
		count = 0
		for i in iterable:
			count += 1
			formated.append(f'{count}. {i}')

		pages = []
		for i in range(int((len(formated) - 1)//20 + 1)):
			pages.append(Page(embed=discord.Embed(
				title=title,
				description='\n'.join(formated[i*20:i*20+20]),
				colour=default_color(ctx)
			)))
		return pages



class NavBar:
	__slots__ = ('ctx', 'page_num', 'page', 'pages', 'entries', 'timeout', 'edited_at', 'nav_emojis', 'message')

	def __init__(self, ctx:commands.Context, *, pages: list=[], entries: int=None, timeout=180.0):
		self.ctx = ctx
		self.page_num = 1
		self.page = None
		self.pages = []
		self.entries = entries
		self.timeout = timeout
		self.add_pages(pages)
		self.edited_at = ctx.message.edited_at
		self.nav_emojis = {
			u'\U000023ee': ('first', 3),
			u'\U00002b05': ('back', 2),
			u'\U000027a1': ('next', 2),
			u'\U000023ed': ('last', 3),
			u'\U0001f522': ('search', 4),
			u'\U000023f9': ('stop', 2)
		}


	def add_pages(self, pages:list):
		count = 0
		for page in pages:
			count += 1
			if page.embed != None:
				page.embed.set_footer(text=(f'Página {len(self.pages)+count} de {len(pages) + len(self.pages)}' if len(self.pages)+len(pages) > 1 else '') + f'{(str(" ("+str(self.entries)+" resultados)")) if self.entries != None else ""}' + (f' | {page.embed.footer.text}' if page.embed.footer.text != discord.Embed.Empty else ""))
		self.pages += pages


	async def start(self):
		self.message = await self.ctx.bot.get_cog('GlobalCog').send(self.ctx, self.pages[0].content, embed=self.pages[0].embed)
		if len(self.pages) > 1:
			self.page = self.pages[0]
			for emoji in self.nav_emojis:
				if len(self.pages) >= self.nav_emojis[emoji][1]:
					await self.message.add_reaction(emoji)
			await self.wait()


	def check(self, reaction, user):
		if self.edited_at != self.ctx.message.edited_at:
			raise ValueError
		return all([user == self.ctx.author, str(reaction.emoji) in self.nav_emojis,
			reaction.message.id == self.message.id])


	async def wait(self):
		try:
			reaction, user = await self.ctx.bot.wait_for('reaction_add', timeout=self.timeout, check=self.check)
		except asyncio.TimeoutError:
			await self.message.clear_reactions()
		except ValueError:
			pass
		else:
			await self.message.remove_reaction(reaction.emoji, user)
			reaction = str(reaction.emoji)
			if self.nav_emojis[reaction][0] == 'first' and self.page_num != 1:
				await self.set_page(1)

			elif self.nav_emojis[reaction][0] == 'back' and self.page_num != 1:
				await self.set_page(self.page_num-1)

			elif self.nav_emojis[reaction][0] == 'next' and self.page_num != len(self.pages):
				await self.set_page(self.page_num+1)

			elif self.nav_emojis[reaction][0] == 'last' and self.page_num != len(self.pages):
				await self.set_page(len(self.pages))

			elif self.nav_emojis[reaction][0] == 'search':
				search = int(await ask(self.ctx, 'Escribe la pagina a la que quieres ir', regex=r'[0-9]+'))
				if search != self.page_num and (0 < search < len(self.pages)+1):
					await self.set_page(search)

			elif self.nav_emojis[reaction][0] == 'stop':
				await self.message.delete()
				return

			await self.wait()


	async def set_page(self, page:int):
		self.page = self.pages[page-1]
		self.page_num = page
		await self.message.edit(content=self.page.content, embed=self.page.embed)



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
