from random import choice
from re import match
from typing import cast

import discord
from discord import app_commands
from discord.ext import commands

import core
import db


class Modtxt(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot


	# emojitext
	@app_commands.command()
	@app_commands.checks.cooldown(5, 5.0)
	@app_commands.rename(text='texto', use_alts='usar-alts', ephemeral='privado')
	async def emojitext(self, interaction: discord.Interaction, text: str, use_alts: bool = False, ephemeral: bool = False):
		"""Devuelve el texto transformado en emojis

		text
			Texto a convertir en emojis
		use_alts
			Usar emojis alterantivos
		ephemeral
			Mandar un mensaje efímero (privado) o no
		"""
		text = text.lower()
		reg_ind = lambda letter: f':regional_indicator_{letter}:'
		result = ''
		alt_emojis = {
			'a': ':a:',
			'b': ':b:',
			'p': ':parking:',
			'o': ':o2:'
		}
		translations = {
			r'[a-z]': lambda letter: reg_ind(letter),
			r'ñ': lambda _: reg_ind('n'),
			r' ': lambda _: ' '*3,
			r'[0-9]+': lambda letter: f'{letter}\ufe0f\u20e3',
			r'\?': lambda _: ':grey_question:',
			r'\!': lambda _: ':grey_exclamation:'
		}
		for letter in text:
			if use_alts and letter in alt_emojis:
				result += f'{alt_emojis[letter]} '
				continue

			for translation in translations:
				if match(translation, letter):
					result += f'{translations[translation](letter)} '
					break

			else: # else clause executes if the loop doesn't end with a break
				result += f'{letter} '

		await interaction.response.send_message(result, ephemeral=ephemeral)


	# replace
	@app_commands.command()
	@app_commands.checks.cooldown(5, 5.0)
	@app_commands.rename(replacing='reemplazar', replacement='por', text='en', count='límite', ephemeral='privado')
	async def replace(
			self,
			interaction: discord.Interaction,
			replacing: str,
			replacement: str,
			text: str,
			count: int = -1,
			ephemeral: bool = False
		):
		"""Reemplaza el texto del primer parámetro por el segundo parametro en un tercer parámetro

		replacing
			Lo que se va a reemplazar en el texto
		replacement
			Por lo que se va a reemplazar
		text
			Un texto
		count
			El límite de veces que se reemplazarán los caracteres
		ephemeral
			Mandar un mensaje efímero (privado) o no
		"""
		await interaction.response.defer(ephemeral=ephemeral, thinking=True)
		embed = discord.Embed(title='Replace', colour=db.default_color(interaction))
		embed.add_field(name='Valor reemplazado:', value=replacing)
		embed.add_field(name='Reemplazado por:', value=replacement)
		if count > -1:
			embed.add_field(name='Límite', value=count)
		embed.add_field(name='Texto', value=text, inline=False)
		embed.add_field(name='Resultado', value=text.replace(replacing, replacement, count))
		await interaction.followup.send(embed=embed)


	# spacedtext
	@app_commands.command()
	@app_commands.checks.cooldown(2, 5.0)
	@app_commands.rename(text='text', spaces='espacios', ephemeral='privado')
	async def spacedtext(
			self,
			interaction: discord.Interaction,
			text: str,
			spaces: app_commands.Range[int, 1, 30] = 1,
			ephemeral: bool = False
		):
		"""Devuelve el texto enviado con cada letra espaciada el número de veces indicado

		text
			Texto al que se le agregarán espacios
		spaces
			Cantidad de espacios entre cada caracter
		ephemeral
			Mandar un mensaje efímero (privado) o no
		"""
		output = ''
		for char in text:
			output += char + (' ' * spaces)
		await interaction.response.send_message(output, ephemeral=ephemeral)


	# vaporwave
	@app_commands.command()
	@app_commands.checks.cooldown(3, 5.0)
	@app_commands.rename(text='texto', ephemeral='privado')
	async def vaporwave(self, interaction: discord.Interaction, text: str, ephemeral: bool = False):
		"""Devuelve el texto en vaporwave

		text
			Texto a convertir a vaporwave
		ephemeral
			Mandar un mensaje efímero (privado) o no
		"""
		output = ''
		other_chars = {32: 12288, 162: 65504, 163: 65505, 165: 65509, 166: 65508, 172: 65506, 
						175: 65507, 8361: 65510, 10629: 65375, 10630: 65376}
		ZERO_WIDTH_OFFSET = 65248
		for character in text:
			currentchar = ord(character)
			if 33 <= currentchar <= 126:
				output += chr(currentchar + ZERO_WIDTH_OFFSET)
			elif currentchar in other_chars:
				output += chr(other_chars[currentchar])
			else:
				output += character
		await interaction.response.send_message(output, ephemeral=ephemeral)


	# sarcastic
	@app_commands.command()
	@app_commands.checks.cooldown(2, 2.0)
	@app_commands.rename(text='texto', ephemeral='privado')
	async def sarcastic(self, interaction: discord.Interaction, text: str, ephemeral: bool = False):
		"""ConVIeRtE el TEXtO a SarcAStiCO

		text
			Texto a convertir a sArcÁStICo
		ephemeral
			Mandar un mensaje efímero (privado) o no
		"""
		msg = ''.join((choice((letter.lower(), letter.upper())) for letter in text))
		await interaction.response.send_message(msg, ephemeral=ephemeral)


	# uppercase
	@app_commands.command()
	@app_commands.checks.cooldown(2, 2.0)
	@app_commands.rename(text='texto', ephemeral='privado')
	async def uppercase(self, interaction: discord.Interaction, text: str, ephemeral: bool = False):
		"""Convierte un texto a mayúsculas

		text
			Texto a convertir a MAYÚSCULAS
		ephemeral
			Mandar un mensaje efímero (privado) o no
		"""
		ctx = await self.bot.get_context(interaction)
		msg = await commands.clean_content().convert(ctx, text.upper())
		await interaction.response.send_message(msg, ephemeral=ephemeral)


	# lowercase
	@app_commands.command()
	@app_commands.checks.cooldown(2, 2.0)
	@app_commands.rename(text='texto', ephemeral='privado')
	async def lowercase(self, interaction: discord.Interaction, text: str, ephemeral: bool = False):
		"""Convierte un texto a minúsculas

		text
			Texto a convertir a minúsculas
		ephemeral
			Mandar un mensaje efímero (privado) o no
		"""
		ctx = await self.bot.get_context(interaction)
		msg = await commands.clean_content().convert(ctx, text.lower())
		await interaction.response.send_message(msg, ephemeral=ephemeral)


	# swapcase
	@app_commands.command()
	@app_commands.checks.cooldown(2, 2.0)
	@app_commands.rename(text='texto', ephemeral='privado')
	async def swapcase(self, interaction: discord.Interaction, text: str, ephemeral: bool = False):
		"""Intercambia las minúsculas y las mayúsculas de un texto

		text
			Texto a intercambiar minúsculas y mayúsculas
		ephemeral
			Mandar un mensaje efímero (privado) o no
		"""
		ctx = await self.bot.get_context(interaction)
		msg = await commands.clean_content().convert(ctx, text.swapcase())
		await interaction.response.send_message(msg, ephemeral=ephemeral)


	# capitalize
	@app_commands.command()
	@app_commands.checks.cooldown(2, 2.0)
	@app_commands.rename(text='texto', ephemeral='privado')
	async def capitalize(self, interaction: discord.Interaction, text: str, ephemeral: bool = False):
		"""Convierte la primera letra de cada palabra a mayúsculas

		text
			Texto a convertir a Capitalizar
		ephemeral
			Mandar un mensaje efímero (privado) o no
		"""
		ctx = await self.bot.get_context(interaction)
		msg = await commands.clean_content().convert(ctx, text.title())
		await interaction.response.send_message(msg, ephemeral=ephemeral)


	# reverse
	@app_commands.command()
	@app_commands.checks.cooldown(2, 2.0)
	@app_commands.rename(text='texto', ephemeral='privado')
	async def reverse(self, interaction: discord.Interaction, text: str, ephemeral: bool = False):
		"""Revierte un texto

		text
			Texto a convertir a invertir
		ephemeral
			Mandar un mensaje efímero (privado) o no
		"""
		await interaction.response.send_message(await commands.clean_content().convert(interaction, text[::-1]), ephemeral=ephemeral)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Modtxt(bot), guilds=core.bot_guilds) # type: ignore
