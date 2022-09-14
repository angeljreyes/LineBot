import asyncio
from random import choice, randint
from re import match, sub

import discord
import tictactoe as ttt
from discord.ext import commands
from requests import get

import botdata


class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.send = bot.get_cog('GlobalCog').send


	# soy
	@commands.command()
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
	@commands.command()
	async def say(self, ctx, *, arg=None):
		if arg != None:
			if ctx.channel.type != discord.ChannelType.private:
				await ctx.message.delete()
			arg = await commands.clean_content().convert(ctx, arg)
		await self.send(ctx, arg if arg != None else botdata.Warning.error('Escribe un texto para que el bot lo escriba'))


	# iq
	@commands.command(name='iq')
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
	@commands.command()
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
				emb = discord.Embed(description=request['joke'], colour=botdata.default_color(ctx)).set_author(name='Joke', icon_url=ctx.message.author.avatar_url).set_footer(text='Joke ID: '+request['id'])
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
				emb = discord.Embed(colour=botdata.default_color(ctx)).set_image(url=url).set_author(name='Joke', icon_url=ctx.message.author.avatar_url).set_footer(text='Joke ID: '+rid)
			else:
				emb = discord.Embed(description=request['joke'], colour=botdata.default_color(ctx)).set_author(name='Joke', icon_url=ctx.message.author.avatar_url).set_footer(text='Joke ID: '+rid)
		except KeyError:
			await self.send(ctx, botdata.Warning.error('ID inválida'))
		else: 
			await self.send(ctx, embed=emb)


	# nothing
	@commands.command()
	async def nothing(self, ctx):
		pass


	# gay
	@commands.command()
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
			colour=botdata.default_color(ctx)
		)
		await self.send(ctx, embed=embed)


	# tictactoe
	@commands.max_concurrency(1, commands.BucketType.channel)
	@commands.command(aliases=['ttt'])
	async def tictactoe(self, ctx, *, user=None):
		if user == None or (await commands.MemberConverter().convert(ctx, user)).id == ctx.guild.me.id:
			user = ctx.guild.me

		else:
			user = await commands.MemberConverter().convert(ctx, user)
			if user.bot:
				await self.send(ctx, botdata.Warning.error('No puedes jugar contra un bot'))
				return
			question = await botdata.askyn(ctx, f'{user.mention} ¿Quieres unirte a la partida de Tic Tac Toe de **{ctx.author.name}**?', timeout=30, user=user)
			
			if question == False:
				await self.send(ctx, botdata.Warning.cancel('La partida fue rechazada'))
				ctx.command.reset_cooldown(ctx)
				return
			
			elif question == None:
				ctx.command.reset_cooldown(ctx)
				return

		msg = await self.send(ctx, botdata.Warning.loading('Cargando tabla...'))
		board = ttt.EMPTY_BOARD
		winner = None
		players = {
			'X': ctx.author,
			'O': user
		}
		embed = discord.Embed(title='Tic Tac Toe', description=f'```{ttt.get_printable_board(board)}```', colour=botdata.default_color(ctx))
		embed.set_footer(text=f'Tip: Escribe "{ctx.prefix}{ctx.invoked_with}' + ('" para jugar contra la maquina.' if players['O'].id != ctx.guild.me.id else ' <usuario>" para jugar contra un miembro del servidor.'))
		vs = f'{players["X"].name} VS {players["O"].name}'
		embed.set_author(name=vs, icon_url=players['X'].avatar_url)
		await msg.edit(content=None, embed=embed)

		while winner == None:
			for player in players:

				if players[player].id == ctx.guild.me.id:
					await asyncio.sleep(1)
					if randint(0, 10) > 7:
						board, winner = ttt.play_random_move(board, player)
					else:
						board, winner = ttt.play_best_move(board, player)

				else:
					for attempt in range(1, 4):
						try:
							text = f'{players[player].mention}, ' + ('es tu turno' if attempt == 1 else 'ese no es un movimiento válido') + ', escribe un número del 1 al 9 o la columna y la fila, separadas por coma, e.g., `2,1`'
							position = await botdata.ask(ctx, text, user=players[player],timeout=30.0, raises=True, regex=r'[1-9][,]? *[1-3]?')
							if match(r'^[1-9]$', position):
								col, row = ttt.index_to_col_row(int(position)-1)

							elif match(r'^[1-3],[ ]*[1-3]$', position):
								col, row = sub(r'\s+', '', position).split(',')
								col, row = int(col) - 1, int(row) - 1

							else:
								raise ttt.IllegalMove

							board, winner = ttt.play(board, player, col, row)
							break

						except (ttt.IllegalMove, ValueError):
							continue

						except asyncio.TimeoutError:
							winner = ttt.opponent(player)
							await self.send(ctx, f'{botdata.Warning.error(players[player].mention)}, te tardaste mucho en responder')
							break

				embed.description = f'```{ttt.get_printable_board(board)}```'
				if winner != None:
					embed.add_field(name='Resultados de la partida', value=f'El ganador de la partida es {players[winner].name}' if winner in ('X', 'O') else 'La partida terminó en un empate')
					await msg.edit(embed=embed)
					return

				else:
					embed.set_author(name=vs, icon_url=players[ttt.opponent(player)].avatar_url)
					await msg.edit(embed=embed)


	# 8ball
	@commands.cooldown(1, 2.5, commands.BucketType.user)
	@commands.command(name='8ball', aliases=['8b'])
	async def _8ball(self, ctx, *, question=None):
		if question == None:
			await self.send(ctx, botdata.Warning.error('Escribe una pregunta'))

		else:
			await self.send(ctx, embed=botdata.embed_author(user=ctx.author, embed=discord.Embed(
				title='Respuesta 8ball',
				description=choice((
					'Sí', 'No', 'En efecto', 'Quizás', 'Mañana', 'Imposible',
					'El simple hecho de que consideraras que eso podría ser cierto es un insulto hacia la inteligencia humana',
					'¿No era obvio que sí?', 'Está científicamente comprobado que sí',
					'No, imbécil', 'Es muy probable', 'Es casi imposible', 'Para nada',
					'Totalmente', 'No lo sé', 'h', 'No lo sé, busca en Google',
					f'No lo sé, preguntale a {choice(list(filter(lambda x: not x.bot, ctx.guild.members))).mention}'
				)),
				colour=botdata.default_color(ctx)
			)))



def setup(bot):
	bot.add_cog(Fun(bot))
