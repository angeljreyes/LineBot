from typing import Self

import discord
from discord.ext import commands

import db
import exceptions


type RawTag = tuple[int, int, str, str, int]


class Tag:
    __slots__ = ('ctx', 'guild', 'user', 'name', 'content', 'nsfw')

    def __init__(self, ctx: 'TagContext', guild_id: int, user_id: int, name: str, content: str, nsfw: bool):
        self.ctx = ctx

        guild = ctx.interaction.client.get_guild(guild_id)
        if guild is None:
            raise KeyError('Invalid guild')
        self.guild = guild

        user = ctx.interaction.client.get_user(user_id)
        if user is None:
            raise KeyError('Invalid user')
        self.user = user

        self.name = name
        self.content = content
        self.nsfw = nsfw

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
    def from_db(cls, ctx: 'TagContext', data: RawTag) -> Self:
        return cls(
            ctx,
            guild_id=data[0],
            user_id=data[1],
            name=data[2],
            content=data[3],
            nsfw=bool(data[4])
        )


class TagSafeInteraction:
    def __init__(self, interaction: discord.Interaction[commands.Bot]):
        # Bunch of conditions to get rid of type checking errors
        if (interaction.channel is None
            or isinstance(interaction.channel, discord.abc.PrivateChannel)
            or isinstance(interaction.user, discord.User)
            or interaction.guild is None
            or interaction.guild_id is None
            or interaction.guild.id is None):
            raise commands.NoPrivateMessage()

        self.interaction = interaction
        self.channel = interaction.channel
        self.member = interaction.user
        self.guild = interaction.guild
        self.guild_id = interaction.guild_id


class TagContext(TagSafeInteraction):
    def __init__(self, interaction: discord.Interaction[commands.Bot], *, bypass=False):
        super().__init__(interaction)
        db.cursor.execute("SELECT guild FROM tagsenabled WHERE guild=?", (self.guild.id,))
        check: tuple[int] | None = db.cursor.fetchone()
        if check is None and not bypass:
            raise exceptions.DisabledTagsError('Tags are not enabled on this guild', ctx=self)


    def get_tag(self, name: str, guild_id: int | None = None) -> Tag:
        guild_id = guild_id or self.guild_id
        db.cursor.execute("SELECT * FROM tags WHERE guild=? AND name=?", (guild_id, name))
        tag: RawTag | None = db.cursor.fetchone()
        if tag is None:
            raise exceptions.NonExistentTagError('This tag does not exist', ctx=self)

        return Tag.from_db(self, tag)


    def add_tag(self, name: str, content: str, nsfw: bool) -> None:
        db.cursor.execute(
            "INSERT INTO tags VALUES(?,?,?,?,?)",
            (self.guild.id, self.member.id, name, content, int(nsfw)))
        db.conn.commit()


    def check_name(self, name: str) -> None:
        for char in name:
            if char in (' ', '_', '~', '*', '`', '|', ''):
                raise ValueError('Invalid characters detected')

        db.cursor.execute(
            "SELECT guild FROM tags WHERE guild=? AND name=?",
            (self.guild_id, name)
        )
        check: tuple[int] | None = db.cursor.fetchone()
        if check is not None:
            raise exceptions.ExistentTagError(f'Tag "{name}" already exists', ctx=self)


    def get_member_tags(self, user: discord.Member) -> list[Tag]:
        db.cursor.execute(
            "SELECT * FROM tags WHERE guild=? AND user=?",
            (self.guild_id, user.id)
        )
        tags: list[RawTag] = db.cursor.fetchall()
        return [Tag.from_db(self, tag) for tag in tags]


    def get_guild_tags(self) -> list[Tag]:
        db.cursor.execute(
            "SELECT * FROM tags WHERE guild=?",
            (self.guild_id,)
        )
        tags: list[RawTag] = db.cursor.fetchall()
        return [Tag.from_db(self, tag) for tag in tags]


