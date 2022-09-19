from discord.ext.commands import CommandError


class ExistentTagError(CommandError):
	pass

class NonExistentTagError(CommandError):
	pass

class DisabledTagsError(CommandError):
	pass

class BlacklistUserError(CommandError):
	pass

class ImageNotFound(CommandError):
	pass