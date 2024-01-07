from urllib.parse import quote

import discord
from discord import app_commands
from discord.ext import commands
from alexflipnote import Client

import core
import db


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
		url = f'https://api.alexflipnote.dev/captcha?text={quote(text)}'
		await interaction.response.send_message(url)


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


	# dog
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5)
	async def dog(self, interaction: discord.Interaction):
		await interaction.response.send_message(await self.api.dog())


	# cat
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5)
	async def cat(self, interaction: discord.Interaction):
		await interaction.response.send_message(await self.api.cat())


	# sadcat
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5)
	async def sadcat(self, interaction: discord.Interaction):
		await interaction.response.send_message(await self.api.sadcat())


	# mcskin
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5)
	async def mcskin(
		self,
		interaction: discord.Interaction,
		user: app_commands.Range[str, 1, 16]
	):
		"""
		user: app_commands.Range[str, 1, 16]
			Nombre de usuario de Minecraft
		"""
		username = quote(user)
		url = f'https://minotar.net/skin/{username}.png'
		embed = (
			discord.Embed(
				title=f'Skin de {user}',
				colour=db.default_color(interaction),
				url=url
			)
				.set_image(url=f'https://minotar.net/armor/body/{username}/400.png')
				.set_thumbnail(url=url)
				.set_footer(text='Steve podría significar que el jugador no existe o la API está caída')
		)
		await interaction.response.send_message(embed=embed)



async def setup(bot):
	await bot.add_cog(Image(bot), guilds=core.bot_guilds)
