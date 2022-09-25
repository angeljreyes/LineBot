import asyncio
from datetime import datetime
from time import perf_counter
from platform import platform, python_version
from cpuinfo import get_cpu_info

import discord
from discord import app_commands
from discord.ext import commands
from psutil import Process, virtual_memory, cpu_percent

import core


class About(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		# self.send = bot.get_cog('GlobalCog').send


	# ping
	@app_commands.command(name='ping')
	async def _ping(self, interaction: discord.Interaction):
		content = core.Warning.info('Pong!')[:-1]
		counter_start = perf_counter()
		await interaction.response.send_message(content)
		counter_stop = perf_counter()
		ping = round((counter_stop - counter_start) * 1000)
		await interaction.edit_original_response(content=f'{content} El ping es de **{ping} ms**.')


	# links
	@app_commands.command()
	async def links(self, interaction: discord.Interaction):
		# emb = discord.Embed(title='Links', colour=core.default_color(interaction))
		# for link in core.links:
		# 	emb.add_field(name=link, value=f'[Aquí]({core.links[link]})')
		view = discord.ui.View()
		for link in core.links:
			view.add_item(discord.ui.Button(label=link, url=core.links[link]))
		await interaction.response.send_message(view=view)


	#changelog
	@app_commands.command()
	@app_commands.autocomplete(version=core.changelog_autocomplete)
	@app_commands.checks.cooldown(1, 3.0)
	@app_commands.rename(version='versión')
	async def changelog(self, interaction: discord.Interaction, version: str = core.bot_version):
		"""
		version: str
			Una versión de Line Bot
		"""
		if version == 'list':
			# Selects released versions if the bot is stable and all versions if it's dev
			sql = {'stable':"SELECT VERSION FROM CHANGELOG WHERE HIDDEN=0", 'dev':"SELECT VERSION FROM CHANGELOG"}[core.bot_mode]
			core.cursor.execute(sql)
			versions = core.cursor.fetchall()
			core.conn.commit()
			versions.reverse()
			embed = discord.Embed(title='Changelog', colour=core.default_color(interaction))
			version_list = ', '.join([f'`{version[0]}`' for version in versions])
			embed.add_field(name='Lista de versiones:', value=version_list)
			embed.set_footer(text=f'Cantidad de versiones: {len(versions)}')
			await interaction.response.send_message(embed=embed)

		else:
			core.cursor.execute(f"SELECT * FROM CHANGELOG WHERE VERSION=?", (version,))
			try:
				summary = core.cursor.fetchall()[0]
			except IndexError:
				await interaction.response.send_message(core.Warning.error('Versión inválida'), ephemeral=True)
				return
			core.conn.commit()
			embed = discord.Embed(title=f'Versión {summary[0]} - {summary[1]}', description=summary[2], colour=core.default_color(interaction))
			await interaction.response.send_message(embed=embed)


	# color
	@app_commands.command()
	@app_commands.autocomplete(value=core.color_autocomplete)
	@app_commands.checks.cooldown(1, 3)
	@app_commands.rename(value='valor')
	async def color(self, interaction: discord.Interaction, value: str = ''):
		"""
		value: str
			Elige un color de la lista o escribe un #hex o rgb(r, g ,b)
		"""
		if value == '':
			embed = discord.Embed(description=':arrow_left: Este es tu color actual', colour=core.default_color(interaction))
			await interaction.response.send_message(embed=embed, ephemeral=True)
			return

		elif value == 'default':
			core.cursor.execute(f"DELETE FROM COLORS WHERE ID={interaction.user.id}")
			await interaction.response.send_message(embed=discord.Embed(description=core.Warning.success('El color ha sido reestablecido'), colour=core.default_color(interaction)), ephemeral=True)

		else:
			if value == 'random':
				new_value = 0
			else:
				try:
					new_value = (await commands.ColourConverter().convert(interaction, value)).value
				except:
					await interaction.response.send_message(core.Warning.error(f'Selecciona un color válido, escribe un código hex `#00ffaa`, rgb `rgb(123, 123, 123)` o selecciona "Color por defecto" para reestablecer el color al del rol del bot'), ephemeral=True)
					return

			core.cursor.execute(f"SELECT ID FROM COLORS WHERE ID={interaction.user.id}")
			check = core.cursor.fetchall()
			# Check if the user is registered in the database or not
			if check == []:
				core.cursor.execute(f"INSERT INTO COLORS VALUES({interaction.user.id}, ?)", (new_value,))
			else:
				core.cursor.execute(f"UPDATE COLORS SET VALUE=? WHERE ID={interaction.user.id}", (new_value,))
			embed = discord.Embed(description=core.Warning.success(f'El color ha sido cambiado a **{value}**'), colour=core.default_color(interaction))
			await interaction.response.send_message(embed=embed, ephemeral=True)

		core.conn.commit()



	# stats
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5.0)
	async def stats(self, interaction):
		embed = discord.Embed(title='Información de Line Bot', colour=core.default_color(interaction))
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
	@app_commands.autocomplete(command=core.commandstats_command_autocomplete)
	@app_commands.checks.cooldown(1, 10.0)
	@app_commands.rename(command='comando')
	async def commandstats(self, interaction, command: str = None):
		"""
		command: str
			Un comando del bot
		"""
		if command == None:
			# Send all the commands and their uses
			core.cursor.execute("SELECT * FROM COMMANDSTATS")
			stats = core.cursor.fetchall()
			stats.sort(key=lambda x: x[1], reverse=True)
			fstats = list(map(lambda x: f'`{x[0]}` - {x[1]}', stats))
			pages = core.Page.from_list(interaction, 'Comandos más usados (Desde 27/06/2020)', fstats)
			paginator = core.Paginator(interaction, pages=pages, entries=len(fstats))
			await interaction.response.send_message(embed=pages[0].embed, view=paginator)

		else:
			# Checks if the command exists
			core.cursor.execute("SELECT * FROM COMMANDSTATS WHERE COMMAND=?", (command,))
			stats = core.cursor.fetchall()
			if stats == []:
				await interaction.response.send_message(core.Warning.error('El comando que escribiste no existe o no se ha usado'), ephemeral=True)

			else:
				stats = stats[0]
				await interaction.response.send_message(core.Warning.info(f'`{stats[0]}` se ha usado {stats[1]} {"veces" if stats[1] != 1 else "vez"}'))		
		core.conn.commit()


async def setup(bot):
	await bot.add_cog(About(bot), guild=core.bot_guild)
