from typing import Any
from discord.app_commands import AppCommandError

from extensions.tags import TagContext


class ExistentTagError(AppCommandError):
    pass

class NonExistentTagError(AppCommandError):
    pass

class DisabledTagsError(AppCommandError):
    def __init__(self, *args, ctx: TagContext):
        super().__init__(args)
        self.ctx = ctx

class BlacklistUserError(AppCommandError):
    pass

class ImageNotFound(AppCommandError):
    pass

class NotOwner(AppCommandError):
    pass

class EvalReturn(AppCommandError):
    def __init__(self, value: Any):
        super().__init__()
        self.value = value

