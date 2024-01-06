import json
from urllib.parse import quote

import discord
from discord import app_commands
from discord.ext import commands
from requests import get

import core
import db
from alexflipnote import Client


class Image(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.api = Client()


	# didyoumean
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5)
	@app_commands.rename(top="superior", bottom="inferior")
	async def didyoumean(
		self,
		interaction: discord.Interaction,
		top: app_commands.Range[str, 0, 45],
		bottom: app_commands.Range[str, 0, 40]
	):
		"""
		top: app_commands.Range[str, 0, 45]
			Texto superior
		bottom: app_commands.Range[str, 0, 40]
			Texto inferior
		"""
		await interaction.response.send_message(await self.api.did_you_mean(top, bottom))


	# # drake
	# @commands.cooldown(1, 5.0, commands.BucketType.user)
	# @app_commands.command()
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
	# @app_commands.command()
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
	# @app_commands.command(aliases=['amiajoketoyou', 'aiaj', 'aiajty'])
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
	# @app_commands.command(aliases=['joh', 'woosh'])
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
	# @app_commands.command()
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
	# @app_commands.command()
	# async def calling(self, ctx, *, text=None):
	# 	if text == None:
	# 		await self.send(ctx, embed=helpsys.get_cmd(ctx))

	# 	elif len(text) > 500:
	# 		await self.send(ctx, botdata.Warning.error('El límite de caracteres es de 500'))

	# 	else:
	# 		await self.send(ctx, await self.api.calling(text))


	# # supreme
	# @commands.cooldown(1, 5.0, commands.BucketType.user)
	# @app_commands.command()
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
	# @app_commands.command()
	# async def captcha(self, ctx, *, text=None):
	# 	if text == None:
	# 		await self.send(ctx, embed=helpsys.get_cmd(ctx))

	# 	elif len(text) > 500:
	# 		await self.send(ctx, botdata.Warning.error('El límite de caracteres es de 500'))

	# 	else:
	# 		await self.send(ctx, await self.api.captcha(text))


	# # facts
	# @commands.cooldown(1, 5.0, commands.BucketType.user)
	# @app_commands.command()
	# async def facts(self, ctx, *, text=None):
	# 	if text == None:
	# 		await self.send(ctx, embed=helpsys.get_cmd(ctx))

	# 	elif len(text) > 500:
	# 		await self.send(ctx, botdata.Warning.error('El límite de caracteres es de 500'))

		# else:
		# 	await self.send(ctx, await self.api.facts(text))


# 	# birb
# 	@commands.cooldown(1, 5.0, commands.BucketType.user)
# 	@app_commands.command()
# 	async def birb(self, ctx):
# 		await self.send(ctx, await self.api.birb())


# 	# dog
# 	@commands.cooldown(1, 5.0, commands.BucketType.user)
# 	@app_commands.command()
# 	async def dog(self, ctx):
# 		await self.send(ctx, await self.api.dogs())


# 	# cat
# 	@commands.cooldown(1, 5.0, commands.BucketType.user)
# 	@app_commands.command()
# 	async def cat(self, ctx):
# 		await self.send(ctx, await self.api.cats())


# 	# sadcat
# 	@commands.cooldown(1, 5.0, commands.BucketType.user)
# 	@app_commands.command()
# 	async def sadcat(self, ctx):
# 		await self.send(ctx, await self.api.sadcat())


# 	# mcskin
# 	@commands.cooldown(1, 5.0, commands.BucketType.user)
# 	@app_commands.command(aliases=['skin'])
# 	async def mcskin(self, ctx, *, user=None):
# 		if user == None:
# 			await self.send(ctx, embed=helpsys.get_cmd(ctx))

# 		elif len(user) > 16:
# 			await self.send(ctx, core.Warning.error('El límite de caracteres es de 16'))

# 		else:
# 			raw = f'https://minotar.net/skin/{quote(user)}.png'
# 			await self.send(ctx, embed=discord.Embed(
# 				title=f'Skin de {user}',
# 				colour=db.default_color(ctx),
# 				url=raw
# 			).set_image(url=f'https://minotar.net/armor/body/{quote(user)}/400.png').set_thumbnail(url=raw)\
# .set_footer(text='La skin de Steve podría ser que el jugador no existe o ha la API está caída'))



async def setup(bot):
	await bot.add_cog(Image(bot), guilds=core.bot_guilds)
