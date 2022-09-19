import asyncio
import exceptions
import json
from random import choice, randint
from re import findall, fullmatch, search
from urllib.parse import quote, unquote

import discord
import rule34
from aiohttp import ClientOSError
from discord.ext import commands
from requests import get
from signi import get_defs
from wiktionaryparser import WiktionaryParser as WikPar

import botdata

rule34 = rule34.Rule34(asyncio.get_event_loop())


class Util(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.morse_dict = { 'A':'.-', 'B':'-...', 'C':'-.-.', 'D':'-..', 'E':'.', 'F':'..-.', 'G':'--.',
		'H':'....', 'I':'..', 'J':'.---', 'K':'-.-', 'L':'.-..', 'M':'--', 'N':'-.', 'Ñ':'--.--',
		'O':'---', 'P':'.--.', 'Q':'--.-', 'R':'.-.', 'S':'...', 'T':'-', 'U':'..-', 'V':'...-',
		'W':'.--', 'X':'-..-', 'Y':'-.--', 'Z':'--..', '1':'.----', '2':'..---', '3':'...--',
		'4':'....-', '5':'.....', '6':'-....', '7':'--...', '8':'---..', '9':'----.', '0':'-----',
		',':'--..--', '.':'.-.-.-', '?':'..--..', '!':'--..--', '/':'-..-.', '-':'-....-', '(':'-.--.',
		')':'-.--.-', '"':'.-..-.', ':':'---...', ';':'-.-.-.', '\'':'.----.', '=':'-...-',
		'&':'.-...', '+':'.-.-.', '_':'..--.-', '$':'...-..-', '@':'.--.-.', ' ':'/'}
		self.send = bot.get_cog('GlobalCog').send


	def add_tag(self, ctx, name, content, nsfw:bool, img:bool):
		botdata.cursor.execute(f"SELECT * FROM TAGS2 WHERE GUILD={ctx.guild.id} AND NAME=?", (name,))
		check = botdata.cursor.fetchall()
		botdata.conn.commit()
		if len(check) == 0:
			botdata.cursor.execute("INSERT INTO TAGS2 VALUES(?,?,?,?,?,?)", (ctx.guild.id, ctx.author.id, name, content, int(nsfw), int(img)))
			botdata.conn.commit()
		else: 
			raise exceptions.ExistentTagError(f'Tag "{name}" already exists')


	async def check_tag(self, ctx, tag_name, tag_content):
		if len(tag_name) > 32:
			ctx.command.reset_cooldown(ctx)
			raise ValueError('Tag name limit reached')

		else:
			for char in tag_name:
				if char in (' ', '_', '~', '*', '`', '|'):
					ctx.command.reset_cooldown(ctx)
					raise ValueError('Invalid characters detected')
			flags = {'nsfw':False, 'img':False}
			for flag in flags:
				if f'-{flag}' in tag_content:
					tag_content = tag_content.replace(f'-{flag}', '')
					flags[flag] = True

			if ctx.channel.is_nsfw:
				flags['nsfw'] = True

			if flags['img']:
				try:
					tag_content = await botdata.get_channel_image(ctx)
					test_embed = discord.Embed(title=tag_name, colour=botdata.default_color(ctx)).set_image(url=tag_content)
					check = await ctx.send(embed=test_embed)
					await check.delete()
				except:
					raise ValueError('Invalid URL')
			
			return tag_content, flags


	def get_tag(self, ctx, name:str, guild=None):
		botdata.cursor.execute(f"SELECT * FROM TAGS2 WHERE GUILD={ctx.guild.id if guild == None else guild.id} AND NAME=?", (name,))
		tag = botdata.cursor.fetchall()
		botdata.conn.commit()
		if tag != []:
			tag = tag[0]
			return botdata.Tag(ctx, tag[0], tag[1], tag[2], tag[3], bool(tag[4]), bool(tag[5]))
		else:
			raise exceptions.NonExistentTagError('This tag does not exist')


	def get_member_tags(self, ctx, user:discord.Member):
		botdata.cursor.execute(f"SELECT * FROM TAGS2 WHERE GUILD={ctx.guild.id} AND USER={user.id}")
		tags = botdata.cursor.fetchall()
		botdata.conn.commit()
		if tags != []:
			return [botdata.Tag(ctx, tag[0], tag[1], tag[2], tag[3], bool(tag[4]), bool(tag[5])) for tag in tags]
		else:
			raise exceptions.NonExistentTagError('This user doesn\'t have tags')


	def get_guild_tags(self, ctx):
		botdata.cursor.execute(f"SELECT * FROM TAGS2 WHERE GUILD={ctx.guild.id}")
		tags = botdata.cursor.fetchall()
		botdata.conn.commit()
		if tags != []:
			return [botdata.Tag(ctx, tag[0], tag[1], tag[2], tag[3], bool(tag[4]), bool(tag[5])) for tag in tags]
		else:
			raise exceptions.NonExistentTagError('This server doesn\'t have tags')


	# choose
	@commands.cooldown(5, 5.0, commands.BucketType.user)
	@commands.command(aliases=['choice'])
	async def choose(self, ctx, *, args=''):
		if args != '':
			args = args.replace(', ', ',')
			args = args.split(',')
		
		emb = discord.Embed(
			title='Yo creo que...',
			description=choice(['Si', 'No'] if args == '' else args),
			colour=botdata.default_color(ctx)
		)

		await self.send(ctx, embed=emb)


	# poll
	@commands.cooldown(1, 6.0, commands.BucketType.user)
	@commands.command()
	async def poll(self, ctx, *, args=None):
		if args == None: 
			await self.send(ctx, embed=helpsys.get_cmd(ctx, 'poll'))
		else:
			emojis = findall(r' -e [^-]*', args)
			if emojis == []:
				emojis = ' -e 👍 👎'
			else:
				emojis = emojis[0]
			content = args.replace(emojis, '')
			emojis = emojis[4:].split(' ')
			emb = discord.Embed(
				title='',
				description=content,
				colour=botdata.default_color(ctx)
			)
			emb.set_author(name=f'Encuesta hecha por {str(ctx.author.name)}', icon_url=ctx.author.avatar_url)
			msg = await self.send(ctx, embed=emb)
			for emoji in emojis:
				try:
					await msg.add_reaction(emoji)
				except:
					continue


	# kao
	@commands.cooldown(1, 3.0, commands.BucketType.user)
	@commands.command()
	async def kao(self, ctx, kaomoji='', delete=''):
		kaomojis = {
			'lenny':'( ͡° ͜ʖ ͡°)',
			'shrug':'¯\\_(ツ)_/¯',
			'lennys':'( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)',
			'disapproval':'ಠ_ಠ',
			'dollar':'[̲̅$̲̅(̲̅5̲̅)̲̅$̲̅]',
			'sniper':'▄︻̷̿┻̿═━一',
			'spiderlenny':'/╲/\\╭( ͡° ͡° ͜ʖ ͡° ͡°)╮/\\╱\\',
			'dollarlenny':'[̲̅$̲̅(̲̅ ͡° ͜ʖ ͡°̲̅)̲̅$̲̅]',
			'finnjake':'| (• ◡•)| (❍ᴥ❍ʋ)',
			'lennywall':'┬┴┬┴┤ ͜ʖ ͡°) ├┬┴┬┴'
		}
		kaomoji = kaomoji.lower()
		if kaomoji == '':
			embed = discord.Embed(
				title='Kaomojis',
				colour=botdata.default_color(ctx)
			)
			embed = botdata.add_fields(embed, kaomojis)
			embed.set_footer(text='Tip: Pon delete al final del comando para eliminar tu mensaje.')
			await self.send(ctx, embed=embed)

		elif kaomoji in kaomojis:
			await self.send(ctx, kaomojis[kaomoji])

		else:
			await self.send(ctx, botdata.Warning.error(f'Ese kaomoji no existe. Usa `{ctx.prefix}kao` para ver todos los kaomojis'))
			ctx.command.reset_cooldown(ctx)

		if delete == 'delete':
			await ctx.message.delete()


	# avatar
	@commands.cooldown(1, 2.5, commands.BucketType.user)
	@commands.command()
	async def avatar(self, ctx, *, user=''):
		user = ctx.message.author if user == '' else await botdata.get_user(ctx, user)
		await self.send(ctx, embed=discord.Embed(
			title=f'Avatar de {str(user)}',
			colour=botdata.default_color(ctx)
		).set_image(url=user.avatar_url))


	# defemoji
	@commands.command(aliases=['defaultemoji'])
	async def defemoji(self, ctx, *, emojis=None):
		if emojis == None:
			await self.send(ctx, 'Escribe algunos emojis para ver su estado por defecto')
		else:
			raw_emojis = emojis.split(' ')
			emojis = []
			for emoji in raw_emojis:
				try:
					emojis.append(await commands.PartialEmojiConverter().convert(ctx, emoji))
				except:
					if fullmatch(r'[^A-Za-z0-9]+', emoji):
						emojis.append(emoji)
					else:
						continue
			output = ' '.join((f'\\{emoji} ' for emoji in emojis))
			await self.send(ctx, output)


	# tag
	@commands.group(aliases=['t', 'tags'])
	@commands.guild_only()
	async def tag(self, ctx):
		if ctx.subcommand_passed == None:
			await self.send(ctx, embed=helpsys.get_cmd(ctx, 'tag'))

		# use a tag
		else:
			if ctx.subcommand_passed != 'toggle':
				botdata.cursor.execute(f"SELECT GUILD FROM TAGSENABLED WHERE GUILD={ctx.guild.id}")
				check = botdata.cursor.fetchall()
				if check == []:
					await self.send(ctx, botdata.Warning.info(
						f'Los tags están desactivados en este servidor. {"Actívalos" if ctx.author.permissions_in(ctx.channel).manage_guild else "Pídele a un admin que los active"} con el comando `{ctx.prefix}tag toggle`'))
					raise exceptions.DisabledTagsError('Tags are not enabled on this guild')

				elif ctx.command.get_command(ctx.subcommand_passed) == None:
					if ctx.subcommand_passed == 'use':
						tag_name = ctx.message.content.replace(f'{ctx.prefix}{ctx.invoked_with} use ', '')
					else:
						tag_name = ctx.subcommand_passed
					tag = self.get_tag(ctx, tag_name)
					if not(not ctx.channel.is_nsfw() and bool(tag.nsfw)):
						if bool(tag.img):
							emb = discord.Embed(title=tag.name, colour=botdata.default_color(ctx)).set_image(url=tag.content)
							await self.send(ctx, embed=emb)
						else:
							await self.send(ctx, await commands.clean_content().convert(ctx, tag.content))
					else:
						await self.send(ctx, botdata.Warning.error('Este tag solo puede mostrarse en canales NSFW'))


	# tag toggle
	@commands.cooldown(1, 10.0, commands.BucketType.guild)
	@tag.command(name='toggle')
	async def tag_toggle(self, ctx):
		if ctx.author.permissions_in(ctx.channel).manage_guild:
			botdata.cursor.execute(f"SELECT GUILD FROM TAGSENABLED WHERE GUILD={ctx.guild.id}")
			check = botdata.cursor.fetchall()
			if check == []:
				question = await botdata.askyn(ctx, 'Los tags en este servidor están desactivados. ¿Quieres activarlos?')
				if question:
					botdata.cursor.execute(f"INSERT INTO TAGSENABLED VALUES({ctx.guild.id})")
					await self.send(ctx, botdata.Warning.success('Se activaron los tags en este servidor'))
				elif question == False:
					await self.send(ctx, botdata.Warning.cancel('No se activaran los tags en este servidor'))

			else:
				question = await botdata.askyn(ctx, 'Los tags en este servidor están activados. ¿Quieres desactivarlos?')
				if question:
					botdata.cursor.execute(f"DELETE FROM TAGSENABLED WHERE GUILD={ctx.guild.id}")
					await self.send(ctx, botdata.Warning.success('Se desactivaron los tags en este servidor'))
				elif question == False:
					await self.send(ctx, botdata.Warning.cancel('No se desactivaran los tags en este servidor'))
			
			botdata.conn.commit()

		else:
			await self.send(ctx, botdata.Warning.error('Necesitas permiso de gestionar servidor para activar o desactivar los tags'))


	# tag add
	@commands.cooldown(1, 10.0, commands.BucketType.user)
	@tag.command(name='add', aliases=['create',])
	async def tag_add(self, ctx, tag_name=None, *, tag_content=None):
		if None in (tag_name, tag_content):
			await self.send(ctx, botdata.Warning.error('Escribe el nombre de tu tag y su contenido'))
			ctx.command.reset_cooldown(ctx)

		else:
			tag_content, flags = await self.check_tag(ctx, tag_name, tag_content)
			self.add_tag(ctx, tag_name, tag_content, flags['img'], flags['nsfw'])
			await self.send(ctx, botdata.Warning.success(f'Se agregó el tag **{await commands.clean_content().convert(ctx, tag_name)}**'))


	# tag gift
	@commands.cooldown(1, 5.0, commands.BucketType.user)
	@tag.command(name='gift')
	async def tag_gift(self, ctx, tag_name=None, user=None):
		if None in (tag_name, user):
			await self.send(ctx, botdata.Warning.error('Tienes que escribir el nombre de un tag tuyo y mencionar a alguien para regalarle el tag'))
			ctx.command.reset_cooldown(ctx)
		else:
			user = await commands.MemberConverter().convert(ctx, user)
			if user == ctx.author:
				await self.send(ctx, botdata.Warning.error('No puedes regalarte un tag a ti mismo'))
			elif user.bot:
				await self.send(ctx, botdata.Warning.error('No puedes regalarle un tag a un bot'))
			else:
				tag = self.get_tag(ctx, tag_name)
				question = await botdata.askyn(ctx, f'{user.mention} ¿Quieres aceptar el tag **{await commands.clean_content().convert(ctx, tag.name)}** por parte de {ctx.author.name}? Tienes 2 minutos para aceptar', timeout=120.0, user=user)
				if question:
					tag.gift(user)
					await self.send(ctx, botdata.Warning.success(f'El tag **{await commands.clean_content().convert(ctx, tag.name)}** fue regalado a {await commands.clean_content().convert(ctx, tag.user.name)} por parte de {await commands.clean_content().convert(ctx, ctx.author.name)}'))
				elif question == False:
					await self.send(ctx, botdata.Warning.cancel(f'{ctx.author.mention} El regalo fue rechazado'))


	# tag rename
	@commands.cooldown(1, 5.0, commands.BucketType.user)
	@tag.command(name='rename')
	async def tag_rename(self, ctx, old_name=None, new_name=None):
		if None in (old_name, new_name):
			await self.send(ctx, botdata.Warning.error('Tienes que escribir el nombre  del tag y su nuevo nombre'))
			ctx.command.reset_cooldown(ctx)
		
		else:
			for char in new_name:
				if char in (' ', '_', '~', '*', '`', '|'):
					await self.send(ctx, botdata.Warning.error('El nombre de un tag no puede contener espacios ni caracteres markdown'))
					ctx.command.reset_cooldown(ctx)
					return
			tag = self.get_tag(ctx, old_name)
			if tag.user.id == ctx.author.id:
				if tag.name == new_name:
					await self.send(ctx, botdata.Warning.error('No puedes ponerle el mismo nombre a un tag'))
				elif len(new_name) > 32:
					await self.send(ctx, botdata.Warning.error('El límite de caracteres para el nombre un tag es de 32'))
				else:
					tag.rename(new_name)
					await self.send(ctx, botdata.Warning.success(f'El nombre del tag **{await commands.clean_content().convert(ctx, old_name)}** se ha cambiado a **{await commands.clean_content().convert(ctx, new_name)}**'))

			else:
				await self.send(ctx, botdata.Warning.error('No puedes renombarar tags de otros usuarios'))


	# tag edit
	@commands.cooldown(1, 10.0, commands.BucketType.user)
	@tag.command(name='edit')
	async def tag_edit(self, ctx, tag_name=None, *, tag_content=None):
		if None in (tag_name, tag_content):
			await self.send(ctx, botdata.Warning.error('Escribe el nombre del tag y su nuevo contenido'))
			ctx.command.reset_cooldown(ctx)
			return

		tag = self.get_tag(ctx, tag_name)
		if ctx.author.id == tag.user.id:
			tag_content, flags = await self.check_tag(ctx, tag_name, tag_content)
			tag.edit(tag_content, flags['img'], flags['nsfw'])
			await self.send(ctx, botdata.Warning.success(f'Se editó el tag **{await commands.clean_content().convert(ctx, tag_name)}**'))
		
		else:
			await self.send(ctx, botdata.Warning.error('No puedes editar tags de otros usuarios'))
			ctx.command.reset_cooldown(ctx)


	# tag delete
	@commands.cooldown(1, 2.0, commands.BucketType.user)
	@tag.command(name= 'delete', aliases=['del', 'remove'])
	async def tag_delete(self, ctx, tag_name=None):
		if tag_name == None:
			await self.send(ctx, botdata.Warning.error('Escribe el nombre del tag a eliminar'))
			ctx.command.reset_cooldown(ctx)
			return

		tag = self.get_tag(ctx, tag_name)
		if ctx.author.id == tag.user.id:
			ask = await botdata.askyn(ctx, f'¿Quieres eliminar el tag **{await commands.clean_content().convert(ctx, tag_name)}**?')
			if ask == True:
				tag.delete()
				await self.send(ctx, botdata.Warning.success(f'El tag **{await commands.clean_content().convert(ctx, tag_name)}** ha sido eliminado'))
			elif ask == False:
				await self.send(ctx, botdata.Warning.cancel(f'El tag no será eliminado'))
			else:
				return

		else: 
			await self.send(ctx, botdata.Warning.error('No puedes eliminar tags de otros usuarios'))
			ctx.command.reset_cooldown(ctx)


	# tag forcedelete
	@tag.command(name='forcedelete', aliases=['forcedel', 'forceremove'])
	@botdata.is_owner()
	async def forcedelete(self, ctx, tag_name=None, guild=None):
		if tag_name == None:
			await self.send(ctx, botdata.Warning.error('Escribe el nombre del tag a eliminar'))
			return
		guild = ctx.guild if guild == None else self.bot.get_guild(int(guild))

		tag = self.get_tag(ctx, tag_name, guild)
		tag.delete()
		await self.send(ctx, botdata.Warning.success(f'El tag **{await commands.clean_content().convert(ctx, tag_name)}** ha sido eliminado'))


	# tag owner
	@commands.cooldown(1, 1.5, commands.BucketType.user)
	@tag.command(name='owner')
	async def tag_owner(self, ctx, tag_name=None):
		if tag_name == None:
			await self.send(ctx, botdata.Warning.error('Escribe el nombre de un tag para ver su dueño'))
		else:
			tag = self.get_tag(ctx, tag_name)
			await self.send(ctx, botdata.Warning.info(f'El dueño del tag **{await commands.clean_content().convert(ctx, tag.name)}** es `{await commands.clean_content().convert(ctx, str(tag.user))}`'))


	# tag list
	@commands.cooldown(1, 2.0, commands.BucketType.user)
	@tag.command(name='list')
	async def tag_list(self, ctx, user=None):
		if user == None:
			user = ctx.author
		else:
			user = await commands.MemberConverter().convert(ctx, user)
		tags = list(map(lambda tag: f'"{tag}"', self.get_member_tags(ctx, user)))
		pages = botdata.Page.from_list(ctx, f'Tags de {user.name}', tags)
		await botdata.NavBar(ctx, pages=pages, entries=len(tags)).start()


	# tag serverlist
	@commands.cooldown(1, 2.0, commands.BucketType.user)
	@tag.command(name='serverlist', aliases=['guildlist'])
	async def tag_serverlist(self, ctx):
		tags = list(map(lambda tag: f'{tag.user.name}: "{tag}"', self.get_guild_tags(ctx)))
		pages = botdata.Page.from_list(ctx, f'Tags de {ctx.guild}', tags)
		await botdata.NavBar(ctx, pages=pages, entries=len(tags)).start()


	# someone
	@commands.cooldown(3, 5.0, commands.BucketType.user)
	@commands.command()
	@commands.has_permissions(mention_everyone=True)
	async def someone(self, ctx):
		await self.send(ctx, choice(ctx.guild.members).mention)


	# ocr
	@commands.cooldown(1, 5.0, commands.BucketType.channel)
	@commands.command()
	async def ocr(self, ctx):
		images = await botdata.get_channel_image(ctx)
		url = ('https://api.tsu.sh/google/ocr?q=' + images) if images != None else None
		try:
			text = get(url).json()['text']
		except KeyError:
			await self.send(ctx, botdata.Warning.error('La imagen es inválida'))
		else:
			await self.send(ctx, f'```{text}```' if text != '' else botdata.Warning.error('La imagen no contiene texto'))


	# dle
	@commands.cooldown(1, 5.0, commands.BucketType.user)
	@commands.command(aliases=['rae'])
	async def dle(self, ctx, *, query=None):
		if query == None:
			await self.send(ctx, botdata.Warning.error('Escribe una palabra en español para buscar su significado'))
			ctx.command.reset_cooldown(ctx)

		else:
			query = query.lower()
			defs = get_defs(query)
			if defs != ['']:
				embed = discord.Embed(title=query.capitalize(), colour=botdata.default_color(ctx)).set_author(name='DLE', icon_url=ctx.message.author.avatar_url)
				count = 0
				desc = ''
				pages = []
				for _def in defs:
					if len(desc + f'{_def}\n') > 2048:
						embed.description = desc
						pages.append(botdata.Page(embed=embed))
						desc = ''
						embed = discord.Embed(title=query.capitalize(), colour=botdata.default_color(ctx)).set_author(name='DRAE', icon_url=ctx.message.author.avatar_url)

					count += 1
					number = int(findall(r'^[0-9]+', _def)[0])
					if count != number:
						desc += '\n'
						count = number
					desc += f'{_def}\n'
				
				embed.description = desc
				pages.append(botdata.Page(embed=embed))
				await botdata.NavBar(ctx, pages=pages, entries=len(defs)).start()
			
			else:
				await self.send(ctx, botdata.Warning.error('Palabra no encontrada'))


	# wiktionary
	@commands.cooldown(1, 5.0, commands.BucketType.user)
	@commands.command(aliases=['wikt', 'wt'])
	async def wiktionary(self, ctx, *, query=None):
		if query == None:
			await self.send(ctx, botdata.Warning.error(f'Escribe una palabra en inglés para buscar su significado. Para buscar palabras en español, usa `{ctx.prefix}dle`'))
			ctx.command.reset_cooldown(ctx)

		else:
			query = query.capitalize()
			parser = WikPar()
			try:
				word = parser.fetch(query.lower())[0]
			except IndexError:
				word = {'etymology': '', 'definitions': [], 'pronunciations': {'text': [], 'audio': []}}
			if word == {'etymology': '', 'definitions': [], 'pronunciations': {'text': [], 'audio': []}}:
				await self.send(ctx, botdata.Warning.error('Palabra no encontrada'))
				ctx.command.reset_cooldown(ctx)
			else:
				pages = [botdata.Page(embed=discord.Embed(title=query, colour=botdata.default_color(ctx)).set_author(name='Wiktionary', icon_url=ctx.message.author.avatar_url))]
				entries = 0
				for definition in word['definitions']:
					value = ['']
					count = 0
					page_count = 0
					
					for entry in definition['text']:
						entries += 1 if count != 0 else 0
						if len(value[page_count] + f'{count}. {entry}\n' if count > 0 else f'{entry}\n') > 1022:
							value.append('')
							page_count += 1
							pages.append(botdata.Page(embed=discord.Embed(title=query, colour=botdata.default_color(ctx)).set_author(name='Wiktionary', icon_url=ctx.message.author.avatar_url)))
						value[page_count] += f'{count}. {entry}\n' if count > 0 else f'{entry}\n'
						count += 1
					
					for i in range(len(value)):
						pages[i].embed.add_field(name=definition['partOfSpeech'].capitalize(), value=value[i], inline=False)
				
				await botdata.NavBar(ctx, pages=pages, entries=entries).start()


	# binary
	@commands.cooldown(2, 2.0, commands.BucketType.user)
	@commands.group()
	async def binary(self, ctx):
		if ctx.invoked_subcommand == None:
			await ctx.trigger_typing()
			await self.send(ctx, embed=helpsys.get_cmd(ctx,))


	# binary encode
	@binary.command(name='encode')
	async def binary_encode(self, ctx, *, text=None):
		if text == None:
			await self.send(ctx, botdata.Warning.error('Escribe un texto para codificarlo'))
		else:
			string = ' '.join(bin(ord(char)).split('b')[1].rjust(8, '0') for char in text)
			await self.send(ctx, f'```{string}```')


	# binary decode
	@binary.command(name='decode')
	async def binary_decode(self, ctx, *, text=None):
		if text == None:
			await self.send(ctx, botdata.Warning.error('Escribe un texto para decodificarlo'))

		elif search(r'[^0-1]', text.replace(' ', '')):
			await self.send(ctx, botdata.Warning.error('Escribe un texto en binario'))

		else:
			string = text.replace(' ', '')
			string = " ".join(string[i:i+8] for i in range(0, len(string), 8))
			string = ''.join(chr(int(binary, 2)) for binary in string.split(' '))
			await self.send(ctx, f'```{await commands.clean_content().convert(ctx, string.replace("`", "`឵"))}```')


	# morse
	@commands.cooldown(2, 2.0, commands.BucketType.user)
	@commands.group()
	async def morse(self, ctx):
		if ctx.invoked_subcommand == None:
			await ctx.trigger_typing()
			await self.send(ctx, embed=helpsys.get_cmd(ctx, 'morse'))


	# morse encode
	@morse.command(name='encode')
	async def morse_encode(self, ctx, *, text=None):
		if text == None:
			await self.send(ctx, botdata.Warning.error('Escribe un texto para codificarlo'))
		else:
			string = ''
			text = text.upper()
			for letter in text:
				if letter in self.morse_dict:
					string += self.morse_dict[letter] + ' '
			await self.send(ctx, f'```{string}```' if string != '' else botdata.Warning.error('Los caracteres especificados son incompatibles'))


	# morse decode
	@morse.command(name='decode')
	async def morse_decode(self, ctx, *, text=None):
		if text == None:
			await self.send(ctx, botdata.Warning.error('Escribe un texto para decodificarlo'))
		else:
			text += ' '
			string = ''
			citext = ''
			for letter in text:
				if letter != ' ':
					citext += letter
				else:
					if citext in list(self.morse_dict.values()):
						string += list(self.morse_dict.keys())[list(self.morse_dict.values()).index(citext)] 
					citext = ''
			await self.send(ctx, f'```{(await commands.clean_content().convert(ctx, string)).capitalize()}```' if string != '' else botdata.Warning.error('Los caracteres especificados son incompatibles'))

	
	# percentencoding
	@commands.cooldown(2, 2.0, commands.BucketType.user)
	@commands.group(aliases=[r'%enc', 'perenc'])
	async def percentencoding(self, ctx):
		if ctx.invoked_subcommand == None:
			await ctx.trigger_typing()
			await self.send(ctx, embed=helpsys.get_cmd(ctx,))


	# percentencoding encode
	@percentencoding.command(name='encode')
	async def percentencoding_encode(self, ctx, *, text=None):
		if text == None:
			await self.send(ctx, botdata.Warning.error('Escribe un texto para codificarlo'))
		else:
			await self.send(ctx, f'```{quote(text)}```')


	# percentencoding decode
	@percentencoding.command(name='decode')
	async def percentencoding_decode(self, ctx, *, text=None):
		if text == None:
			await self.send(ctx, botdata.Warning.error('Escribe un texto para decodificarlo'))

		else:
			await self.send(ctx, f'```{await commands.clean_content().convert(ctx, unquote(text))}```')


	# userinfo
	@commands.cooldown(1, 3.0, commands.BucketType.user)
	@commands.command(aliases=['user'])
	@commands.guild_only()
	async def userinfo(self, ctx, *, user=None):
		user = ctx.author if user == None else await botdata.get_user(ctx, user)
		data_dict = {
			'Usuario': str(user),
			'ID': user.id,
			'Tipo de cuenta~': {True:'Bot', False:'Usuario'}[user.bot] + (' del sistema de discord' if user.system else ''),
			'Fecha de creación de la cuenta': botdata.fix_date(user.created_at, True, True)
		}
		try:
			user = await commands.MemberConverter().convert(ctx, str(user.id))
		except:
			pass
		else:
			data_dict.update({
				'Apodo':user.nick,
				'Fecha de entrada al servidor': botdata.fix_date(user.joined_at, True, True),
				'Permisos en este canal~': f'Integer: `{user.permissions_in(ctx.channel).value}`\n' + ', '.join((f'{("`"+perm[0].replace("_"," ").capitalize()+"`") if perm[1] else ""}' for perm in tuple(filter(lambda x: x[1], tuple(user.permissions_in(ctx.channel)))))),
				'Boosteando el server desde': botdata.fix_date(user.premium_since, True, True) if user.premium_since != None else None,
				'Actividades':'\n'.join(({
					discord.ActivityType.unknown: 'Desconocido ',
					discord.ActivityType.playing: 'Jugando a ',
					discord.ActivityType.streaming: 'Transmitiendo ',
					discord.ActivityType.listening: 'Escuchando ',
					discord.ActivityType.watching: 'Viendo ',
					discord.ActivityType.custom:''
					}[activity.type]+(f'**{activity.name}**' if activity.type != discord.ActivityType.custom else str(user.activity)) for activity in user.activities)) if len(user.activities) > 0 else None,
				'Color HEX':str(user.color),
				'Estados':'\n'.join((client[0]+{
						'online': 'En linea',
						'offline': 'Desconectado',
						'idle': 'Ausente',
						'dnd': 'No molestar'
					}[str(client[1])] for client in ((':desktop: ', user.desktop_status), (':iphone: ', user.mobile_status), (':globe_with_meridians: ', user.web_status)))),
				})
		embed = discord.Embed(title='Información del usuario', colour=botdata.default_color(ctx)).set_thumbnail(url=user.avatar_url)
		for data in data_dict:
			if data_dict[data] != None:
				if data == 'Apodo':
					embed.insert_field_at(1, name=data, value=data_dict[data])
				else:	
					embed.add_field(name=data.replace('~', ''), value=data_dict[data], inline=not data.endswith('~'))
		await self.send(ctx, embed=embed)


	# roleinfo
	@commands.cooldown(1, 3.0, commands.BucketType.user)
	@commands.command(aliases=['role'])
	@commands.guild_only()
	async def roleinfo(self, ctx, *, role=None):
		if role == None:
			await self.send(ctx, embed=helpsys.get_cmd(ctx))
		else:
			role = await commands.RoleConverter().convert(ctx, role)
			data_dict = {
				'Nombre': role.name,
				'Mención': role.mention,
				'ID': role.id,
				'Posición': f'{role.position} de {len(ctx.guild.roles)-1}',
				'Mencionable': botdata.bools[role.mentionable],
				'Aparece separado': botdata.bools[role.hoist],
				'Manejado por una integración': botdata.bools[role.managed],
				'Color HEX': str(role.color),
				'Fecha de creación': botdata.fix_date(role.created_at, True, True),
				'Cantidad de usuarios': f'{len(role.members)} de {len(ctx.guild.members)}',
				'Permisos~': f'Integer: `{role.permissions.value}`\n' + ', '.join((f'{("`"+perm[0].replace("_"," ").capitalize()+"`") if perm[1] else ""}' for perm in tuple(filter(lambda x: x[1], tuple(role.permissions)))))
			}
			embed = discord.Embed(title='Información del rol', colour=botdata.default_color(ctx))
			embed = botdata.add_fields(embed, data_dict)
			await self.send(ctx, embed=embed)


	# channelinfo
	@commands.cooldown(1, 3.0, commands.BucketType.user)
	@commands.command(aliases=('channel', 'categoryinfo', 'category'))
	async def channelinfo(self, ctx, *, channel=None):
		channel = ctx.channel if channel == None else await botdata.ChannelConverter().convert(ctx, channel)
		data_dict = {
			'Nombre': str(channel),
			'ID': channel.id,
			'Fecha de creación~': botdata.fix_date(channel.created_at, True),
			'Tipo de canal': {
				discord.ChannelType.text: 'Canal de texto',
				discord.ChannelType.voice: 'Canal de voz',
				discord.ChannelType.private: 'Mensaje directo',
				discord.ChannelType.category: 'Categoría',
				discord.ChannelType.news: 'Canal de noticias',
				discord.ChannelType.store: 'Tienda'
			}[channel.type]
		}
		if channel.type not in (discord.ChannelType.private, discord.ChannelType.category):
			data_dict.update({
				'Posición': f'{channel.position+1} de {len(ctx.guild.channels)}',
				'Categoría': channel.category
			})

		if channel.type in (discord.ChannelType.text, discord.ChannelType.news):
			data_dict.update({
				'Tema': channel.topic,
				'Slowmode': f'{channel.slowmode_delay} segundos',
				'Miembros que pueden ver el canal': f'{len(channel.members)} de {len(ctx.guild.members)}',
				'Es NSFW': botdata.bools[channel.nsfw]
			})

		elif channel.type == discord.ChannelType.voice:
			data_dict.update({
				'Bitrate': f'{channel.bitrate//1000}kbps',
				'Límite de usuarios': channel.user_limit if channel.user_limit != 0 else 'Sin límite',
				'Cantidad de miembros en el canal': f'{len(channel.members)} de {len(ctx.guild.members)}' if channel.members != [] else None,
			})

		elif channel.type == discord.ChannelType.category:
			data_dict.update({
				'Posición': f'{channel.position+1} de {len(ctx.guild.channels)}',
				'Es NSFW': botdata.bools[channel.nsfw],
				'Cantidad de canales': f'De texto: {len(channel.text_channels)}\nDe voz: {len(channel.voice_channels)}\nTotal: {len(channel.channels)}'
			})

		embed = discord.Embed(title='Información del canal', colour=botdata.default_color(ctx))
		embed = botdata.add_fields(embed, data_dict)
		await self.send(ctx, embed=embed)


	# serverinfo
	@commands.cooldown(1, 3.0, commands.BucketType.user)
	@commands.command(aliases=('server', 'guildinfo', 'guild'))
	@commands.guild_only()
	async def serverinfo(self, ctx):
		guild = ctx.guild
		data_dict = {
			'Nombre': guild.name,
			'ID': guild.id,
			'Región': guild.region,
			'Fecha de creación~': botdata.fix_date(guild.created_at, True),
			'Límite AFK': f'{guild.afk_timeout} segundos',
			'Canal AFK': guild.afk_channel,
			'Canal de mensajes del sistema': guild.system_channel.mention if guild.system_channel != None else None,
			'Dueño': guild.owner.mention,
			'Máximo de miembros': guild.max_members,
			'Descripción': guild.description,
			'Autenticación de 2 factores': botdata.bools[bool(guild.mfa_level)],
			'Nivel de verificación~': {
				discord.VerificationLevel.none: 'Ninguno',
				discord.VerificationLevel.low: 'Bajo: Los miembros deben tener un email verificado en su cuenta',
				discord.VerificationLevel.medium: 'Medio: Los miembros deben tener un email verificado y estar registrados por más de 5 minutos',
				discord.VerificationLevel.high: 'Alto: Los miembros deben tener un email verificado, estar registrados por más de 5 minutos y estar en el servidor por más de 10 minutos',
				discord.VerificationLevel.extreme: 'Extremo: Los miembros deben tener un teléfono verificado en su cuenta'
			}[guild.verification_level],
			'Filtro de contenido explícito': {
				discord.ContentFilter.disabled: 'Deshabilitado',
				discord.ContentFilter.no_role: 'Analizar el contenido multimedia de los miembros sin rol',
				discord.ContentFilter.all_members: 'Analizar el contenido multimedia de todos los miembros'
			}[guild.explicit_content_filter],
			'Características': ', '.join((f'`{feature.replace("_", " ").capitalize()}`' for feature in guild.features)),
			'Número de canales': f'De texto: {len(guild.text_channels)}\nDe voz: {len(guild.voice_channels)}\nCategorías: {len(guild.categories)}\nTotal: {len(guild.channels)}',
			'Cantidad de miembros': f'''Total: {len(guild.members)}
Bots: {len(tuple(filter(lambda x: x.bot, guild.members)))}
Usuarios: {len(tuple(filter(lambda x: not x.bot, guild.members)))}
''',
# Online: {len(tuple(filter(lambda x: not x.bot and x.status == discord.Status.online, guild.members)))}
# Ausente: {len(tuple(filter(lambda x: not x.bot and x.status == discord.Status.idle, guild.members)))}
# No molestar: {len(tuple(filter(lambda x: not x.bot and x.status == discord.Status.dnd, guild.members)))}
# Desconetado: {len(tuple(filter(lambda x: not x.bot and x.status == discord.Status.offline, guild.members)))}
			'Cantidad de roles': len(guild.roles),
			'Cantidad de baneos': len(await guild.bans())
		}

		embed = discord.Embed(title='Información del servidor', colour=botdata.default_color(ctx))
		if str(guild.icon_url) != '':
			embed.set_thumbnail(url=guild.icon_url)
		embed = botdata.add_fields(embed, data_dict)
		await self.send(ctx, embed=embed)


	# count
	@commands.cooldown(1, 2.0, commands.BucketType.user)
	@commands.command()
	async def count(self, ctx, to_count=None, *, text=None):
		if None in (to_count, text):
			await self.send(ctx, embed=helpsys.get_cmd(ctx))
		else:
			count = text.count(to_count)
			embed = discord.Embed(title='Contador de caracteres', colour=botdata.default_color(ctx))
			if to_count == '':
				data_dict = {
					'Cantidad de caracteres': len(text),
					'Cantidad de palabras': len(findall(r'[A-Za-z]+', text))
				}

			else:
				if to_count.startswith(' ') or to_count.endswith(' '):
					to_count = f'"{to_count}"'
				data_dict = {
					'caracteres~': to_count,
					'Número de coincidencias': f'{len(to_count*count)} de {len(text)}',
					'Porcentaje de aparición': f'{(100 / (len(text) / len(to_count*count))) if count > 0 else 0}%'
				}
				if len(to_count) > 1:
					spaced_count = len(findall(r'[^A-Za-z]' + to_count + r'[^A-Za-z]', text))
					data_dict.update({
						'Número de coincidencias de la palabra': f'{spaced_count} de {len(text.split(" "))}',
						'Porcentaje de aparición de la palabra': f'{(100 / (len(text.split(" ")) / spaced_count)) if spaced_count > 0 else 0}%'
					})
			embed = botdata.add_fields(embed, data_dict)
			await self.send(ctx, embed=embed)


	# randomnumber
	@commands.command(aliases=['randint', 'randnum', 'ri', 'rn', 'dice', 'roll', 'rolldice'])
	async def randomnumber(self, ctx, *, args=None):
		args = list(filter(lambda x: x != '', args.replace(' ', ',').split(','))) if args != None else ['a']
		if len(list(filter(lambda x: not fullmatch(r'[-]?[0-9]+', x), args))) != 0 or len(args) == 0:
			await self.send(ctx, embed=helpsys.get_cmd(ctx))

		else:
			args = list(map(lambda x: int(x), args))
			if len(args) == 1:
				if args[0] < 0:
					start = args[0]
					end = 0
				else:
					start = 0
					end = args[0]

			else:
				try:
					start = args[0]
					end = args[1]
				except ValueError:
					await self.send(ctx, botdata.Warning.error('Intervalo inválido. Revisa que el primer número sea menor que el segundo'))
					return

			if len(f'{start}{end}') > 24:
				await self.send(ctx, botdata.Warning.error('Número demasiado grande'))

			else:
				print(start, end)
				await self.send(ctx, embed=discord.Embed(
					title=f'Número aleatorio entre {start} y {end}',
					description=str(randint(start, end)),
					colour=botdata.default_color(ctx)
				))


	#r34
	@commands.cooldown(2, 7.0, commands.BucketType.user)
	@commands.command(aliases=['rule34'])
	@commands.is_nsfw()
	async def r34(self, ctx, *, query=''):
		async with ctx.typing():
			query = query.replace(' ', '_')
			try:
				images = []
				all_images = await rule34.getImages(query, randomPID=True)
				if all_images == None:
					raise TypeError
				while len(images) < 3:
					random_img = choice(all_images)
					if random_img not in images or len(all_images) < 3:
						images.append(random_img)
			except (TypeError, ClientOSError, asyncio.TimeoutError):
				await self.send(ctx, botdata.Warning.error(
					f'Ocurrió un error. Intenta buscar el nombre del personaje completo o con el nombre de la \
serie o juego donde aparezca. Ejemplo: `{ctx.prefix}{ctx.command.name} zero two (darling in the franxx)`'
				))
				ctx.command.reset_cooldown(ctx)
				return

			else:
				for i in range(3):
					image = images[i]
					if findall(r'\.[A-Za-z0-9]+$', image.file_url)[0] in ('.mp4', '.webm'):
						await ctx.send(f'> **Video número {i+1}**\n' + 
							f'> Link del post: <https://rule34.xxx/index.php?page=post&s=view&id={image.id}>\n' +
							f'> Puntuación: `{image.score}`\n> {image.file_url}'
						)

					else:
						await ctx.send(embed=botdata.embed_author(discord.Embed(
							title=f'Imagen número {i+1}',
							description=f'[Link del post](https://rule34.xxx/index.php?page=post&s=view&id={image.id})\nPuntuación: `{image.score}`',
							colour=botdata.default_color(ctx)
						).set_image(url=image.sample_url), ctx.author))


def setup(bot):
	bot.add_cog(Util(bot))
