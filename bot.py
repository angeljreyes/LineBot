import asyncio
from traceback import format_exc

import discord
from discord.ext import commands

import botdata

intents = discord.Intents.all()
intents.bans = False
intents.integrations = False
intents.webhooks = False
intents.invites = False
intents.voice_states = False

bot = commands.Bot(command_prefix=botdata.get_prefix, help_command=None, owner_id=337029735144226825, case_insensitive=True, intents=intents)

for extension in ('globalcog', 'listeners', 'modtxt', 'mod', 'util', 'fun', 'about', 'owner', 'image'):
	bot.load_extension(extension)

botdata.config_commands(bot)


@bot.event
async def on_error(event, *args, **kwargs):
	ctx = args[0]
	log = f'Ha ocurrido un error: "{ctx.message.content}" {repr(ctx.message)}'
	botdata.logger.error(f'{log}\n{format_exc()}')
	await bot.get_channel(botdata.error_logging_channel).send(f'<@{bot.owner_id}>', delete_after=30)


@bot.event
async def on_guild_join(guild):
	botdata.logger.info(f'El bot ha entrado a un servidor: {repr(guild)}')


botdata.cursor.execute(f"SELECT VALUE FROM RESOURCES WHERE KEY='{botdata.bot_mode}_token'")
token = botdata.cursor.fetchall()[0][0]
botdata.conn.commit()
bot.run(token)
del token
