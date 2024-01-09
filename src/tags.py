import discord

import db
import exceptions


class Tag:
	__slots__ = ('interaction', 'guild', 'user', 'name', 'content', 'img', 'nsfw')

	def __init__(self, interaction: discord.Interaction, guild_id: int, user_id: int, name: str, content: str, nsfw: bool):
		self.interaction = interaction
		self.guild = interaction.client.get_guild(guild_id)
		self.user = interaction.client.get_user(user_id)
		self.name = name
		self.content = content
		self.nsfw = bool(nsfw)

	def __str__(self) -> str:
		return self.name

	def gift(self, user: discord.Member) -> None:
		db.cursor.execute("UPDATE tags SET user=? WHERE guild=? AND name=?", (user.id, self.guild.id, self.name))
		db.conn.commit()
		self.user = user

	def rename(self, name: str) -> None:
		db.cursor.execute("UPDATE tags SET name=? WHERE guild=? AND name=?", (name, self.guild.id, self.name))
		db.conn.commit()
		self.name = name

	def edit(self, content: str, nsfw: bool) -> None:
		self.content = content
		self.nsfw = nsfw
		db.cursor.execute("UPDATE tags SET content=?, nsfw=? WHERE guild=? AND name=?", (self.content, int(self.nsfw), self.guild.id, self.name))
		db.conn.commit()

	def delete(self) -> None:
		db.cursor.execute("DELETE FROM tags WHERE guild=? AND name=?", (self.guild.id, self.name,))
		db.conn.commit()


async def tag_check(interaction: discord.Interaction) -> None:
	db.cursor.execute("SELECT guild FROM tagsenabled WHERE guild=?", (interaction.guild.id,))
	check = db.cursor.fetchall()
	if check == []:
		await interaction.response.send_message(Warning.info(
			f'Los tags están desactivados en este servidor. {"Actívalos" if interaction.channel.permissions_for(interaction.user).manage_guild else "Pídele a un administrador que los active"} con el comando {list(filter(lambda x: x.name == "toggle", list(filter(lambda x: x.name == "tag", await interaction.client.tree.fetch_commands(guild=interaction.guild)))[0].options))[0].mention}'))
		raise exceptions.DisabledTagsError('Tags are not enabled on this guild')


def add_tag(interaction: discord.Interaction, name: str, content: str, nsfw: bool) -> None:
    db.cursor.execute("INSERT INTO tags VALUES(?,?,?,?,?)", (interaction.guild.id, interaction.user.id, name, content, int(nsfw)))
    db.conn.commit()


def check_tag_name(interaction: discord.Interaction, tag_name: str) -> None:
    for char in tag_name:
        if char in (' ', '_', '~', '*', '`', '|', ''):
            raise ValueError('Invalid characters detected')
    if tag_name in [tag.name for tag in get_guild_tags(interaction)]:
        raise exceptions.ExistentTagError(f'Tag "{tag_name}" already exists')


def get_tag(interaction: discord.Interaction, name: str, guild: discord.Guild | None = None) -> Tag:
    guild_id = interaction.guild_id if guild is None else guild.id
    db.cursor.execute("SELECT * FROM tags WHERE guild=? AND name=?", (guild_id, name))
    tag = db.cursor.fetchall()
    if tag != []:
        tag = tag[0]
        return Tag(interaction, tag[0], tag[1], tag[2], tag[3], bool(tag[4]))
    else:
        raise exceptions.NonExistentTagError('This tag does not exist')


def get_member_tags(interaction: discord.Interaction, user: discord.Member) -> list[Tag]:
    db.cursor.execute("SELECT * FROM tags WHERE guild=? AND user=?", (interaction.guild.id, user.id))
    tags = db.cursor.fetchall()
    if tags != []:
        return [Tag(interaction, tag[0], tag[1], tag[2], tag[3], bool(tag[4])) for tag in tags]
    else:
        raise exceptions.NonExistentTagError('This user doesn\'t have tags')


def get_guild_tags(interaction: discord.Interaction) -> list[Tag]:
    db.cursor.execute("SELECT * FROM tags WHERE guild=?", (interaction.guild.id,))
    tags = db.cursor.fetchall()
    if tags != []:
        return [Tag(interaction, tag[0], tag[1], tag[2], tag[3], bool(tag[4])) for tag in tags]
    else:
        raise exceptions.NonExistentTagError('This server doesn\'t have tags')
