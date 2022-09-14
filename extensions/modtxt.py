import asyncio
from random import choice
from re import match

import discord
from discord.ext import commands

import core
import helpsys


class Modtxt(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.send = bot.get_cog('GlobalCog').send


	# emojitext
	@commands.cooldown(5, 5.0, commands.BucketType.user)
	@commands.command(aliases=['emojitxt', 'etext', 'etxt'])
	async def emojitext(self, ctx, *, arg=None):
		if arg == None:
			await self.send(ctx, core.Warning.error('Escribe un texto para transformar a emojis'))
		else:
			arg = arg.lower()
			reg_ind = lambda letter: f':regional_indicator_{letter}:'
			result = ''
			other_emojis = {
				'?':':grey_question: ',
				'!':':grey_exclamation: '
			}
			translations = {
				r'[a-z]': lambda letter: reg_ind(letter),
				r'ñ': lambda letter: reg_ind('n'),
				r' ': lambda letter: ' '*3,
				r'[0-9]+': lambda letter: f'{letter}\ufe0f\u20e3',
			}
			for letter in arg:
				for translation in translations:
					if match(translation, letter):
						result += f'{translations[translation](letter)} '
						break

				else:				
					if letter in other_emojis:
						result += f'{other_emojis[letter]} '
						
					else:
						result += f'{letter} '

			await self.send(ctx, result)


	# replace
	@commands.cooldown(5, 5.0, commands.BucketType.user)
	@commands.command()
	async def replace(self, ctx, replacing=None, replacement=None, *, text=None):
		if None in (replacing, replacement, text):
			await self.send(ctx, embed=helpsys.get_cmd(ctx, 'replace'))
		else:
			await self.send(ctx, await commands.clean_content().convert(ctx, text.replace(replacing, replacement)))


	# spacedtext
	@commands.cooldown(2, 5.0, commands.BucketType.user)
	@commands.command(aliases=['spacetext', 'spacedtxt', 'spacetxt'])
	async def spacedtext(self, ctx, spaces=None, *, arg=None):
		if None in (spaces, arg) or not spaces.isnumeric(): 
			await self.send(ctx, embed=helpsys.get_cmd(ctx, 'spacedtext'))
		else:
			spaces = int(spaces)
			if spaces > 30: spaces = 30
			output = ''
			for i in arg:
				output += (i + (' ' * spaces))
			await self.send(ctx, output)


	# vaporwave
	@commands.cooldown(3, 5.0, commands.BucketType.user)
	@commands.command(aliases=['vapor'])
	async def vaporwave(self, ctx, *, arg='Sample text'):
		output = ""
		other_chars = {32: 12288, 162: 65504, 163: 65505, 165: 65509, 166: 65508, 172: 65506, 175: 65507, 8361: 65510, 10629: 65375, 10630: 65376}
		for character in arg:
			currentchar = ord(character)
			if 33 <= currentchar <= 126:
				output += chr(currentchar + 65248)
			elif currentchar in other_chars:
				output += chr(other_chars.get(currentchar))
			else:
				output += character
		await self.send(ctx, output)


	# sarcastic
	@commands.cooldown(2, 2.0, commands.BucketType.user)
	@commands.command()
	async def sarcastic(self, ctx, *, text='escribe algo pues'):
		await self.send(ctx, ''.join((choice((letter.lower(), letter.upper())) for letter in text)))


	# uppercase
	@commands.cooldown(2, 2.0, commands.BucketType.user)
	@commands.command()
	async def uppercase(self, ctx, *, text='escribe algo'):
		await self.send(ctx, await commands.clean_content().convert(ctx, text.upper()))


	# lowercase
	@commands.cooldown(2, 2.0, commands.BucketType.user)
	@commands.command()
	async def lowercase(self, ctx, *, text='escribe algo'):
		await self.send(ctx, await commands.clean_content().convert(ctx, text.lower()))


	# swapcase
	@commands.cooldown(2, 2.0, commands.BucketType.user)
	@commands.command()
	async def swapcase(self, ctx, *, text='escribe algo'):
		await self.send(ctx, await commands.clean_content().convert(ctx, text.swapcase()))


	# capitalize
	@commands.cooldown(2, 2.0, commands.BucketType.user)
	@commands.command()
	async def capitalize(self, ctx, *, text='escribe algo'):
		await self.send(ctx, await commands.clean_content().convert(ctx, text.title()))


	# reverse
	@commands.cooldown(2, 2.0, commands.BucketType.user)
	@commands.command()
	async def reverse(self, ctx, *, text='escribe algo'):
		await self.send(ctx, await commands.clean_content().convert(ctx, text[::-1]))


def setup(bot):
	bot.add_cog(Modtxt(bot))
