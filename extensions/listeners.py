import asyncio
import exceptions
import re
from datetime import datetime, timedelta

import discord
from discord.ext import commands

import core
import logging


class Listeners(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.Cog.listener('on_ready')
	async def ready(self):
		core.logger.info('Bot iniciado')


	@commands.Cog.listener('on_resumed')
	async def resume(self):
		core.logger.info('Sesión resumida')


	@commands.Cog.listener('on_command_error')
	async def error_handler(self, ctx, error):
		error_msg = None
		# An error object and its error message
		error_messages = {
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
			# Sometimes CommandInvokeError is raised, so the error is
			# identified by the first characters of the exception string
			commands.CommandInvokeError: {
				'403 Forbidden (error code: 50013): Missing Permissions': 'No tengo los permisos requeridos para ejecutar este comando. Intenta añadirlos editando los permisos o la posición mi rol',
				'Unknown Message': 'El mensaje que se trató de editar/eliminar/reaccionar fue eliminado',
				'Invalid Form Body\nIn content: Must be 2000 or fewer in length': 'El mensaje supera los 2000 caracteres',
				'Invalid Form Body\nIn content: Must be 4000 or fewer in length': 'El mensaje supera los 4000 caracteres',
				'ValueError: Tag name limit reached': 'El límite de caracteres para el nombre un tag es de 32',
				'ValueError: Invalid characters detected': 'El nombre de un tag no puede contener espacios ni caracteres markdown',
				'ValueError: Invalid URL': 'URL inválida'
			},
			# Custom exceptions
			exceptions.DisabledTagsError: '',
			exceptions.ExistentTagError: 'Este tag ya existe---',
			exceptions.ImageNotFound: 'No se encontró ninguna imagen en los últimos 30 mensajes',
			exceptions.NonExistentTagError: {
				'This tag': 'Este tag no existe---',
				'This user': 'Este usuario no tiene tags---',
				'This server': 'Este servidor no tiene tags---'
			}
		}
		
		# If the error is a blacklist or cooldown error...
		if isinstance(error, exceptions.BlacklistUserError):
			await ctx.author.send(core.Warning.error('Estás en la lista negra. No tienes permitido usar el bot'), delete_after=60)
			return
		elif isinstance(error, commands.CommandOnCooldown):
			retry_after = error.retry_after
			error_msg = f'Tienes que esperar **{core.fix_delta(timedelta(seconds=retry_after), ms=True)}** para ejecutar este comando de nuevo'

		# If the error message hasn't been determined yet
		if error_msg == None:
			# Check if the error type is in the error_messages list
			for exception_type in error_messages:
				if isinstance(error, exception_type):
					# Check if the error message is a dict (is variable)
					if isinstance(error_messages[exception_type], dict):
						for string in error_messages[exception_type]:
							if string in str(error):
								error_msg = error_messages[exception_type][string]
								break
					else:
						error_msg = error_messages[exception_type]
						break

		# If error_msg is a lambda function, run it
		if not isinstance(error_msg, str) and error_msg != None:
			error_msg = error_msg()

		# If the error remains unidentified, send a generic error message
		if error_msg == None:
			await ctx.send(embed=discord.Embed(
				title=f'Ha ocurrido un error',
				description=f'```py\n{repr(error)}\n```',
				colour=core.default_color(ctx)
			).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url).set_footer(text='Este error ha sido notificado y será investigado para su posterior correción.'))
			raise error

		# If the error message is an empty string, don't do anything
		if error_msg == '':
			return
		else:
			# If the error message ends with '---', don't set a cooldown
			if error_msg.endswith('---'):
				error_msg = error_msg[:-3]
				ctx.command.reset_cooldown(ctx)
			await ctx.send(core.Warning.error(error_msg))


	@commands.Cog.listener('on_app_command_completion')
	async def command_logging(self, interaction, command):
		core.logger.info(f'Se he usado un comando: "{command.name} {interaction.namespace}", servidor "{interaction.guild.name} <{interaction.guild.id}>", canal "{interaction.channel.name} <{interaction.channel.id}>" {interaction.data}')

		if core.bot_mode == 'stable':
			# Update the command stats
			core.cursor.execute(f"SELECT * FROM COMMANDSTATS WHERE COMMAND='{command.name}'")
			db_command_data = core.cursor.fetchall()
			if db_command_data == []:
				core.cursor.execute(f"INSERT INTO COMMANDSTATS VALUES('{command.name}', 1)")
			else:
				core.cursor.execute(f"UPDATE COMMANDSTATS SET USES={db_command_data[0][1] + 1} WHERE COMMAND='{db_command_data[0][0]}'")

			core.conn.commit()


	@commands.Cog.listener('on_guild_join')
	async def guild_join_logging(self, guild):
		core.logger.info(f'El bot ha entrado a un servidor: {repr(guild)}')


	@commands.Cog.listener('on_guild_remove')
	async def guild_join_logging(self, guild):
		core.logger.info(f'El bot ha salido de un servidor: {repr(guild)}')


async def setup(bot):
	await bot.add_cog(Listeners(bot), guild=core.bot_guild)
