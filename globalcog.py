import discord
from discord.ext import commands
from datetime import datetime

class GlobalCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.ready_at = datetime.utcnow()
		self.command_registry = {}
		self.cached_prefixes = {}

	async def send(self, ctx, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, 
	nonce=None, allowed_mentions=None, failed=False):
		if ctx.message.id in self.command_registry:
			msg = self.command_registry[ctx.message.id]
			try:
				await msg.clear_reactions()
			except:
				pass
			await msg.edit(content=content, tts=tts, embed=embed, delete_after=delete_after, allowed_mentions=allowed_mentions)
			return await msg.channel.fetch_message(msg.id)

		else:
			msg = await ctx.send(content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after,
			nonce=nonce, allowed_mentions=allowed_mentions)
			if len(self.command_registry) > 300:
				del self.command_registry[list(self.command_registry.keys())[0]]
			self.command_registry.update({ctx.message.id: msg})
			return msg



def setup(bot):
	bot.add_cog(GlobalCog(bot))