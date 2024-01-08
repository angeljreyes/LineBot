from datetime import datetime
from time import perf_counter
from platform import platform, python_version

import discord
from discord import app_commands
from discord.ext import commands
from cpuinfo import get_cpu_info
from psutil import Process, virtual_memory, cpu_percent

import core
import pagination
import db
import autocomplete


class About(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		# self.send = bot.get_cog('GlobalCog').send


	# ping
	@app_commands.command(name='ping')
	async def _ping(self, interaction: discord.Interaction):
		"""Muestra en milisegundos lo que tarda el bot en enviar un mensaje desde que mandaste el comando"""
		content = core.Warning.info('Pong!')[:-1]
		counter_start = perf_counter()
		await interaction.response.send_message(content)
		counter_stop = perf_counter()
		ping = round((counter_stop - counter_start) * 1000)
		await interaction.edit_original_response(content=f'{content} El ping es de **{ping} ms**.')


	# links
	@app_commands.command()
	async def links(self, interaction: discord.Interaction):
		"""Obtén los links oficiales del bot"""
		# emb = discord.Embed(title='Links', colour=db.default_color(interaction))
		# for link in core.links:
		# 	emb.add_field(name=link, value=f'[Aquí]({core.links[link]})')
		view = discord.ui.View()
		for link in core.links:
			view.add_item(discord.ui.Button(label=link, url=core.links[link]))
		await interaction.response.send_message(view=view)


	#changelog
	@app_commands.command()
	@app_commands.autocomplete(version=autocomplete.changelog)
	@app_commands.checks.cooldown(1, 3.0)
	@app_commands.rename(version='versión')
	async def changelog(self, interaction: discord.Interaction, version: str = core.bot_version):
		"""Revisa el registro de cambios de la última versión del bot o de una especificada

		version: str
			Una versión de Line Bot
		"""
		if version == 'list':
			# Selects released versions if the bot is stable and all versions if it's dev
			sql = {'stable':"SELECT VERSION FROM CHANGELOG WHERE HIDDEN=0", 'dev':"SELECT VERSION FROM CHANGELOG"}[core.bot_mode]
			db.cursor.execute(sql)
			versions = db.cursor.fetchall()
			db.conn.commit()
			versions.reverse()
			embed = discord.Embed(title='Changelog', colour=db.default_color(interaction))
			version_list = ', '.join([f'`{version[0]}`' for version in versions])
			embed.add_field(name='Lista de versiones:', value=version_list)
			embed.set_footer(text=f'Cantidad de versiones: {len(versions)}')
			await interaction.response.send_message(embed=embed)

		else:
			db.cursor.execute(f"SELECT * FROM CHANGELOG WHERE VERSION=?", (version,))
			try:
				summary = db.cursor.fetchall()[0]
			except IndexError:
				await interaction.response.send_message(core.Warning.error('Versión inválida'), ephemeral=True)
				return
			db.conn.commit()
			embed = discord.Embed(title=f'Versión {summary[0]} - {summary[1]}', description=summary[2], colour=db.default_color(interaction))
			await interaction.response.send_message(embed=embed)


	# color
	@app_commands.command()
	@app_commands.autocomplete(value=autocomplete.color)
	@app_commands.checks.cooldown(1, 3)
	@app_commands.rename(value='valor')
	async def color(self, interaction: discord.Interaction, value: str = ''):
		"""Cambia el color de los embeds del bot

		value: str
			Elige un color de la lista o escribe un #hex o rgb(r, g ,b)
		"""
		if value == '':
			embed = discord.Embed(description=':arrow_left: Este es tu color actual', colour=db.default_color(interaction))
			await interaction.response.send_message(embed=embed, ephemeral=True)
			return

		elif value == 'default':
			db.cursor.execute(f"DELETE FROM COLORS WHERE ID={interaction.user.id}")
			await interaction.response.send_message(embed=discord.Embed(description=core.Warning.success('El color ha sido reestablecido'), colour=db.default_color(interaction)), ephemeral=True)

		else:
			if value == 'random':
				new_value = 0
			else:
				try:
					new_value = (await commands.ColourConverter().convert(interaction, value)).value
				except:
					await interaction.response.send_message(core.Warning.error(f'Selecciona un color válido, escribe un código hex `#00ffaa`, rgb `rgb(123, 123, 123)` o selecciona "Color por defecto" para reestablecer el color al del rol del bot'), ephemeral=True)
					return

			db.cursor.execute(f"SELECT ID FROM COLORS WHERE ID={interaction.user.id}")
			check = db.cursor.fetchall()
			# Check if the user is registered in the database or not
			if check == []:
				db.cursor.execute(f"INSERT INTO COLORS VALUES({interaction.user.id}, ?)", (new_value,))
			else:
				db.cursor.execute(f"UPDATE COLORS SET VALUE=? WHERE ID={interaction.user.id}", (new_value,))
			embed = discord.Embed(description=core.Warning.success(f'El color ha sido cambiado a **{value}**'), colour=db.default_color(interaction))
			await interaction.response.send_message(embed=embed, ephemeral=True)

		db.conn.commit()



	# stats
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5.0)
	async def stats(self, interaction: discord.Interaction):
		"""Muestra información sobre el bot"""
		embed = discord.Embed(title='Información de Line Bot', colour=db.default_color(interaction))
		embed.add_field(name='Sistema operativo', value=platform(aliased=True, terse=True))
		embed.add_field(name='\u200b', value='\u200b')
		embed.add_field(name='CPU', value=get_cpu_info()['brand_raw'])
		embed.add_field(name='Uso de CPU', value=f'{Process().cpu_percent()}% / {cpu_percent()}%')
		embed.add_field(name='\u200b', value='\u200b')
		embed.add_field(name='Uso de RAM', value=f'{Process().memory_info().vms//1000000} MB / {virtual_memory().used//1000000} MB / {virtual_memory().total//1000000} MB')
		embed.add_field(name='Librería', value=f'Discord.py {discord.__version__}')
		embed.add_field(name='\u200b', value='\u200b')
		embed.add_field(name='Versión de Python', value='Python ' + python_version())
		embed.add_field(name='Cantidad de servidores', value=len(self.bot.guilds))
		embed.add_field(name='\u200b', value='\u200b')
		embed.add_field(name='Cantidad de usuarios', value=len(self.bot.users))
		embed.add_field(name='Uptime', value=core.fix_delta(datetime.utcnow() - core.bot_ready_at))
		embed.add_field(name='\u200b', value='\u200b')
		embed.add_field(name='Dueño del bot', value=str(self.bot.get_user(self.bot.owner_id)))
		view = discord.ui.View()
		for link in core.links:
			view.add_item(discord.ui.Button(label=link, url=core.links[link]))
		await interaction.response.send_message(embed=embed, view=view)


	# commandstats
	@app_commands.command()
	@app_commands.autocomplete(command=autocomplete.commandstats)
	@app_commands.checks.cooldown(1, 10.0)
	@app_commands.rename(command='comando')
	async def commandstats(self, interaction: discord.Interaction, command: str | None):
		"""Muestra cuáles son los comandos más usados y cuántas veces se han

		command: str
			Un comando del bot
		"""
		if command is None:
			# Send all the commands and their uses
			db.cursor.execute("SELECT * FROM COMMANDSTATS")
			stats = db.cursor.fetchall()
			stats.sort(key=lambda x: x[1], reverse=True)
			fstats = list(map(lambda x: f'`{x[0]}` - {x[1]}', stats))
			pages = pagination.Page.from_list(interaction, 'Comandos más usados (Desde 27/06/2020)', fstats)
			paginator = pagination.Paginator(interaction, pages=pages, entries=len(fstats))
			await interaction.response.send_message(embed=pages[0].embed, view=paginator)

		else:
			# Checks if the command exists
			db.cursor.execute("SELECT * FROM COMMANDSTATS WHERE COMMAND=?", (command,))
			stats = db.cursor.fetchall()
			if stats == []:
				await interaction.response.send_message(core.Warning.error('El comando que escribiste no existe o no se ha usado'), ephemeral=True)

			else:
				stats = stats[0]
				await interaction.response.send_message(core.Warning.info(f'`{stats[0]}` se ha usado {stats[1]} {"veces" if stats[1] != 1 else "vez"}'))		
		db.conn.commit()


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(About(bot), guilds=core.bot_guilds)
