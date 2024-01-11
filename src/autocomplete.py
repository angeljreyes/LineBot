import discord
from discord import app_commands

import db
import core


async def changelog(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
	versions = list(filter(lambda x: x.startswith(current), core.cached_versions))
	if len(versions) > 25:
		versions = versions[:24]
	version_choices = [app_commands.Choice(name=version, value=version) for version in versions]
	version_choices.append(app_commands.Choice(name='Ver todo', value='list'))
	return version_choices


async def color(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
	color_options = list(filter(lambda x: x.startswith(current), list(core.colors_display)))
	color_options = [app_commands.Choice(name=core.colors_display[color], value=color) for color in core.colors]
	color_options.append(app_commands.Choice(name='Color por defecto', value='default'))
	return color_options


async def commandstats(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
	commands = sorted(list(filter(lambda x: x.startswith(current), db.commandstats_commands)))[:7]
	commands = [app_commands.Choice(name=command, value=command) for command in commands]
	return commands
