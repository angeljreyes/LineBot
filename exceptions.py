<<<<<<< HEAD
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
=======
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
>>>>>>> 9fe46c28313b8936e0c4946ceb77782969ee0c19
	pass