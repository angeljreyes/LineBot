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
