import asyncio
from random import choice
from re import match

import discord
from discord import app_commands
from discord.ext import commands

import core


class Modtxt(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	# emojitext
	@app_commands.command()
	@app_commands.checks.cooldown(5, 5.0)
	@app_commands.rename(text='texto', use_alts='usar-alts', ephemeral='privado')
	async def emojitext(self, interaction, text:str, use_alts:bool=False, ephemeral:bool=False):
		"""
		text: str
			Texto a convertir en emojis
		use_alts: bool
			Usar emojis alterantivos
		ephemeral: bool
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
			r'ñ': lambda letter: reg_ind('n'),
			r' ': lambda letter: ' '*3,
			r'[0-9]+': lambda letter: f'{letter}\ufe0f\u20e3',
			'\?': lambda letter: ':grey_question:',
			'\!': lambda letter: ':grey_exclamation:'
		}
		for letter in text:
			if use_alts and letter in alt_emojis:
				result += f'{alt_emojis[letter]} '
			else:
				for translation in translations:
					if match(translation, letter):
						result += f'{translations[translation](letter)} '
						break

				else:
					result += f'{letter} '

		await interaction.response.send_message(result, ephemeral=ephemeral)


	# replace
	@app_commands.command()
	@app_commands.checks.cooldown(5, 5.0)
	@app_commands.rename(replacing='reemplazar', replacement='por', text='en', count='límite', ephemeral='privado')
	async def replace(self, interaction, replacing:str, replacement:str, text:str, count:int=-1, ephemeral:bool=False):
		"""
		replacing: str
			Lo que se va a reemplazar en el texto
		replacement: str
			Por lo que se va a reemplazar
		text: str
			Un texto
		count: int
			El límite de veces que se reemplazarán los caracteres
		ephemeral: bool
			Mandar un mensaje efímero (privado) o no
		"""
		await interaction.response.defer(ephemeral=ephemeral, thinking=True)
		embed = discord.Embed(title='Replace', colour=core.default_color(interaction))
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
	async def spacedtext(self, interaction, text:str, spaces:int=1, ephemeral:bool=False):
		"""
		text: str
			Texto al que se le agregarán espacios
		spaces: int
			Cantidad de espacios entre cada caracter
		ephemeral: bool
			Mandar un mensaje efímero (privado) o no
		"""
		if spaces > 30: 
			spaces = 30
		if spaces < 1:
			spaces = 1
		output = ''
		for char in text:
			output += (char + (' ' * spaces))
		await interaction.response.send_message(output, ephemeral=ephemeral)


	# vaporwave
	@app_commands.command()
	@app_commands.checks.cooldown(3, 5.0)
	@app_commands.rename(text='texto', ephemeral='privado')
	async def vaporwave(self, interaction, text:str, ephemeral:bool=False):
		"""
		text: str
			Texto a convertir a vaporwave
		ephemeral: bool
			Mandar un mensaje efímero (privado) o no
		"""
		output = ""
		other_chars = {32: 12288, 162: 65504, 163: 65505, 165: 65509, 166: 65508, 172: 65506, 175: 65507, 8361: 65510, 10629: 65375, 10630: 65376}
		for character in text:
			currentchar = ord(character)
			if 33 <= currentchar <= 126:
				output += chr(currentchar + 65248)
			elif currentchar in other_chars:
				output += chr(other_chars.get(currentchar))
			else:
				output += character
		await interaction.response.send_message(output, ephemeral=ephemeral)


	# sarcastic
	@app_commands.command()
	@app_commands.checks.cooldown(2, 2.0)
	@app_commands.rename(text='texto', ephemeral='privado')
	async def sarcastic(self, interaction, text:str, ephemeral:bool=False):
		"""
		text: str
			Texto a convertir a sArcÁStICo
		ephemeral: bool
			Mandar un mensaje efímero (privado) o no
		"""
		await interaction.response.send_message(''.join((choice((letter.lower(), letter.upper())) for letter in text)), ephemeral=ephemeral)


	# uppercase
	@app_commands.command()
	@app_commands.checks.cooldown(2, 2.0)
	@app_commands.rename(text='texto', ephemeral='privado')
	async def uppercase(self, interaction, text:str, ephemeral:bool=False):
		"""
		text: str
			Texto a convertir a MAYÚSCULAS
		ephemeral: bool
			Mandar un mensaje efímero (privado) o no
		"""
		await interaction.response.send_message(await commands.clean_content().convert(interaction, text.upper()), ephemeral=ephemeral)


	# lowercase
	@app_commands.command()
	@app_commands.checks.cooldown(2, 2.0)
	@app_commands.rename(text='texto', ephemeral='privado')
	async def lowercase(self, interaction, text:str, ephemeral:bool=False):
		"""
		text: str
			Texto a convertir a minúsculas
		ephemeral: bool
			Mandar un mensaje efímero (privado) o no
		"""
		await interaction.response.send_message(await commands.clean_content().convert(interaction, text.lower()), ephemeral=ephemeral)


	# swapcase
	@app_commands.command()
	@app_commands.checks.cooldown(2, 2.0)
	@app_commands.rename(text='texto', ephemeral='privado')
	async def swapcase(self, interaction, text:str, ephemeral:bool=False):
		"""
		text: str
			Texto a intercambiar minúsculas y mayúsculas
		ephemeral: bool
			Mandar un mensaje efímero (privado) o no
		"""
		await interaction.response.send_message(await commands.clean_content().convert(interaction, text.swapcase()), ephemeral=ephemeral)


	# capitalize
	@app_commands.command()
	@app_commands.checks.cooldown(2, 2.0)
	@app_commands.rename(text='texto', ephemeral='privado')
	async def capitalize(self, interaction, text:str, ephemeral:bool=False):
		"""
		text: str
			Texto a convertir a Capitalizar
		ephemeral: bool
			Mandar un mensaje efímero (privado) o no
		"""
		await interaction.response.send_message(await commands.clean_content().convert(interaction, text.title()), ephemeral=ephemeral)


	# reverse
	@app_commands.command()
	@app_commands.checks.cooldown(2, 2.0)
	@app_commands.rename(text='texto', ephemeral='privado')
	async def reverse(self, interaction, text:str, ephemeral:bool=False):
		"""
		text: str
			Texto a convertir a invertir
		ephemeral: bool
			Mandar un mensaje efímero (privado) o no
		"""
		await interaction.response.send_message(await commands.clean_content().convert(interaction, text[::-1]), ephemeral=ephemeral)


async def setup(bot):
	await bot.add_cog(Modtxt(bot), guilds=core.bot_guilds)
