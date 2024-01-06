import json
from urllib.parse import quote

import discord
from discord import app_commands
from discord.ext import commands
from requests import get
from urllib.parse import quote

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
		top: app_commands.Range[str, 1, 45],
		bottom: app_commands.Range[str, 1, 40]
	):
		"""
		top: app_commands.Range[str, 0, 45]
			Texto superior
		bottom: app_commands.Range[str, 0, 40]
			Texto inferior
		"""
		await interaction.response.send_message(await self.api.did_you_mean(top, bottom))


	# drake
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5)
	@app_commands.rename(top="superior", bottom="inferior")
	async def drake(
		self,
		interaction: discord.Interaction,
		top: app_commands.Range[str, 1, 250],
		bottom: app_commands.Range[str, 1, 250]
):
		"""
		top: app_commands.Range[str, 0, 250]
			Texto superior
		bottom: app_commands.Range[str, 0, 250]
			Texto inferior
		"""
		await interaction.response.send_message(await self.api.drake(top, bottom))


	# calling
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5)
	@app_commands.rename(text='texto')
	async def calling(
		self,
		interaction: discord.Interaction,
		text: app_commands.Range[str, 1, 500],
	):
		await interaction.response.send_message(await self.api.calling(text))


	# supreme
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5)
	@app_commands.rename(text='texto')
	async def supreme(
		self,
		interaction: discord.Interaction,
		text: app_commands.Range[str, 1, 500],
	):
		await interaction.response.send_message(await self.api.supreme(text))


	# captcha
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5)
	@app_commands.rename(text='texto')
	async def captcha(
		self,
		interaction: discord.Interaction,
		text: app_commands.Range[str, 1, 250],
	):
		# I had to do it this way because Client.captcha() is broken
		URL = 'https://api.alexflipnote.dev/captcha?text={}'
		await interaction.response.send_message(URL.format(quote(text)))


	# facts
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5)
	@app_commands.rename(text='texto')
	async def facts(
		self,
		interaction: discord.Interaction,
		text: app_commands.Range[str, 1, 500],
	):
		await interaction.response.send_message(await self.api.facts(text))


	# birb
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5)
	async def birb(self, interaction: discord.Interaction):
		await interaction.response.send_message(await self.api.birb())


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
