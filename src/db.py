from random import choice
from sqlite3 import connect
from pathlib import Path

import discord

import core
import exceptions


conn = connect('../line.db')
cursor = conn.cursor()

cursor.execute("SELECT command FROM commandstats")
commandstats_commands = [command[0] for command in cursor.fetchall()]


def default_color(interaction: discord.Interaction) -> int | discord.Color:
	# Check the color of the user in the database
	cursor.execute("SELECT value FROM colors WHERE id=?", (interaction.user.id,))
	color = cursor.fetchall()
	if interaction.guild is None and color == []:
		return discord.Colour.blue()
	elif color == []:
		try:
			return interaction.guild.me.color
		except AttributeError:
			return discord.Color.blue()
	else:
		# If the color value is 0, return a random color
		if color[0][0] == 0:
			return core.colors[choice(tuple(core.colors)[1:])].value
		return int(color[0][0])


def check_blacklist(interaction: discord.Interaction, user=None, raises=True) -> bool:
	user = interaction.user if user is None else user
	cursor.execute("SELECT user FROM blacklist WHERE user=?", (user.id,))
	check = cursor.fetchall()
	if check == []:
		return True
	if raises:
		raise exceptions.BlacklistUserError('This user is in the blacklist')
	return False
	