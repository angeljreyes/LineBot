import discord, asyncio, botdata
from discord.ext import commands


class Mod(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.send = bot.get_cog('GlobalCog').send


	# purge
	@commands.cooldown(1, 4.0, commands.BucketType.user)
	@commands.command(aliases=['clear'])
	@commands.has_permissions(manage_messages=True)
	@commands.guild_only()
	async def purge(self, ctx, amount='a'):	
		if amount.isdigit():
			amount = int(amount)
			if amount > 700: 
				amount = 700
			await ctx.channel.purge(limit=amount+1)
			await ctx.send(f'Ok, eliminé **{amount}' + (' mensaje**' if amount == 1 else ' mensajes**'), delete_after=5)

		else:
			await self.send(ctx, botdata.Warning.error('Escribe un número positivo para eliminar mensajes'))
			ctx.command.reset_cooldown(ctx)


	# kick
	@commands.command()
	@commands.has_permissions(kick_members=True)
	@commands.guild_only()
	async def kick(self, ctx, member=None, reason=''):
		if member == None:
			await self.send(ctx, botdata.Warning.error('Menciona a alguien y di una razon para kickearlo si quieres'))

		else:
			member = await commands.MemberConverter().convert(ctx, member)
			if ctx.author.top_role > member.top_role:
				reason = f'{ctx.author}: Sin razón' if reason == '' else f'{ctx.author}: ' + reason
				await member.kick(reason=reason)
				await self.send(ctx, botdata.Warning.success(f'**{await commands.clean_content().convert(ctx, str(member))}** ha sido kickeado'))
			else:
				await self.send(ctx, botdata.Warning.error('Este usuario tiene el mismo rol o un rol superior al tuyo'))


	# ban
	@commands.command()
	@commands.has_permissions(ban_members=True)
	@commands.guild_only()
	async def ban(self, ctx, member=None, reason=''):
		if member == None:
			await self.send(ctx, botdata.Warning.error('Menciona a alguien y di una razon para banearlo si quieres'))

		else:
			member = await commands.MemberConverter().convert(ctx, member)
			if ctx.author.top_role > member.top_role:
				reason = f'{ctx.author}: Sin razón' if reason == '' else f'{ctx.author}: {reason}'
				await member.ban(reason=reason)
				await self.send(ctx, botdata.Warning.success(f'**{await commands.clean_content().convert(ctx, str(member))}** ha sido baneado'))
			else:
				await self.send(ctx, botdata.Warning.error('Este usuario tiene el mismo rol o un rol superior al tuyo'))


	# hackban
	@commands.command()
	@commands.has_permissions(ban_members=True)
	@commands.guild_only()
	async def hackban(self, ctx, user=None, reason=''):
		if user == None:
			await self.send(ctx, botdata.Warning.error('Menciona a alguien y di una razon para hackbanearlo si quieres'))

		else:
			user = await botdata.get_user(ctx, user)
			reason = f'{ctx.author}: Sin razón' if reason == '' else f'{ctx.author}: {reason}'
			try:
				await ctx.guild.fetch_ban(user)
			except discord.NotFound:
				await ctx.guild.ban(user, reason=reason)
				await self.send(ctx, botdata.Warning.success(f'**{await commands.clean_content().convert(ctx, str(user))}** ha sido hackbaneado'))
			else:
				await self.send(ctx, botdata.Warning.error('Este usuario ya está baneado'))


	# unban
	@commands.command()
	@commands.has_permissions(ban_members=True)
	@commands.guild_only()
	async def unban(self, ctx, user=None, reason=''):
		if user == None:
			await self.send(ctx, botdata.Warning.error('Escribe la ID de alguien y di una razon para revocarle el baneo si quieres'))

		else:
			user = await botdata.get_user(ctx, user)
			reason = f'{ctx.author}: Sin razón' if reason == '' else f'{ctx.author}: ' + reason
			try:
				await ctx.guild.unban(user=user, reason=reason)
			except discord.HTTPException:
				await self.send(ctx, botdata.Warning.error('Este usuario no está baneado'))
			else:
				await self.send(ctx, botdata.Warning.success(f'A **{await commands.clean_content().convert(ctx, str(user))}** se le ha revocado el ban'))


def setup(bot):
	bot.add_cog(Mod(bot))