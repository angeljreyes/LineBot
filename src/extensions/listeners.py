import exceptions
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands

import core
import db


class Listeners(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

		@self.bot.tree.error
		async def error_handler(interaction: discord.Interaction, error: Exception) -> None:
			error_msg = None

			# An exception object and its error message
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
				commands.ArgumentParsingError: 'Hiciste un mal uso de las comillas',
				commands.NoPrivateMessage: 'Este comando solo se puede usar en servidores',
				commands.MaxConcurrencyReached: lambda: f'Se alcanzó el límite de usuarios para este comando: `{error.number}{"" if error.per == commands.BucketType.default else f" por {core.bucket_types[error.per]}"}`',
				commands.MissingPermissions: lambda: f'No tienes los permisos requeridos para ejecutar este comando: ' + ', '.join((f'`{perm.replace("_", " ")}`' for perm in error.missing_perms)),
				commands.NSFWChannelRequired: 'Este comando solo se puede usar en canales NSFW',
				app_commands.CommandOnCooldown: lambda: f'Tienes que esperar **{core.fix_delta(timedelta(seconds=error.retry_after), ms=True)}** para ejecutar este comando de nuevo',
				# Sometimes CommandInvokeError is raised, so the error is
				# identified by the first characters of the error string
				app_commands.CommandInvokeError: {
					'403 Forbidden (error code: 50013): Missing Permissions': 'No tengo los permisos requeridos para ejecutar este comando. Intenta añadirlos editando los permisos o la posición mi rol',
					'Unknown Message': 'El mensaje que se trató de editar/eliminar/reaccionar fue eliminado',
					'.value: Must be 1024 or fewer in length.': 'El valor de una sección de un embed no debe ser mayor a 1024 caracteres',
					'Invalid Form Body\nIn data.content: Must be 2000 or fewer in length': 'El mensaje no debe superar los 2000 caracteres',
					'Invalid Form Body\nIn data.content: Must be 4000 or fewer in length': 'El mensaje no debe superar los 4000 caracteres',
					'ValueError: Tag name limit reached': 'El límite de caracteres para el nombre un tag es de 32',
					'ValueError: Invalid characters detected': 'El nombre de un tag no puede contener espacios ni caracteres markdown',
					'ValueError: Invalid URL': 'URL inválida'
				},
				# Custom exceptions
				exceptions.DisabledTagsError: '',
				exceptions.ExistentTagError: 'Este tag ya existe', #---
				exceptions.ImageNotFound: 'No se encontró ninguna imagen en los últimos 30 mensajes',
				exceptions.NotOwner: 'Comando exclusivo del dueño del bot',
				exceptions.BlacklistUserError: 'Estás en la lista negra. No tienes permitido usar el bot',
				exceptions.NonExistentTagError: {
					'This tag': 'Este tag no existe', #---
					'This user': 'Este usuario no tiene tags', #---
					'This server': 'Este servidor no tiene tags' #---
				}
			}

			# If the error message hasn't been determined yet
			if error_msg is None:
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
			if not isinstance(error_msg, str) and error_msg is not None:
				error_msg = error_msg()

			# If the error remains unidentified, send a generic error message
			if error_msg is None:
				embed = discord.Embed(
					title=f'Ha ocurrido un error',
					description=f'```py\n{repr(error)}\n```',
					colour=db.default_color(interaction)
				).set_author(
					name=interaction.user.name,
					icon_url=interaction.user.display_avatar.url
				).set_footer(text='Este error ha sido notificado y será investigado para su posterior correción.')
				if not interaction.response.is_done():
					await interaction.response.send_message(embed=embed, ephemeral=True)
				else:
					await interaction.edit_original_response(content=None, embed=embed, attachments=[], view=None)
					await (await interaction.original_response()).clear_reactions()
				core.logger.error('An error has ocurred', exc_info=error)
				return

			# If the error message is an empty string, don't do anything
			if error_msg == '':
				return
			else:
				# If the error message ends with '---', don't set a cooldown
				try:
					await interaction.response.send_message(core.Warning.error(error_msg), ephemeral=True)
				except discord.InteractionResponded:
					await interaction.followup.send(core.Warning.error(error_msg))

	@commands.Cog.listener('on_ready')
	async def ready(self) -> None:
		core.logger.info('Bot iniciado')


	@commands.Cog.listener('on_resumed')
	async def resume(self) -> None:
		core.logger.info('Sesión resumida')


	@commands.Cog.listener('on_app_command_completion')
	async def command_logging(
		self,
		interaction: discord.Interaction,
		command: app_commands.Command | app_commands.ContextMenu
	) -> None:
		core.logger.info(
			f'Se he usado un comando: "{command.name} {interaction.namespace}", '
			f'servidor "{interaction.guild.name} <{interaction.guild.id}>", '
			f'canal "{interaction.channel.name} <{interaction.channel.id}>" {interaction.data}'
		)

		if core.bot_mode == 'stable':
			# Update the command stats
			db.cursor.execute("SELECT * FROM commandstats WHERE command='?'", (command.qualified_name,))
			db_command_data: tuple[str, int] | None = db.cursor.fetchone()

			if db_command_data is None:
				db.cursor.execute("INSERT INTO commandstats VALUES('?', 1)", (command.qualified_name,))

			else:
				command_name, command_uses = db_command_data
				db.cursor.execute("UPDATE commandstats SET uses=? WHERE command='?'", (command_uses + 1, command_name))

			db.conn.commit()


	@commands.Cog.listener('on_guild_join')
	async def guild_join_logging(self, guild: discord.Guild) -> None:
		core.logger.info(f'El bot ha entrado a un servidor: {repr(guild)}')


	@commands.Cog.listener('on_guild_remove')
	async def guild_join_logging(self, guild: discord.Guild) -> None:
		core.logger.info(f'El bot ha salido de un servidor: {repr(guild)}')


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Listeners(bot), guilds=core.bot_guilds)
