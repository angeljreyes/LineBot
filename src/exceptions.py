from typing import Any
from discord.app_commands import AppCommandError


class ExistentTagError(AppCommandError):
    pass

class NonExistentTagError(AppCommandError):
    pass

class DisabledTagsError(AppCommandError):
    pass

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

