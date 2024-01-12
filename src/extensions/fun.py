import requests
from random import choice, randint
from urllib.parse import quote

import discord
from discord import app_commands
from discord.ext import commands

import core
import tictactoe as ttt
import db


class Fun(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.DADJOKE_BASE_URL = 'https://icanhazdadjoke.com/'
		self.DADJOKE_HEADERS = {'Accept': 'application/json'}


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
	dadjoke_group = app_commands.Group(
		name='dadjoke',
		description='Envía chistes que dan menos risa que los de Siri'
	)


	async def send_dadjoke(
			self,
			interaction: discord.Interaction,
			*,
			joke: str,
			joke_id: str,
			status: int,
			is_image: bool
		) -> None:
		if status != 200:
			await interaction.response.send_message(
				core.Warning.error(f'Hubo un error con [la API]({self.DADJOKE_BASE_URL}) :('),
				ephemeral=True
			)
			return

		embed = (discord.Embed(
			title='Dad joke',
			colour=db.default_color(interaction)
		)
			.set_footer(text=f'Joke ID: {joke_id}'))

		if is_image:
			image_url = f'{self.DADJOKE_BASE_URL}j/{joke_id}.png'
			embed.set_image(url=image_url)
		else:
			embed.description = joke

		await interaction.response.send_message(embed=embed)


	# dadjoke random
	@dadjoke_group.command(name='random')
	@app_commands.checks.cooldown(1, 5.0)
	@app_commands.rename(is_image='imagen')
	async def dadjoke_random(self, interaction: discord.Interaction, is_image: bool = False):
		"""Mostrar un chiste random
		
		is_image
			Mostrar el chiste como imagen
		"""
		request: dict = requests.get(
			self.DADJOKE_BASE_URL,
			headers=self.DADJOKE_HEADERS
		).json()

		await self.send_dadjoke(
			interaction,
			joke=request['joke'],
			joke_id=request['id'],
			status=request['status'],
			is_image=is_image
		)


	# dadjoke search
	@dadjoke_group.command(name='search')
	@app_commands.checks.cooldown(1, 5.0)
	@app_commands.rename(query='búsqueda', is_image='imagen')
	async def dadjoke_search(
			self,
			interaction: discord.Interaction,
			query: str,
			is_image: bool = False
		):
		"""Buscar un chiste por su contenido
		
		query
			Busca un chiste que contenga esta búsqueda
		is_image
			Mostrar el chiste como imagen
		"""
		request: dict = requests.get(
			f'{self.DADJOKE_BASE_URL}search',
			params={'term': query},
			headers=self.DADJOKE_HEADERS
		).json()

		if not request.get('results', None):
			await interaction.response.send_message(
				core.Warning.error('No se encontraron resultados'),
				ephemeral=True
			)
			return

		result: dict = request['results'][0]
		await self.send_dadjoke(
			interaction,
			joke=result['joke'],
			joke_id=result['id'],
			status=request['status'],
			is_image=is_image
		)


	# dadjoke fetch
	@dadjoke_group.command(name='fetch')
	@app_commands.checks.cooldown(1, 5.0)
	@app_commands.rename(joke_id='id', is_image='imagen')
	async def dadjoke_fetch(
			self,
			interaction: discord.Interaction,
			joke_id: str,
			is_image: bool = False
		):
		"""Buscar un chiste por su ID
		
		joke_id
			ID del chiste que quieres buscar
		is_image
			Mostrar el chiste como imagen
		"""
		request: dict = requests.get(
			f'{self.DADJOKE_BASE_URL}j/{quote(joke_id)}',
			headers=self.DADJOKE_HEADERS
		).json()

		if 'id' not in request:
			await interaction.response.send_message(
				core.Warning.error('ID inválida'),
				ephemeral=True
			)
			return

		await self.send_dadjoke(
			interaction,
			joke=request['joke'],
			joke_id=request['id'],
			status=request['status'],
			is_image=is_image
		)


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
			10: 'se le cayó el pene',
			9: 'le dan asco las mujeres',
			8: 'se corre al pensar en hombres',
			7: 'le encanta chupar piroca',
			6: 'está pensando en penes ahora mismo',
			5: 'es bisexual, re normie',
			4: 'seguro está enamorado de su mejor amigo',
			3: 'es el chico afeminado del grupo',
			2: 'aunque no lo acepte, le excita un poco el porno gay',
			1: 'hombre heterosexual promedio',
			0: 'le dan asco los hombres'
		}[percent//10]
		embed = discord.Embed(
			title='Medidor de homosexualidad',
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
