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
		view = discord.ui.View()
		for label, link in core.links.items():
			if link:
				view.add_item(discord.ui.Button(label=label, url=link))
			
		if view.children:
			await interaction.response.send_message(view=view)
		else:
			await interaction.response.send_message('No hay links :(')


	#changelog
	@app_commands.command()
	@app_commands.autocomplete(version=autocomplete.changelog)
	@app_commands.checks.cooldown(1, 3.0)
	@app_commands.rename(version='versión')
	async def changelog(self, interaction: discord.Interaction, version: str = core.bot_version):
		"""Revisa el registro de cambios de la última versión del bot o de una especificada

		version
			Una versión de Line Bot
		"""
		if version == 'list':
			version_list = ', '.join([f'`{version}`' for version in core.cached_versions])
			embed = (discord.Embed(title='Changelog', colour=db.default_color(interaction))
				.add_field(name='Lista de versiones:', value=version_list)
				.set_footer(text=f'Cantidad de versiones: {len(core.cached_versions)}'))
			await interaction.response.send_message(embed=embed)

		else:
			db.cursor.execute("SELECT * FROM changelog WHERE version=?", (version,))
			summary: tuple[str, str, str, int] | None = db.cursor.fetchone()
			if summary is None:
				await interaction.response.send_message(core.Warning.error('Versión inválida'), ephemeral=True)
				return

			name, date, content, _ = summary
			embed = discord.Embed(
				title=f'Versión {name} - {date}',
				description=content,
				colour=db.default_color(interaction)
			)
			await interaction.response.send_message(embed=embed)


	# color
	@app_commands.command()
	@app_commands.autocomplete(value=autocomplete.color)
	@app_commands.checks.cooldown(1, 3)
	@app_commands.rename(value='valor')
	async def color(self, interaction: discord.Interaction, value: str = ''):
		"""Cambia el color de los embeds del bot

		value
			Elige un color de la lista o escribe un #hex o rgb(r, g ,b)
		"""
		if value == '':
			embed = discord.Embed(
				description=':arrow_left: Este es tu color actual',
				colour=db.default_color(interaction)
			)
			await interaction.response.send_message(embed=embed, ephemeral=True)
			return

		if value == 'default':
			db.cursor.execute("DELETE FROM colors WHERE id=?", (interaction.user.id,))
			embed = discord.Embed(
				description=core.Warning.success('El color ha sido reestablecido'),
				colour=db.default_color(interaction)
			)
			await interaction.response.send_message(embed=embed, ephemeral=True)
			db.conn.commit()
			return

		if value == 'random':
			new_value = 0
		else:
			try:
				new_value = (await commands.ColourConverter().convert(interaction, value)).value
			except (commands.CommandError, commands.BadArgument):
				await interaction.response.send_message(core.Warning.error(
					'Selecciona un color válido, escribe un código hex `#00ffaa`, '
					'rgb `rgb(123, 123, 123)` o selecciona "Color por defecto" para '
					'reestablecer el color al del rol del bot'
				), ephemeral=True)
				return

		db.cursor.execute("SELECT id FROM colors WHERE id=?", (interaction.user.id,))
		check: tuple[int] | None = db.cursor.fetchone()
		# Check if the user is registered in the database or not
		if check is None:
			db.cursor.execute("INSERT INTO colors VALUES(?, ?)", (interaction.user.id, new_value))
		else:
			db.cursor.execute("UPDATE colors SET value=? WHERE id=?", (new_value, interaction.user.id))

		embed = discord.Embed(
			description=core.Warning.success(f'El color ha sido cambiado a **{value}**'),
			colour=db.default_color(interaction)
		)
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
		embed.add_field(name='Dueño del bot', value=str(self.bot.application.owner))

		view = discord.ui.View()
		for label, link in core.links.items():
			if link:
				view.add_item(discord.ui.Button(label=label, url=link))

		await interaction.response.send_message(embed=embed, view=view)


	# commandstats
	@app_commands.command()
	@app_commands.autocomplete(command=autocomplete.commandstats)
	@app_commands.checks.cooldown(1, 10.0)
	@app_commands.rename(command='comando')
	async def commandstats(self, interaction: discord.Interaction, command: str | None):
		"""Muestra cuáles son los comandos más usados y cuántas veces se han

		command
			Un comando del bot
		"""
		if command is None:
			# Send all the commands and their uses
			db.cursor.execute("SELECT * FROM commandstats ORDER BY uses DESC")
			stats = db.cursor.fetchall()
			if not stats:
				await interaction.response.send_message(
					core.Warning.info('No se encontraron comandos')
				)
				return

			paginator = pagination.Paginator.optional(interaction, pages=pages, entries=len(f_stats))
			await interaction.response.send_message(embed=pages[0].embed, view=paginator)

		else:
			# Checks if the command exists
			db.cursor.execute("SELECT * FROM commandstats WHERE command=?", (command,))
			stats: tuple[str, int] | None = db.cursor.fetchone()

			if stats is None:
				await interaction.response.send_message(core.Warning.error('El comando que escribiste no existe o no se ha usado'), ephemeral=True)
				return

			command_name, uses = stats
			await interaction.response.send_message(core.Warning.info(f'`/{command_name}` se ha usado {uses} {"veces" if stats[1] != 1 else "vez"}'))		


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(About(bot), guilds=core.bot_guilds)
