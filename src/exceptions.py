from typing import Any

from discord.app_commands import AppCommandError

from tags import TagContext


class TagError(AppCommandError):
    def __init__(self, *args: object, ctx: 'TagContext') -> None:
        super().__init__(*args)
        self.ctx = ctx


class ExistentTagError(TagError):
    pass


class NonExistentTagError(TagError):
    pass


class DisabledTagsError(TagError):
    pass


class BlacklistUserError(AppCommandError):
    pass


class NotOwnerError(AppCommandError):
    pass


class EvalReturn(AppCommandError):  #noqa: N818
    def __init__(self, value: Any):
        super().__init__()
        self.value = value
