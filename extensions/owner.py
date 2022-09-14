import asyncio
from math import floor
from re import DOTALL, findall, fullmatch
from timeit import default_timer as timer

import discord
from discord.ext import commands

import core
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
				returned_value = core.returned_value
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
					description=f'Tipo de dato y resultado:\n```py\n{types}\n```\n```py\n{core.returned_value}\n```',
					colour=core.default_color(ctx)
				).set_footer(text=f'Ejecutado en {floor((end - start) * 1000)}ms'))
				core.returned_value = None
		finally:
			try:
				await self.bot.remove_command('evalcmd')
			except TypeError:
				pass


	# reload
	@commands.command()
	async def reload(self, ctx, extension=''):
		self.bot.reload_extension(extension)
		core.config_commands(self.bot)
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
		core.config_commands(self.bot)
		await ctx.message.add_reaction(u'\U00002705')


	# blacklist
	@commands.command()
	async def blacklist(self, ctx, *, user):
		user = await core.get_user(ctx, user)
		if core.check_blacklist(ctx, user, False):
			core.cursor.execute(f"INSERT INTO BLACKLIST VALUES({user.id})")
			await ctx.message.add_reaction(u'\U00002935')
		
		else:
			core.cursor.execute(f"DELETE FROM BLACKLIST WHERE USER={user.id}")
			await ctx.message.add_reaction(u'\U00002934')

		core.conn.commit()


	#button_test
	@commands.command()
	async def test(self, ctx):
		components = [
			discord.ActionRow(
				discord.ui.Button(label='Botón 1', custom_id='1', style=discord.ButtonStyle.green),
				discord.ui.Button(label='Botón 2', custom_id='2', style=discord.ButtonStyle.blurple, emoji='👁')
			),
			discord.ActionRow(
				discord.ui.Button(label='Botón 3', custom_id='3', style=discord.ButtonStyle.blurple, emoji=(await commands.PartialEmojiConverter().convert(ctx, '<:yerkoturbio:840259087496118352>'))),
				discord.ui.Button(label='Botón 4', custom_id='4', style=discord.ButtonStyle.red, emoji='4️⃣'),
				discord.ui.Button(label='Botón 5', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ')
			)
		]
		msg = await ctx.send(embed=discord.Embed(title='Qqqq', description='loo'), components=components)
		interaction: discord.RawInteractionCreateEvent = await self.bot.wait_for('interaction_create', check=lambda i: ctx.author == i.member and msg == i.message)
		interaction.defer()
		await interaction.edit(embed=discord.Embed(title='ok', description=interaction.button.emoji), components=[components[0].disable_all_buttons(), components[1].disable_all_buttons()])


def setup(bot):
	bot.add_cog(Owner(bot))
