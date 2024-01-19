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
			note = str(error)

			match error:

				case discord.HTTPException():
					if 'Must be 2000 or fewer in length' in note:
						error_msg = 'El mensaje supera los 2000 caracteres'
				
				case commands.CommandNotFound():
					error_msg = ''

				case commands.BadArgument():
					if 'Member' in note:
						error_msg = 'No se encontró a ese usuario en este servidor'
					elif 'User' in note:
						error_msg = 'No se encontró a ese usuario'
					elif 'Role' in note:
						error_msg = 'No se encontró ese rol'
					elif 'Channel' in note:
						error_msg = 'No se encontró ese canal'

				case commands.NoPrivateMessage():
					error_msg = 'Este comando solo se puede usar en servidores'

				case commands.MaxConcurrencyReached(number=number, per=per):
					error_msg = f'Se alcanzó el límite de usuarios para este comando: {number}'
					if per != commands.BucketType.default:
						error_msg += f' por {core.bucket_types[per]}'

				case commands.MissingPermissions(missing_permissions=perms):
					error_msg = (
						'No tienes los permisos requeridos para ejecutar este comando: '
						+ ', '.join([f'`{perm}`' for perm in perms])
					)

				case commands.NSFWChannelRequired():
					error_msg = 'Este comando solo se puede usar en canales NSFW'

				case app_commands.CommandOnCooldown(retry_after=retry_after):
					cooldown = core.fix_delta(timedelta(seconds=retry_after), ms=True)
					error_msg = f'Tienes que esperar **{cooldown}** para ejecutar este comando de nuevo'

				case app_commands.CommandInvokeError():
					types = (
						('(error code: 50013): Missing Permissions', 
						   'No tengo los permisos requeridos para ejecutar este comando. '
						   'Intenta añadirlos editando los permisos o la posición mi rol'),
						('Unknown Message', 'El mensaje que se trató de editar/eliminar/reaccionar fue eliminado'),
						('.value: Must be 1024 or fewer in length.', 'El valor de una sección de un embed no debe ser mayor a 1024 caracteres'),
						('Must be 2000 or fewer in length', 'El mensaje no debe superar los 2000 caracteres'),
						('Must be 4000 or fewer in length', 'El mensaje no debe superar los 4000 caracteres'),
						('ValueError: Tag name limit reached', 'El límite de caracteres para el nombre un tag es de 32'),
						('ValueError: Invalid characters detected', 'El nombre de un tag no puede contener espacios ni caracteres markdown'),
						('ValueError: Invalid URL', 'URL inválida')
					)
					for error_note, message in types:
						if error_note in note:
							error_msg = message

				case exceptions.DisabledTagsError():
					error_msg = ''
				
				case exceptions.ExistentTagError():
					error_msg = 'Este tag ya existe'

				case exceptions.ImageNotFound():
					error_msg = 'No se encontró ninguna imagen en los últimos 30 mensajes'

				case exceptions.NotOwner():
					error_msg = 'Comando exclusivo del dueño del bot'

				case exceptions.BlacklistUserError():
					error_msg = 'Estás en la lista negra. No tienes permitido usar el bot'

				case exceptions.NonExistentTagError():
					if 'This tag' in note:
						error_msg = 'Este tag no existe'
					if 'This user' in note:
						error_msg = 'Este usuario no tiene tags'
					elif 'This server' in note:
						error_msg = 'Este servidor no tiene tags'

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
			if not error_msg:
				return

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
			f'servidor "{interaction.guild} <{interaction.guild.id if interaction.guild else "?"}>", '
			f'canal "{interaction.channel} <{interaction.channel.id if interaction.channel else "?"}>" {interaction.data}'
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
	async def guild_leave_logging(self, guild: discord.Guild) -> None:
		core.logger.info(f'El bot ha salido de un servidor: {repr(guild)}')


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Listeners(bot), guilds=core.bot_guilds) # type: ignore
