from random import choice, randint
from requests import get

import discord
from discord import app_commands
from discord.ext import commands

import core
import tictactoe as ttt
import db


class Fun(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot


	# soy
	@app_commands.command()
	@app_commands.checks.cooldown(1, 1.5)
	async def soy(self, interaction: discord.Interaction):
		"""Descubre quién eres"""
		await interaction.response.send_message(choice((
			'Eres re gay, te encanta chuparla',
			'Eres un weon con pija dorada',
			'Eres un jugador de Free Fire y te matan 2374 veces por partida',
			'Eres mi exclavo sexual B)',
			'Eres un gamer de nivel superior :cowboy:',
			'Eres el novio de Trump B(',
			'Eres el CEO de Anonymous y le puedes hackear la PC al Markass Brownlee',
			'Eres hijo de WindyGirk y Yao Cabrera',
			'Eres hijo de Elon Musk :o',
			'gay',
			'Eres más gordo que Nikocado Avocado',
			'Sos un capo sabelo',
			'Eres anti-vacunas',
			'Eres alguien',
			'Zoquete',
			'Eres Eren Jaeger',
			'Un indigente',
			'Eres un gordo termotanque',
			'La reencarnación de la Reina Isabel II',
			'Serás el primer ser humano en pisar Jupiter',
			'Tu vieja',
			'No sé',
			'Eres un jugador de Genshin Impact al que hay que alejar de los niños cuanto antes',
			'Eres un jugador de lol que pesa 180 kg'
		)))


	# iq
	@app_commands.command(name='iq')
	@app_commands.checks.cooldown(1, 1.5)
	@app_commands.rename(user='usuario')
	async def _iq(self, interaction: discord.Interaction, user: discord.Member | None):
		"""Calcula tu IQ o el de otra persona

		user
			Usuario al que buscar IQ
		"""
		iqs = (
			'-10, tu cabeza está en blanco, ni siquiera deberías estar respirando :thinking:',
			'0, cómo entraste siquiera a este servidor?',
			'10, no sabes ni leer seguro',
			'30, un perro iguala tu inteligencia',
			'50, seguro tus padres son hermanos :pensive:',
			'60, alto retraso mental tienes',
			'80, no eres muy tonto, pero no eres inteligente hm',
			'100, justo en la media :o',
			'120, felicidades, ahora te hacen bullying por ser diferente',
			'140, seguro eres el gafitas del salón de clases',
			'150, no puedes cargar con el peso de tu cerebro',
			'170, el Einstein te dicen',
			'200 :0000',
			'300, tu cerebro es una pc master race',
			'infinito qqq'
		)
		msg = f'{"Tienes" if user is None else user.name + ", tienes"} un IQ de {choice(iqs)}'
		await interaction.response.send_message(msg)


	# dadjoke
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5.0)
	@app_commands.rename(search='buscar', joke_id='id', image='imagen')
	async def dadjoke(
			self,
			interaction: discord.Interaction,
			search: str | None,
			joke_id: str | None,
			image: bool = False
		):
		"""Envia chistes que dan menos risa que los de Siri

		search
			Buscar una broma con el termino indicado
		joke_id
			Buscar una broma por su ID
		image
			Mostrar la broma como imagen
		"""
		BASE_URL = 'https://icanhazdadjoke.com/'
		HEADERS = {'Accept': 'application/json'}

		#search
		if search is not None:
			request: dict = get(
				f'{BASE_URL}search',
				params={'term': search},
				headers=HEADERS
			).json()
			try:
				request: dict[str, str] = request['results'][0]
			except IndexError:
				await interaction.response.send_message(
					core.Warning.error('No se encontraron resultados'),
					ephemeral=True
				)
				return

		# id
		elif joke_id is not None:
			url = f'{BASE_URL}j/{joke_id}'

		# random
		else:
			url = BASE_URL

		if search is None:
			request = get(url, headers=HEADERS).json()

		if 'id' not in request:
			await interaction.response.send_message(
				core.Warning.error('ID inválida'),
				ephemeral=True
			)
			return

		request_id = request['id']
		embed = (discord.Embed(
			title='Dad joke',
			colour=db.default_color(interaction)
		)
			.set_footer(text=f'Joke ID: {request_id}'))

		if image:
			url = f'{BASE_URL}j/{request_id}.png'
			embed.set_image(url=url)
		else:
			embed.description = request['joke']

		await interaction.response.send_message(embed=embed)


	# nothing
	@app_commands.command()
	async def nothing(self, interaction: discord.Interaction):
		"""Literalmente no hace nada"""
		pass


	# gay
	@app_commands.command()
	@app_commands.checks.cooldown(1, 1.5)
	@app_commands.rename(user='usuario')
	async def gay(self, interaction: discord.Interaction, user: discord.Member | None):
		"""Detecta como de homosexual eres

		user
			Usuario al que medirle la homosexualidad
		"""
		username = interaction.user.name if user is None else user.name
		percent = randint(0, 100)
		extra = {
			10:'se le cayó el pene',
			9:'le dan asco las mujeres',
			8:'se corre al pensar en hombres',
			7:'le encanta chupar piroca',
			6:'está pensando en penes ahora mismo',
			5:'es bisexual, re normie',
			4:'seguro está enamorado de su mejor amigo',
			3:'es el chico afeminado del grupo',
			2:'aunque no lo acepte, le excita un poco el porno gay',
			1:'hombre heterosexual promedio',
			0:'le dan asco los hombres'
		}[percent//10]
		embed = discord.Embed(
			title='Medidor gamer de homosexualidad',
			description=f'{username} es un {percent}% gay, {extra}.',
			colour=db.default_color(interaction)
		)
		await interaction.response.send_message(embed=embed)


	# tictactoe
	tictactoe_group = app_commands.Group(
		name='tictactoe',
		description='Juega una partida de Tic Tac Toe contra la máquina o contra otra persona'
	)


	#tictactoe against-machine
	@tictactoe_group.command(name='against-machine')
	@app_commands.checks.cooldown(1, 15)
	async def against_machine(self, interaction: discord.Interaction):
		"""Juega una partida de Tic Tac Toe contra la máquina"""
		game = ttt.TicTacToe(interaction, interaction.user, interaction.guild.me)
		await interaction.response.send_message(game.get_content(), view=game)


	#tictactoe against-player
	@tictactoe_group.command(name='against-player')
	@app_commands.checks.cooldown(1, 15)
	@app_commands.rename(opponent='oponente')
	async def against_player(self, interaction: discord.Interaction, opponent: discord.Member | None):
		"""Juega una partida de Tic tac Toe contra otra persona

		opponent
			Usuario contra el que quieres jugar
		"""
		if opponent is None:
			join_view = ttt.JoinView(interaction)
			await interaction.response.send_message(core.Warning.searching(f'**{interaction.user.name}** está buscando un oponente para jugar Tic Tac Toe'), view=join_view)
			await join_view.wait()

			if join_view.user is None:
				return

			else:
				opponent = join_view.user
				await join_view.interaction.response.defer()

		else:
			if opponent.bot:
				await interaction.response.send_message(core.Warning.error('No puedes jugar contra un bot'), ephemeral=True)
				return
			ask_view = core.Confirm(interaction, opponent)
			ask_string = f'{opponent.mention} ¿Quieres unirte a la partida de Tic Tac Toe de **{interaction.user.name}**?' if opponent.id != interaction.user.id else f'¿Estás tratando de jugar contra ti mismo?'
			await interaction.response.send_message(ask_string, view=ask_view)
			await ask_view.wait()

			if ask_view.value is None:
				return
			
			elif not ask_view.value:
				await ask_view.last_interaction.response.edit_message(content=core.Warning.cancel('La partida fue rechazada'), view=ask_view)
				return

			else:
				await ask_view.last_interaction.response.defer()

		game = ttt.TicTacToe(interaction, interaction.user, opponent)
		await interaction.edit_original_response(content=game.get_content(), view=game)


	# 8ball
	@app_commands.command(name='8ball')
	@app_commands.checks.cooldown(1, 2.5)
	@app_commands.rename(question='pregunta')
	async def _8ball(self, interaction: discord.Interaction, question: str):
		"""Pregúntale algo al bot para que te dé su opinión

		question
			Pregunta que el bot responderá
		"""
		await interaction.response.send_message(embed=core.embed_author(
			user=interaction.user, 
			embed=discord.Embed(
				title='8ball',
				description=question,
				colour=db.default_color(interaction)
			).add_field(
				name='Respuesta',
				value=choice((
					'Sí', 'No', 'En efecto', 'Quizás', 'Mañana', 'Imposible',
					'El simple hecho de que consideraras que eso podría ser cierto es un insulto hacia la inteligencia humana',
					'¿No era obvio que sí?', 'Está científicamente comprobado que sí',
					'No, imbécil', 'Es muy probable', 'Es casi imposible', 'Para nada',
					'Totalmente', 'No lo sé', 'h', 'No lo sé, busca en Google',
					f'No lo sé, preguntale a {choice(list(filter(lambda x: not x.bot, interaction.guild.members))).mention}'
				))
			)
		))



async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Fun(bot), guilds=core.bot_guilds)
