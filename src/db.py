from random import choice
from sqlite3 import connect

import discord

import core
import exceptions


conn = connect('./line.db')
cursor = conn.cursor()

cursor.execute("SELECT command FROM commandstats")
commandstats_commands: list[str] = [command[0] for command in cursor.fetchall()]


def default_color(interaction: discord.Interaction) -> int | discord.Color:
    # Check the color of the user in the database
    cursor.execute("SELECT value FROM colors WHERE id=?", (interaction.user.id,))
    color: tuple[int] | None = cursor.fetchone()

    if color is None:
        if interaction.guild is None:
            return discord.Color.blue()
        try:
            return interaction.guild.me.color
        except AttributeError:
            return discord.Color.blue()

    # If the color value is 0, return a random color
    if color[0] == 0:
        return core.colors[choice(tuple(core.colors)[1:])].value
    return int(color[0])


def check_blacklist(
        interaction: discord.Interaction,
        user: discord.abc.User | None = None,
        raises=True
    ) -> bool:
    user = user or interaction.user
    cursor.execute("SELECT user FROM blacklist WHERE user=?", (user.id,))
    check: tuple[int] | None = cursor.fetchone()
    if check is None:
        return True
    if raises:
        raise exceptions.BlacklistUserError('This user is in the blacklist')
    return False
    
