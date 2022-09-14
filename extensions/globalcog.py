import discord
from discord.ext import commands
from datetime import datetime

MISSING = discord.utils.MISSING

class GlobalCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.ready_at = datetime.utcnow()
		self.command_registry = {}
		self.cached_prefixes = {}

	async def send(self, ctx, content=None, *, tts=None, embed=None, embeds=None, file=None, files=None, stickers=None, delete_after=None, 
	nonce=None, allowed_mentions=None, reference=None, mention_author=None, view=None):
		# Check if there's a command attached to the messaged
		if ctx.message.id in self.command_registry:
			msg = self.command_registry[ctx.message.id]
			try:
				await msg.clear_reactions()
			except:
				pass
			# if embed != None:
			# 	if embeds != None:
			# 		raise discord.errors.InvalidArgument('cannot pass both embed and embeds parameter to edit()')
			# 	embeds = [embed]
			embeds = MISSING if embeds == None else embeds
			await msg.edit(content=content, embed=embed, embeds=ic(embeds), delete_after=delete_after, allowed_mentions=allowed_mentions, view=view)
			return await msg.channel.fetch_message(msg.id)

		else:
			msg = await ctx.send(content, tts=tts, embed=embed, embeds=embeds, file=file, files=files, stickers=stickers, delete_after=delete_after,
			nonce=nonce, allowed_mentions=allowed_mentions, reference=reference, mention_author=mention_author, view=view)
			if len(self.command_registry) > 300:
				del self.command_registry[list(self.command_registry.keys())[0]]
			self.command_registry.update({ctx.message.id: msg})
			return msg



def setup(bot):
	bot.add_cog(GlobalCog(bot))