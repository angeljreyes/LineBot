from typing import Self, cast

import discord
from discord.ext import commands

import db
import exceptions
import core


RawTag = tuple[int, int, str, str, int]


class Tag:
	__slots__ = ('interaction', 'guild', 'user', 'name', 'content', 'img', 'nsfw')

	def __init__(self, interaction: discord.Interaction, guild_id: int, user_id: int, name: str, content: str, nsfw: bool):
		self.interaction = interaction

		guild = interaction.client.get_guild(guild_id)
		if guild is None:
			raise KeyError('Invalid guild')
		self.guild = guild

		user = interaction.client.get_user(user_id)
		if user is None:
			raise KeyError('Invalid user')
		self.user = user

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

	@classmethod
	def from_db(cls, interaction: discord.Interaction, data: RawTag) -> Self:
		return cls(
			interaction,
			guild_id=data[0],
			user_id=data[1],
			name=data[2],
			content=data[3],
			nsfw=bool(data[4])
		)


async def tag_check(interaction: discord.Interaction[commands.Bot]) -> None:
	if interaction.guild is None:
		raise Exception('The developer missed a guild_only check :(')
	
	db.cursor.execute("SELECT guild FROM tagsenabled WHERE guild=?", (interaction.guild.id,))
	check = db.cursor.fetchone()

	if not check:
		if interaction.channel is None:
			raise exceptions.DisabledTagsError('Invalid channel')

		member = cast(discord.Member, interaction.user)
		has_permission = interaction.channel.permissions_for(member).manage_guild
		toggle_command = await core.fetch_app_command(interaction, 'tag toggle')

		if toggle_command is not None:
			await interaction.response.send_message(core.Warning.info(
				'Los tags están desactivados en este servidor. ' +
				('Actívalos ' if has_permission else 'Pídele a un administrador que los active ') +
				f'con el comando {toggle_command.mention}'
			))

		raise exceptions.DisabledTagsError('Tags are not enabled on this guild')


def add_tag(interaction: discord.Interaction, name: str, content: str, nsfw: bool) -> None:
	if interaction.guild is None:
		raise Exception('The developer missed a guild_only check :(')
		
	db.cursor.execute("INSERT INTO tags VALUES(?,?,?,?,?)", (interaction.guild.id, interaction.user.id, name, content, int(nsfw)))
	db.conn.commit()


def check_tag_name(interaction: discord.Interaction, tag_name: str) -> None:
	for char in tag_name:
		if char in (' ', '_', '~', '*', '`', '|', ''):
			raise ValueError('Invalid characters detected')
	if tag_name in [tag.name for tag in get_guild_tags(interaction)]:
		raise exceptions.ExistentTagError(f'Tag "{tag_name}" already exists')


def get_tag(
		interaction: discord.Interaction,
		name: str,
		guild: discord.Guild | None = None,
		*,
		raises=True
	) -> Tag | None:
	guild_id = interaction.guild_id if guild is None else guild.id
	db.cursor.execute("SELECT * FROM tags WHERE guild=? AND name=?", (guild_id, name))
	tag: RawTag | None = db.cursor.fetchone()
	if tag is not None:
		return Tag.from_db(interaction, tag)

	if raises:
		raise exceptions.NonExistentTagError('This tag does not exist')
	
	return None


def get_member_tags(interaction: discord.Interaction, user: discord.Member, *, raises=False) -> list[Tag]:
	if interaction.guild is None:
		raise Exception('The developer missed a guild_only check :(')
		
	db.cursor.execute("SELECT * FROM tags WHERE guild=? AND user=?", (interaction.guild.id, user.id))
	tags: list[RawTag] = db.cursor.fetchall()
	if tags:
		return [Tag.from_db(interaction, tag) for tag in tags]

	if raises:
		raise exceptions.NonExistentTagError('This user doesn\'t have tags')

	return []


def get_guild_tags(interaction: discord.Interaction, *, raises=False) -> list[Tag]:
	if interaction.guild is None:
		raise Exception('The developer missed a guild_only check :(')
		
	db.cursor.execute("SELECT * FROM tags WHERE guild=?", (interaction.guild.id,))
	tags: list[RawTag] = db.cursor.fetchall()

	if tags:
		return [Tag.from_db(interaction, tag) for tag in tags]

	if raises:
		raise exceptions.NonExistentTagError('This server doesn\'t have tags')

	return []
