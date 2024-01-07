import discord
from discord import app_commands

import db
import core


async def changelog(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
	hidden = 'WHERE HIDDEN=0 ' if core.bot_mode == 'stable' else ''
	sql = f"SELECT VERSION FROM CHANGELOG {hidden}ORDER BY VERSION DESC"
	db.cursor.execute(sql)
	db_version_data: list[tuple[str]] = db.cursor.fetchall()
	db.conn.commit()
	versions = [version[0] for version in db_version_data]
	versions = list(filter(lambda x: x.startswith(current), versions))
	if len(versions) > 25:
		versions = db_version_data[:24]
	versions = [app_commands.Choice(name=version, value=version) for version in versions]
	versions.append(app_commands.Choice(name='Ver todo', value='list'))
	return versions


async def color(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
	color_options = list(filter(lambda x: x.startswith(current), list(core.colors_display)))
	color_options = [app_commands.Choice(name=core.colors_display[color], value=color) for color in core.colors]
	color_options.append(app_commands.Choice(name='Color por defecto', value='default'))
	return color_options


async def commandstats(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
	commands = sorted(list(filter(lambda x: x.startswith(current), db.commandstats_commands)))[:7]
	commands = [app_commands.Choice(name=command, value=command) for command in commands]
	return commands
