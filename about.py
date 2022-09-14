import asyncio
from datetime import datetime

import discord
from discord.ext import commands
from psutil import Process, virtual_memory, cpu_percent

import botdata
import helpsys


class About(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.send = bot.get_cog('GlobalCog').send


	# help
	@commands.cooldown(1, 1.5, commands.BucketType.user)
	@commands.command(name='help')
	async def _help(self, ctx, command=None):
		if command == None:
			emb = helpsys.get_all(ctx)
			await self.send(ctx, embed=emb)
		elif self.bot.get_command(command) in self.bot.commands:
			command = self.bot.get_command(command)
			emb = helpsys.get_cmd(ctx, command.name)
			await self.send(ctx, embed=emb)
		else:
			await self.send(ctx, botdata.Warning.error(f'El comando **{await commands.clean_content().convert(ctx, command)}** no existe'))
			ctx.command.reset_cooldown(ctx)


	# ping
	@commands.command(name='ping')
	async def _ping(self, ctx):
		content = botdata.Warning.info('El ping es de')[:-1]
		msg = await self.send(ctx, content)
		ping = (ctx.message.created_at - msg.created_at).microseconds // 1000
		await msg.edit(content=content + f' **{ping} ms**.')


	# uptime
	@commands.command()
	async def uptime(self, ctx):
		delta = botdata.fix_delta(datetime.utcnow() - self.bot.get_cog('GlobalCog').ready_at)
		await self.send(ctx, botdata.Warning.info(f'Online por **{delta}**'))


	# links
	@commands.command(aliases=('invite', 'vote'))
	async def links(self, ctx):
		emb = discord.Embed(title='Links', colour=botdata.default_color(ctx))
		for link in botdata.links:
			emb.add_field(name=link, value=f'[Aquí]({botdata.links[link]})')
		await self.send(ctx, embed=emb)


	#prefix
	@commands.cooldown(1, 5.0, commands.BucketType.guild)
	@commands.command(aliases=['lineprefix'])
	@commands.guild_only()
	async def prefix(self, ctx, prefix=None):
		if not ctx.message.author.permissions_in(ctx.channel).manage_guild:
			await self.send(ctx, botdata.Warning.error('Necesitas permiso de administrador para cambiar el prefijo del servidor'))
			ctx.command.reset_cooldown(ctx)

		else:
			if prefix == None:
				await self.send(ctx, embed=helpsys.get_cmd(ctx, 'prefix'))
				return

			elif len(prefix) > 16:
				await self.send(ctx, botdata.Warning.error('El límite de carácteres de un prefijo es 16'))
				ctx.command.reset_cooldown(ctx)
				return

			elif prefix == botdata.default_prefix:
				botdata.cursor.execute(f"DELETE FROM {botdata.prefix_table} WHERE ID={ctx.guild.id}")

			else:
				botdata.cursor.execute(f"SELECT PREFIX FROM {botdata.prefix_table} WHERE ID={ctx.guild.id}")
				check = botdata.cursor.fetchall()
				if check == []:
					botdata.cursor.execute(f"INSERT INTO {botdata.prefix_table} VALUES({ctx.guild.id},?)", (prefix,))
				else:
					botdata.cursor.execute(f"UPDATE {botdata.prefix_table} SET PREFIX=? WHERE ID={ctx.guild.id}", (prefix,))

			botdata.conn.commit()
			del self.bot.get_cog('GlobalCog').cached_prefixes[ctx.guild.id]
			await self.send(ctx, botdata.Warning.success(f'El prefijo ha sido actualizado correctamente a `{await commands.clean_content().convert(ctx, prefix)}`'))


	#changelog
	@commands.cooldown(1, 3.0, commands.BucketType.user)
	@commands.command(aliases=['release', 'version'])
	async def changelog(self, ctx, version=None):
		title = 'Changelog'
		sql = {'stable':"SELECT VERSION FROM CHANGELOG WHERE HIDDEN=0", 'dev':"SELECT VERSION FROM CHANGELOG"}[botdata.bot_mode]
		
		if version == 'list':
			botdata.cursor.execute(sql)
			versions = botdata.cursor.fetchall()
			botdata.conn.commit()
			versions.reverse()
			embed = discord.Embed(title='Changelog', colour=botdata.default_color(ctx))
			version_list = ', '.join([f'`{version[0]}`' for version in versions])
			embed.add_field(name='Lista de versiones:', value=version_list)
			embed.set_footer(text=f'Cantidad de versiones: {len(versions)}')
			await self.send(ctx, embed=embed)

		else:
			if version == None:
				botdata.cursor.execute(f"SELECT * FROM CHANGELOG WHERE VERSION='{botdata.bot_version}'")
				summary = botdata.cursor.fetchall()[0]
			else:
				botdata.cursor.execute(sql)
				versions = botdata.cursor.fetchall()
				botdata.conn.commit()
				if (version,) in versions:
					botdata.cursor.execute(f"SELECT * FROM CHANGELOG WHERE VERSION=?", (version,))
					summary = botdata.cursor.fetchall()[0]
				else:
					await self.send(ctx, botdata.Warning.error('Versión inválida'))
					ctx.command.reset_cooldown(ctx)
					return
			botdata.conn.commit()
			embed = discord.Embed(title=f'Versión {summary[0]} - {summary[1]}', description=summary[2], colour=botdata.default_color(ctx))
			embed.set_footer(text=f'Escribe "{ctx.prefix}changelog list" para ver la lista de versiones')
			await self.send(ctx, embed=embed)


	# color
	@commands.cooldown(1, 1.5, commands.BucketType.user)
	@commands.command()
	async def color(self, ctx, *, value=None):

		if value == 'list':
			color_string = ''
			for color in botdata.colors:
				color_string += f'- {color}\n'
			color_embed = discord.Embed(title='Colores disponibles', description=color_string, colour=botdata.default_color(ctx))
			await self.send(ctx, embed=color_embed)

		elif value == 'default':
			botdata.cursor.execute(f"DELETE FROM COLORS WHERE ID={ctx.message.author.id}")
			await self.send(ctx, botdata.Warning.success('El color ha sido reestablecido'))

		else:
			if value == 'random':
				new_value = 0
			else:
				try:
					new_value = (await commands.ColourConverter().convert(ctx, value)).value
				except:
					await self.send(ctx, botdata.Warning.error(f'Introduce un color válido, un código hex o `default` para reestablecer el color al del rol del bot. Usa `{ctx.prefix}color list` para ver los colores válidos'))
					ctx.command.reset_cooldown(ctx)
					return

			botdata.cursor.execute(f"SELECT ID FROM COLORS WHERE ID={ctx.message.author.id}")
			check = botdata.cursor.fetchall()
			if check == []:
				botdata.cursor.execute(f"INSERT INTO COLORS VALUES({ctx.message.author.id}, ?)", (new_value,))
			else:
				botdata.cursor.execute(f"UPDATE COLORS SET VALUE=? WHERE ID={ctx.message.author.id}", (new_value,))
			await self.send(ctx, botdata.Warning.success(f'El color ha sido cambiado a **{value}**'))

		botdata.conn.commit()


	# botinfo
	@commands.cooldown(1, 3.0, commands.BucketType.user)
	@commands.command(aliases=['stats'])
	async def botinfo(self, ctx):
		embed = discord.Embed(title='Información del bot', colour=botdata.default_color(ctx))
		data_dict = {
			'Librería': f'Discord.py {discord.__version__}',
			'Uso de RAM y CPU': f'RAM: {Process().memory_info().vms//1000000} MB \
/ {virtual_memory().used//1000000/1000} GB / {virtual_memory().total//1000000000} GB\n\
CPU: {Process().cpu_percent()}% / {cpu_percent()}%',
			'Uptime': botdata.fix_delta(datetime.utcnow() - self.bot.get_cog('GlobalCog').ready_at),
			'Cantidad de servidores': len(ctx.bot.guilds),
			'Cantidad de usuarios': len(ctx.bot.users),
			'Dueño del bot': ctx.bot.get_user(ctx.bot.owner_id).mention,
			'Links': ' | '.join((f'[{link}]({botdata.links[link]})' for link in botdata.links))
		}
		embed = botdata.add_fields(embed, data_dict, inline_char=None)
		await self.send(ctx, embed=embed)


	# commandstats
	@commands.cooldown(1, 15.0, commands.BucketType.guild)
	@commands.command(aliases=['commanduses', 'cmdstats', 'cmduses'])
	async def commandstats(self, ctx, command=None):
		if command == None:
			botdata.cursor.execute("SELECT * FROM COMMANDSTATS")
			stats = botdata.cursor.fetchall()
			stats.sort(key=lambda x: x[1], reverse=True)
			fstats = list(map(lambda x: f'`{x[0]}` - {x[1]}', stats))
			pages = botdata.Page.from_list(ctx, 'Comandos más usados (Desde 27/06/2020)', fstats)
			await botdata.NavBar(ctx, pages=pages, entries=len(fstats)).start()

		else:
			botdata.cursor.execute("SELECT * FROM COMMANDSTATS WHERE COMMAND=?", (command,))
			stats = botdata.cursor.fetchall()
			if stats == []:
				await self.send(ctx, botdata.Warning.error('El comando que escribiste no existe o no se ha usado'))

			else:
				stats = stats[0]
				await self.send(ctx, botdata.Warning.info(f'`{stats[0]}` se ha usado {stats[1]} {"veces" if stats[1] != 1 else "vez"}'))
			
			ctx.command.reset_cooldown(ctx)
		
		botdata.conn.commit()


def setup(bot):
	bot.add_cog(About(bot))
