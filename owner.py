import asyncio
from math import floor
from re import DOTALL, findall, fullmatch
from timeit import default_timer as timer

import discord
from discord.ext import commands

import botdata
import helpsys


class Owner(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.send = bot.get_cog('GlobalCog').send


	# die
	@commands.command()
	async def die(self, ctx):
		await ctx.message.add_reaction(u'\U0001f480')
		print('\nBot apagado')
		await self.bot.logout()


	# getmsg
	@commands.command()
	async def getmsg(self, ctx, id):
		print(await ctx.fetch_message(id))
		await ctx.message.add_reaction(u'\U00002705')


	# eval
	@commands.command()
	async def eval(self, ctx, *, code):
		use_embed = True
		if code.endswith(' -s'):
			code = code[:-3]
			use_embed = False

		if fullmatch(r'```.+```', code, flags=DOTALL):
			code = code[len(code.splitlines()[0]):-4]
		
		if use_embed:
			return_line = findall(r'[^ ].+$', code.splitlines()[-1])[0]
			code = code[:-(len(return_line))] + f'botdata.returned_value = {return_line}'

		code = '''@self.bot.command()\nasync def evalcmd(ctx):\n    '''+code.replace('\n','\n    ')
		try:
			exec(code)
			start = timer()
			await self.bot.get_command('evalcmd').__call__(ctx)
			end = timer()
			if use_embed:
				types = ''
				returned_value = botdata.returned_value
				while True:
					try:
						types += str(type(returned_value))
						if not isinstance(returned_value, str):
							iter(returned_value)
						else:
							raise TypeError
					except TypeError:
						break
					else:
						try:
							if len(returned_value) == 0:
								break
							returned_value = returned_value[0]
						except (TypeError, KeyError):
							returned_value = tuple(returned_value)[0]

				await self.send(ctx, embed=discord.Embed(
					title='Resultados del eval',
					description=f'Tipo de dato y resultado:\n```py\n{types}\n```\n```py\n{botdata.returned_value}\n```',
					colour=botdata.default_color(ctx)
				).set_footer(text=f'Ejecutado en {floor((end - start) * 1000)}ms'))
				botdata.returned_value = None
		finally:
			try:
				await self.bot.remove_command('evalcmd')
			except TypeError:
				pass


	# reload
	@commands.command()
	async def reload(self, ctx, extension=''):
		self.bot.reload_extension(extension)
		botdata.config_commands(self.bot)
		await ctx.message.add_reaction(u'\U00002705')


	# unload
	@commands.command()
	async def unload(self, ctx, extension=''):
		self.bot.unload_extension(extension)
		await ctx.message.add_reaction(u'\U00002705')


	# load
	@commands.command()
	async def load(self, ctx, extension=''):
		self.bot.load_extension(extension)
		botdata.config_commands(self.bot)
		await ctx.message.add_reaction(u'\U00002705')


	# blacklist
	@commands.command()
	async def blacklist(self, ctx, *, user):
		user = await botdata.get_user(ctx, user)
		if botdata.check_blacklist(ctx, user, False):
			botdata.cursor.execute(f"INSERT INTO BLACKLIST VALUES({user.id})")
			await ctx.message.add_reaction(u'\U00002935')
		
		else:
			botdata.cursor.execute(f"DELETE FROM BLACKLIST WHERE USER={user.id}")
			await ctx.message.add_reaction(u'\U00002934')

		botdata.conn.commit()


def setup(bot):
	bot.add_cog(Owner(bot))
