import asyncio
import exceptions
import re
from datetime import datetime, timedelta

import discord
from discord.ext import commands

import core
import helpsys
import logging


class Listeners(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.send = bot.get_cog('GlobalCog').send
		
		@bot.before_invoke
		async def typing_check(ctx):
			if not ctx.message.id in self.bot.get_cog('GlobalCog').command_registry:
				try:
					helpsys.descs[ctx.command.name]
				except KeyError:
					pass
				else:
					if helpsys.descs[ctx.command.name].endswith('-s'):
						return
				await ctx.channel.trigger_typing()

	@commands.Cog.listener('on_ready')
	async def ready(self):
		core.logger.info('Bot iniciado')
		await self.bot.change_presence(activity=discord.Game(name=core.default_prefix+'help'))


	@commands.Cog.listener('on_resumed')
	async def resume(self):
		core.logger.info('Sesión resumida')
		await self.bot.change_presence(activity=discord.Game(name=core.default_prefix+'help'))


	@commands.Cog.listener('on_command_error')
	async def error_handler(self, ctx, error):
		error_msg = None
		errors = {
			discord.HTTPException: {
				'Must be 2000 or fewer in length': 'El mensaje supera los 2000 caracteres'
			},
			commands.CommandNotFound: '',
			commands.BadArgument: {
				'Member': 'No se encontró a ese usuario en este servidor',
				'User': 'No se encontró a ese usuario',
				'Role': 'No se encontró ese rol',
				'Channel': 'No se encontró ese canal'
			},
			commands.NotOwner: 'Comando exclusivo del dueño del bot',
			commands.ArgumentParsingError: 'Hiciste un mal uso de las comillas',
			commands.NoPrivateMessage: 'Este comando solo se puede usar en servidores',
			commands.MaxConcurrencyReached: lambda: f'Se alcanzó el límite de usuarios para este comando: `{error.number}{"" if error.per == commands.BucketType.default else f" por {core.bucket_types[error.per]}"}`',
			commands.MissingPermissions: lambda: f'No tienes los permisos requeridos para ejecutar este comando: ' + ', '.join((f'`{perm.replace("_", " ")}`' for perm in error.missing_perms)),
			commands.NSFWChannelRequired: 'Este comando solo se puede usar en canales NSFW',
			commands.CommandInvokeError: {
				'403 Forbidden (error code: 50013): Missing Permissions': 'No tengo los permisos requeridos para ejecutar este comando. Intenta añadirlos editando los permisos o la posición mi rol',
				'Unknown Message': 'El mensaje que se trató de editar/eliminar/reaccionar fue eliminado',
				'Invalid Form Body\nIn content: Must be 2000 or fewer in length': 'El mensaje supera los 2000 caracteres',
				'Invalid Form Body\nIn content: Must be 4000 or fewer in length': 'El mensaje supera los 4000 caracteres',
				'ValueError: Tag name limit reached': 'El límite de caracteres para el nombre un tag es de 32',
				'ValueError: Invalid characters detected': 'El nombre de un tag no puede contener espacios ni caracteres markdown',
				'ValueError: Invalid URL': 'URL inválida'
			},
			exceptions.DisabledTagsError: '',
			exceptions.ExistentTagError: 'Este tag ya existe---',
			exceptions.ImageNotFound: 'No se encontró ninguna imagen en los últimos 30 mensajes',
			exceptions.NonExistentTagError: {
				'This tag': 'Este tag no existe---',
				'This user': 'Este usuario no tiene tags---',
				'This server': 'Este servidor no tiene tags---'
			}
		}
		
		if isinstance(error, exceptions.BlacklistUserError):
			await ctx.author.send(core.Warning.error('Estás en la lista negra. No tienes permitido usar el bot'), delete_after=60)
			return

		elif isinstance(error, commands.CommandOnCooldown):
			retry_after = error.retry_after
			error_msg = f'Tienes que esperar **{core.fix_delta(timedelta(seconds=retry_after), ms=True)}** para ejecutar este comando de nuevo'

		if error_msg == None:
			for exception in errors:
				if isinstance(error, exception):
					if isinstance(errors[exception], dict):
						for string in errors[exception]:
							if string in str(error):
								error_msg = errors[exception][string]
								break
					else:
						error_msg = errors[exception]
						break

		if not isinstance(error_msg, str) and error_msg != None:
			error_msg = error_msg()

		if error_msg == None:
			await self.send(ctx, embed=discord.Embed(
				title=f'Ha ocurrido un error',
				description=f'```py\n{repr(error)}\n```',
				colour=core.default_color(ctx)
			).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url).set_footer(text='Este error ha sido notificado y será investigado para su posterior correción.'))
			raise error

		if error_msg == '':
			return
		else:
			if error_msg.endswith('---'):
				error_msg = error_msg[:-3]
				ctx.command.reset_cooldown(ctx)
			await self.send(ctx, core.Warning.error(error_msg))


	@commands.Cog.listener('on_message')
	async def prefix_help(self, message):
		if message.content.replace('!', '') == f'<@{self.bot.user.id}>' and not message.author.bot:
			try: 
				core.check_blacklist(await self.bot.get_context(message))
				await message.channel.send(core.Warning.info(f'Hola, mi prefijo en este servidor es `{core.get_prefix(self.bot, message, ignore_mention=True)}`'))
			except exceptions.BlacklistUserError:
				await message.author.send(core.Warning.error('Estás en la lista negra. No tienes permitido usar el bot'), delete_after=30)				


	@commands.Cog.listener('on_message_edit')
	async def message_editing(self, before, after):
		used_before = False
		if before.id in self.bot.get_cog('GlobalCog').command_registry:
			used_before = self.bot.get_cog('GlobalCog').command_registry[before.id].edited_at
			if used_before == None:
				used_before = self.bot.get_cog('GlobalCog').command_registry[before.id].created_at
		await self.bot.process_commands(after)
		if before.id in self.bot.get_cog('GlobalCog').command_registry:
			used_after = self.bot.get_cog('GlobalCog').command_registry[before.id].edited_at
			if used_after == None:
				used_after = self.bot.get_cog('GlobalCog').command_registry[before.id].created_at


	@commands.Cog.listener('on_message_delete')
	async def message_delete(self, message):
		if message.id in self.bot.get_cog('GlobalCog').command_registry:
			del self.bot.get_cog('GlobalCog').command_registry[message.id]


	@commands.Cog.listener('on_command')
	async def command_logging(self, ctx):
		core.logger.info(f'Se he usado un comando: "{ctx.message.content}" {repr(ctx.message)}')

		if core.bot_mode == 'stable' and not ctx.command_failed:
			core.cursor.execute(f"SELECT * FROM COMMANDSTATS WHERE COMMAND='{ctx.command.name}'")
			command = core.cursor.fetchall()
			if command == []:
				core.cursor.execute(f"INSERT INTO COMMANDSTATS VALUES('{ctx.command.name}', 1)")

			else:
				core.cursor.execute(f"UPDATE COMMANDSTATS SET USES={command[0][1] + 1} WHERE COMMAND='{command[0][0]}'")

			core.conn.commit()


	# @commands.Cog.listener('on_guild_join')
	# async def guild_join_logging(self, guild):
	# 	botdata.logger.info(f'El bot ha entrado a un servidor: {repr(guild)}')


	@commands.Cog.listener('on_guild_remove')
	async def guild_join_logging(self, guild):
		core.logger.info(f'El bot ha salido de un servidor: {repr(guild)}')


def setup(bot):
	bot.add_cog(Listeners(bot))
