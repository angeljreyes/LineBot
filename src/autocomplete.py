import discord

import db
import core

async def changelog(interaction: discord.Interaction, current: str):
	sql = {'stable':"SELECT VERSION FROM CHANGELOG WHERE HIDDEN=0", 'dev':"SELECT VERSION FROM CHANGELOG"}[core.bot_mode]
	db.cursor.execute(sql)
	db_version_data = db.cursor.fetchall()
	db.conn.commit()
	db_version_data.reverse()
	versions = [version[0] for version in db_version_data]
	versions = list(filter(lambda x: x.startswith(current), versions))
	if len(versions) > 25:
		versions = db_version_data[0: 24]
	versions = [core.app_commands.Choice(name=version, value=version) for version in versions]
	versions.append(core.app_commands.Choice(name='Ver todo', value='list'))
	return versions


async def color(interaction: discord.Interaction, current: str):
	color_options = list(filter(lambda x: x.startswith(current), list(core.colors_display)))
	color_options = [core.app_commands.Choice(name=core.colors_display[color], value=color) for color in core.colors]
	color_options.append(core.app_commands.Choice(name='Color por defecto', value='default'))
	return color_options


async def commandstats(interaction: discord.Interaction, current: str):
	commands = sorted(list(filter(lambda x: x.startswith(current), core.commandstats_commands)))[:7]
	commands = [core.app_commands.Choice(name=command, value=command) for command in commands]
	return commands

