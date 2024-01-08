import discord

import db
import exceptions


class Tag:
	__slots__ = ('interaction', 'guild', 'user', 'name', 'content', 'img', 'nsfw')

	def __init__(self, interaction: discord.Interaction, guild_id: int, user_id: int, name: str, content: str, img: bool, nsfw: bool):
		self.interaction = interaction
		self.guild = interaction.client.get_guild(guild_id)
		self.user = interaction.client.get_user(user_id)
		self.name = name
		self.content = content
		self.img = bool(img)
		self.nsfw = bool(nsfw)

	def __str__(self) -> str:
		return self.name

	def gift(self, user: discord.Member) -> None:
		db.cursor.execute(f"UPDATE TAGS2 SET USER={user.id} WHERE GUILD={self.guild.id} AND NAME=?", (self.name,))
		db.conn.commit()
		self.user = user

	def rename(self, name: str) -> None:
		db.cursor.execute(f"UPDATE TAGS2 SET NAME=? WHERE GUILD={self.guild.id} AND NAME=?", (name, self.name))
		db.conn.commit()
		self.name = name

	def edit(self, content: str, img: bool, nsfw: bool) -> None:
		self.content = content
		self.img = img
		self.nsfw = nsfw
		db.cursor.execute(f"UPDATE TAGS2 SET CONTENT=?, IMG={int(self.img)}, NSFW={int(self.nsfw)} WHERE GUILD={self.guild.id} AND NAME=?", (self.content, self.name))
		db.conn.commit()

	def delete(self) -> None:
		db.cursor.execute(f"DELETE FROM TAGS2 WHERE GUILD={self.guild.id} AND NAME=?", (self.name,))
		db.conn.commit()


async def tag_check(interaction: discord.Interaction) -> None:
	db.cursor.execute(f"SELECT GUILD FROM TAGSENABLED WHERE GUILD={interaction.guild.id}")
	check = db.cursor.fetchall()
	if check == []:
		await interaction.response.send_message(Warning.info(
			f'Los tags están desactivados en este servidor. {"Actívalos" if interaction.channel.permissions_for(interaction.user).manage_guild else "Pídele a un administrador que los active"} con el comando {list(filter(lambda x: x.name == "toggle", list(filter(lambda x: x.name == "tag", await interaction.client.tree.fetch_commands(guild=interaction.guild)))[0].options))[0].mention}'))
		raise exceptions.DisabledTagsError('Tags are not enabled on this guild')


def add_tag(interaction: discord.Interaction, name: str, content: str, nsfw: bool) -> None:
    db.cursor.execute("INSERT INTO TAGS2 VALUES(?,?,?,?,?,?)", (interaction.guild.id, interaction.user.id, name, content, int(nsfw), 0))
    db.conn.commit()


def check_tag_name(interaction: discord.Interaction, tag_name: str) -> None:
    for char in tag_name:
        if char in (' ', '_', '~', '*', '`', '|', ''):
            raise ValueError('Invalid characters detected')
    if tag_name in [tag.name for tag in get_guild_tags(interaction)]:
        raise exceptions.ExistentTagError(f'Tag "{tag_name}" already exists')


def get_tag(interaction: discord.Interaction, name: str, guild: discord.Guild | None = None) -> Tag:
    db.cursor.execute(f"SELECT * FROM TAGS2 WHERE GUILD={interaction.guild_id if guild is None else guild.id} AND NAME=?", (name,))
    tag = db.cursor.fetchall()
    db.conn.commit()
    if tag != []:
        tag = tag[0]
        return Tag(interaction, tag[0], tag[1], tag[2], tag[3], bool(tag[4]), bool(tag[5]))
    else:
        raise exceptions.NonExistentTagError('This tag does not exist')


def get_member_tags(interaction: discord.Interaction, user: discord.Member) -> list[Tag]:
    db.cursor.execute(f"SELECT * FROM TAGS2 WHERE GUILD={interaction.guild.id} AND USER={user.id}")
    tags = db.cursor.fetchall()
    db.conn.commit()
    if tags != []:
        return [Tag(interaction, tag[0], tag[1], tag[2], tag[3], bool(tag[4]), bool(tag[5])) for tag in tags]
    else:
        raise exceptions.NonExistentTagError('This user doesn\'t have tags')


def get_guild_tags(interaction: discord.Interaction) -> list[Tag]:
    db.cursor.execute(f"SELECT * FROM TAGS2 WHERE GUILD={interaction.guild.id}")
    tags = db.cursor.fetchall()
    db.conn.commit()
    if tags != []:
        return [Tag(interaction, tag[0], tag[1], tag[2], tag[3], bool(tag[4]), bool(tag[5])) for tag in tags]
    else:
        raise exceptions.NonExistentTagError('This server doesn\'t have tags')
