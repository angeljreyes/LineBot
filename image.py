import json
from urllib.parse import quote

import discord
from discord.ext import commands
from requests import get

import botdata
import helpsys
from alexflipnote import Client


class Image(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.send = bot.get_cog('GlobalCog').send
		botdata.cursor.execute("SELECT VALUE FROM RESOURCES WHERE KEY='alexflipnote_token'")
		token = botdata.cursor.fetchall()[0][0]
		botdata.conn.commit()
		self.api = Client(token)


	# # didyoumean
	# @commands.cooldown(1, 5.0, commands.BucketType.user)
	# @commands.command(aliases=['didumean', 'dym', 'dum'])
	# async def didyoumean(self, ctx, *, text=None):
	# 	if text != None:
	# 		if ' ; ' in text:
	# 			top, bottom = list(map(lambda x: quote(x), text.split(' ; ')))[:2]
	# 			if len(top) > 45 or len(bottom) > 40:
	# 				await self.send(ctx, botdata.Warning.error('El límite del texto superior es de 45 caracteres, el del texto inferior es de 40'))
				
	# 			else:
	# 				await self.send(ctx, (await self.api.didyoumean(top, bottom)).url)

	# 	else:
	# 		await self.send(ctx, embed=helpsys.get_cmd(ctx), )


	# # drake
	# @commands.cooldown(1, 5.0, commands.BucketType.user)
	# @commands.command()
	# async def drake(self, ctx, *, text=None):
	# 	if text != None:
	# 		if ' ; ' in text:
	# 			top, bottom = list(map(lambda x: quote(x), text.split(' ; ')))[:2]
	# 			if len(top + bottom) > 500:
	# 				await self.send(ctx, botdata.Warning.error('El límite de caracteres es de 500 entre los 2 textos'))

	# 			else:
	# 				await self.send(ctx, (await self.api.drake(top, bottom)).url)

	# 	else:
	# 		await self.send(ctx, embed=helpsys.get_cmd(ctx))


	# # bad
	# @commands.cooldown(1, 5.0, commands.BucketType.user)
	# @commands.command()
	# async def bad(self, ctx, url=None):
	# 	if url == None:
	# 		image = await botdata.get_channel_image(ctx)

	# 	else:
	# 		image = url

	# 	if image.startswith('https://cdn.discordapp.com/'):
	# 		await self.send(ctx, (await self.api.bad(image)).url)

	# 	else:
	# 		await self.send(ctx, botdata.Warning.error('URL inválida. Solo se permiten URLs de imagenes de discord: `cdn.discordapp.com/`'))


	# # amiajoke
	# @commands.cooldown(1, 5.0, commands.BucketType.user)
	# @commands.command(aliases=['amiajoketoyou', 'aiaj', 'aiajty'])
	# async def amiajoke(self, ctx, url=None):
	# 	if url == None:
	# 		image = await botdata.get_channel_image(ctx)

	# 	else:
	# 		image = url

	# 	if image.startswith('https://cdn.discordapp.com/'):
	# 		await self.send(ctx, (await self.api.amiajoke(image)).url)

	# 	else:
	# 		await self.send(ctx, botdata.Warning.error('URL inválida. Solo se permiten URLs de imagenes de discord: `cdn.discordapp.com/`'))


	# # jokeoverhead
	# @commands.cooldown(1, 5.0, commands.BucketType.user)
	# @commands.command(aliases=['joh', 'woosh'])
	# async def jokeoverhead(self, ctx, url=None):
	# 	if url == None:
	# 		image = await botdata.get_channel_image(ctx)

	# 	else:
	# 		image = url

	# 	if image.startswith('https://cdn.discordapp.com/'):
	# 		await self.send(ctx, (await self.api.jokeoverhead(image)).url)

	# 	else:
	# 		await self.send(ctx, botdata.Warning.error('URL inválida. Solo se permiten URLs de imagenes de discord: `cdn.discordapp.com/`'))


	# # salty
	# @commands.cooldown(1, 5.0, commands.BucketType.user)
	# @commands.command()
	# async def salty(self, ctx, url=None):
	# 	if url == None:
	# 		image = await botdata.get_channel_image(ctx)

	# 	else:
	# 		image = url

	# 	if image.startswith('https://cdn.discordapp.com/'):
	# 		await self.send(ctx, (await self.api.salty(image)).url)

	# 	else:
	# 		await self.send(ctx, botdata.Warning.error('URL inválida. Solo se permiten URLs de imagenes de discord: `cdn.discordapp.com/`'))


	# # calling
	# @commands.cooldown(1, 5.0, commands.BucketType.user)
	# @commands.command()
	# async def calling(self, ctx, *, text=None):
	# 	if text == None:
	# 		await self.send(ctx, embed=helpsys.get_cmd(ctx))

	# 	elif len(text) > 500:
	# 		await self.send(ctx, botdata.Warning.error('El límite de caracteres es de 500'))

	# 	else:
	# 		await self.send(ctx, await self.api.calling(text))


	# # supreme
	# @commands.cooldown(1, 5.0, commands.BucketType.user)
	# @commands.command()
	# async def supreme(self, ctx, theme=None, *, text=None):
	# 	if None in (theme, text):
	# 		await self.send(ctx, embed=helpsys.get_cmd(ctx))

	# 	elif len(text) > 500:
	# 		await self.send(ctx, botdata.Warning.error('El límite de caracteres es de 500'))

	# 	else:
	# 		theme = theme.lower()
	# 		if theme not in ('dark', 'light'):
	# 			await self.send(ctx, embed=helpsys.get_cmd(ctx))

	# 		else:
	# 			await self.send(ctx, await self.api.supreme(text, dark=theme == 'dark', light=theme == 'light'))


	# # captcha
	# @commands.cooldown(1, 5.0, commands.BucketType.user)
	# @commands.command()
	# async def captcha(self, ctx, *, text=None):
	# 	if text == None:
	# 		await self.send(ctx, embed=helpsys.get_cmd(ctx))

	# 	elif len(text) > 500:
	# 		await self.send(ctx, botdata.Warning.error('El límite de caracteres es de 500'))

	# 	else:
	# 		await self.send(ctx, await self.api.captcha(text))


	# # facts
	# @commands.cooldown(1, 5.0, commands.BucketType.user)
	# @commands.command()
	# async def facts(self, ctx, *, text=None):
	# 	if text == None:
	# 		await self.send(ctx, embed=helpsys.get_cmd(ctx))

	# 	elif len(text) > 500:
	# 		await self.send(ctx, botdata.Warning.error('El límite de caracteres es de 500'))

		# else:
		# 	await self.send(ctx, await self.api.facts(text))


	# birb
	@commands.cooldown(1, 5.0, commands.BucketType.user)
	@commands.command()
	async def birb(self, ctx):
		await self.send(ctx, await self.api.birb())


	# dog
	@commands.cooldown(1, 5.0, commands.BucketType.user)
	@commands.command()
	async def dog(self, ctx):
		await self.send(ctx, await self.api.dogs())


	# cat
	@commands.cooldown(1, 5.0, commands.BucketType.user)
	@commands.command()
	async def cat(self, ctx):
		await self.send(ctx, await self.api.cats())


	# sadcat
	@commands.cooldown(1, 5.0, commands.BucketType.user)
	@commands.command()
	async def sadcat(self, ctx):
		await self.send(ctx, await self.api.sadcat())


	# mcskin
	@commands.cooldown(1, 5.0, commands.BucketType.user)
	@commands.command(aliases=['skin'])
	async def mcskin(self, ctx, *, user=None):
		if user == None:
			await self.send(ctx, embed=helpsys.get_cmd(ctx))

		elif len(user) > 16:
			await self.send(ctx, botdata.Warning.error('El límite de caracteres es de 16'))

		else:
			raw = f'https://minotar.net/skin/{quote(user)}.png'
			await self.send(ctx, embed=discord.Embed(
				title=f'Skin de {user}',
				colour=botdata.default_color(ctx),
				url=raw
			).set_image(url=f'https://minotar.net/armor/body/{quote(user)}/400.png').set_thumbnail(url=raw)\
.set_footer(text='La skin de Steve podría ser que el jugador no existe o ha la API está caída'))



def setup(bot):
	bot.add_cog(Image(bot))
