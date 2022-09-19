import asyncio
from random import choice, randint

import discord
from discord import app_commands
from discord.ext import commands

import modded_libraries.tictactoe as ttt
from requests import get

import core


class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.send = bot.get_cog('GlobalCog').send


	# soy
	@app_commands.command()
	async def soy(self, ctx):
		await self.send(ctx, choice((
		'Eres re gay, te encanta chuparla',
		'Eres un wn con pija dorada',
		'Eres alto imbécil, juegas Free Fire y te matan 2374 veces por partida',
		'Eres mi exclavo sexual B)',
		'Eres un gamer de nivel superior :cowboy:',
		'Eres el novio de Macri B(',
		'Eres el CEO de Anonymous y le puedes hackear la PC al Tech Nigga',
		'Eres hijo de WindyGirk y Yao Cabrera',
		'Eres hijo de Elon Musk :o',
		'gay',
		'Eres más gordo que Zapata',
		'Sos un capo sabelo',
		'Eres anti-vacunas'
	)))


	# say
	@commands.cooldown(5, 5.0, commands.BucketType.user)
	@app_commands.command()
	async def say(self, ctx, *, arg=None):
		if arg != None:
			if ctx.channel.type != discord.ChannelType.private:
				await ctx.message.delete()
			arg = await commands.clean_content().convert(ctx, arg)
		await self.send(ctx, arg if arg != None else core.Warning.error('Escribe un texto para que el bot lo escriba'))


	# iq
	@app_commands.command(name='iq')
	async def _iq(self, ctx, user:discord.Member=''):
		iqs = (
			'-10, tu cabeza está en blanco, ni siquiera deberias estar respirando :thinking:',
			'0, como chucha usaste este comando?',
			'10, no sabes ni leer seguro ***XD***',
			'30, un perro iguala tu inteligencia',
			'50, seguro tus padres son hermanos :pensive:',
			'60, alto retraso mental tienes',
			'80, no eres muy tonto, pero no eres inteligente hm',
			'100, justo en la media :o',
			'120, felicidades, ahora te hacen bullying',
			'140, seguro eres el gafitas del salón de clases',
			'150, re capo eres',
			'170, el Einstein te dicen',
			'200 :0000',
			'300, tu cerebro es una pc master race dou',
			'infinito qqq'
		)
		await self.send(ctx, 'Tienes un IQ de ' + choice(iqs) if user == '' else f'**{str(user)[0:-5]}**, tienes un {choice(iqs)}')


	# joke
	@commands.cooldown(1, 2.0, commands.BucketType.user)
	@app_commands.command()
	async def joke(self, ctx, *, args=None):
		if args == None or not args.endswith('-img'):
			isImg = False
		else:
			isImg = True
			args = args.replace('-img', '')
			if args == '': args = None
		# id
		if args != None:
			#search
			if args.startswith('search'):
				url = 'https://icanhazdadjoke.com/search'
				term = args[7:] if args not in ('search', 'search ') else ''
				request = get('https://icanhazdadjoke.com/', params={'term':term}, headers={'Accept':'application/json'}).json()
				emb = discord.Embed(description=request['joke'], colour=core.default_color(ctx)).set_author(name='Joke', icon_url=ctx.message.author.avatar.url).set_footer(text='Joke ID: '+request['id'])
				await self.send(ctx, embed=emb)
				return
			url = 'https://icanhazdadjoke.com/j/'+args.split(' ')[0]
		# random
		elif args == None:
			url = 'https://icanhazdadjoke.com/'
		request = get(url, headers={'Accept':'application/json'}).json()
		try:
			rid = request['id']
			if isImg:
				url = f'https://icanhazdadjoke.com/j/{rid}.png'
				emb = discord.Embed(colour=core.default_color(ctx)).set_image(url=url).set_author(name='Joke', icon_url=ctx.message.author.avatar.url).set_footer(text='Joke ID: '+rid)
			else:
				emb = discord.Embed(description=request['joke'], colour=core.default_color(ctx)).set_author(name='Joke', icon_url=ctx.message.author.avatar.url).set_footer(text='Joke ID: '+rid)
		except KeyError:
			await self.send(ctx, core.Warning.error('ID inválida'))
		else: 
			await self.send(ctx, embed=emb)


	# nothing
	@app_commands.command()
	async def nothing(self, ctx):
		pass


	# gay
	@app_commands.command()
	async def gay(self, ctx, *, user=None):
		user = ctx.message.author.display_name if user == None else (await commands.MemberConverter().convert(ctx, user)).display_name
		percent = randint(0, 100)
		extra = {
			10:'se le cayó el pene',
			9:'le dan asco las mujeres',
			8:'se corre al pensar en hombres',
			7:'le encanta chupar piroca',
			6:'está pensando en penes ahora mismo',
			5:'es bisexual, re normie ndeah',
			4:'seguro está enamorado de su mejor amigo',
			3:'es el chico afeminado del grupo',
			2:'aunque no lo acepte, le excita un poco el porno gay',
			1:'hombre heterosexual promedio',
			0:'hasta le dan asco los hombres'
		}[percent//10]
		embed = discord.Embed(
			title='Medidor gamer de homosexualidad',
			description=f'{user} es un {percent}% gay, {extra}.',
			colour=core.default_color(ctx)
		)
		await self.send(ctx, embed=embed)


	# tictactoe
	@commands.max_concurrency(1, commands.BucketType.user)
	@app_commands.command(aliases=['ttt'])
	async def tictactoe(self, ctx, *, user=None):
		if user == None or (await commands.MemberConverter().convert(ctx, user)).id == ctx.guild.me.id:
			user = ctx.guild.me

		else:
			user = await commands.MemberConverter().convert(ctx, user)
			if user.bot:
				await self.send(ctx, core.Warning.error('No puedes jugar contra un bot'))
				return
			question = await core.askyn(ctx, f'{user.mention} ¿Quieres unirte a la partida de Tic Tac Toe de **{ctx.author.name}**?', timeout=120, user=user)
			
			if question == False:
				await self.send(ctx, core.Warning.cancel('La partida fue rechazada'))
				ctx.command.reset_cooldown(ctx)
				return
			
			elif question == None:
				ctx.command.reset_cooldown(ctx)
				return

		msg = await self.send(ctx, core.Warning.loading('Cargando tabla...'))
		board = ttt.EMPTY_BOARD
		winner = None
		timeout_win = False
		x_emoji = await commands.PartialEmojiConverter().convert(ctx, core.cross_emoji)
		o_emoji = await commands.PartialEmojiConverter().convert(ctx, core.circle_emoji)
		empty_emoji = await commands.PartialEmojiConverter().convert(ctx, core.empty_emoji)
		players = {
			'X': ctx.author,
			'O': user
		}
		buttons = {
			'X': lambda x: discord.Button(custom_id='X', style=1, emoji=x_emoji),
			'O': lambda x: discord.Button(custom_id='O', style=3, emoji=o_emoji),
			None: lambda cid: discord.Button(custom_id=cid, style=2, emoji=empty_emoji)
		}
		def check(interaction, button):
			return interaction.message.id == msg.id and interaction.author.id == players[player].id and button.custom_id not in ('X', 'O')
		header = f'__**Tic Tac Toe**__\n:crossed_swords: **{players["X"].name}** vs **{players["O"].name}**'
		content = header + f'\n:timer: Turno de {players["X"].mention}'
		components = [[buttons[None](f'{i*3+j}{i}{j}') for j in range(3)] for i in range(3)]
		ic(components[0][0].custom_id)
		await msg.edit(content=content, components=components)

		while winner == None:
			for player in players:

				if players[player].id == ctx.guild.me.id:
					await asyncio.sleep(1.5)
					if randint(0, 10) > 7:
						board, winner = ttt.play_random_move(board, player)
					else:
						board, winner = ttt.play_best_move(board, player)

				else:
					try:
						interaction, button = await ctx.bot.wait_for('button_click', timeout=30, check=check)
						await interaction.defer()
						col, row = ttt.index_to_col_row(int(button.custom_id[0]))
						board, winner = ttt.play(board, player, col, row)

					except (ttt.IllegalMove, ValueError):
						pass

					except asyncio.TimeoutError:
						winner = ttt.opponent(player)
						timeout_win = True

				for i in range(3):
					for j in range(3):
						components[i][j] = buttons[board[i*3+j]](f'{i*3+j}{i}{j}')
				if winner != None:
					content = header + (f'\n:crown: {(players[player].name + " se tardó demasiado en responder, ") if timeout_win else ""}**{players[winner].name}** ganó la partida' if winner in ('X', 'O') else '\n:flag_white: La partida terminó en un empate')
					for i in range(3):
						for j in range(3):
							components[i][j]._disabled = True
					try:
						await interaction.edit(content=content, components=components)
					except UnboundLocalError:
						await msg.edit(content=content, components=components)
					return

				else:
					content = header + f'\n:timer: Turno de {players[ttt.opponent(player)].mention}'
					await interaction.edit(content=content, components=components)


	# 8ball
	@commands.cooldown(1, 2.5, commands.BucketType.user)
	@app_commands.command(name='8ball', aliases=['8b'])
	async def _8ball(self, ctx, *, question=None):
		if question == None:
			await self.send(ctx, core.Warning.error('Escribe una pregunta'))

		else:
			await self.send(ctx, embed=core.embed_author(user=ctx.author, embed=discord.Embed(
				title='Respuesta 8ball',
				description=choice((
					'Sí', 'No', 'En efecto', 'Quizás', 'Mañana', 'Imposible',
					'El simple hecho de que consideraras que eso podría ser cierto es un insulto hacia la inteligencia humana',
					'¿No era obvio que sí?', 'Está científicamente comprobado que sí',
					'No, imbécil', 'Es muy probable', 'Es casi imposible', 'Para nada',
					'Totalmente', 'No lo sé', 'h', 'No lo sé, busca en Google',
					f'No lo sé, preguntale a {choice(list(filter(lambda x: not x.bot, ctx.guild.members))).mention}'
				)),
				colour=core.default_color(ctx)
			)))



def setup(bot):
	bot.add_cog(Fun(bot))
