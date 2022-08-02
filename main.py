from disnake import *
from disnake.ext import commands
import os, traceback

bot = commands.InteractionBot(intents=Intents.default())

@bot.event
async def on_ready():
    print('*********\nBot is Ready.\n*********')

# bot.remove_command('help')

@bot.slash_command()
async def ping(ctx):
    await ctx.send (f"📶 {round(bot.latency * 1000)}ms")

# @bot.event
# async def on_command_error(ctx,error):
#     if isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
#         return
#     else:
#         print

for file in os.listdir('./cogs'):
    if file.endswith('.py') and file != '__init__.py':
        try:
            bot.load_extension("cogs."+file[:-3])
            print(f"{file[:-3]} Loaded successfully.")
        except:
            print(f"Unable to load {file[:-3]}.")
            print(traceback.format_exc())

bot.run("MTAwMzk1NDc3OTM0NjcxODcyMA.GvdCkj.bfHjQKiRlkzRTm1KdRSXUV0-Sug4P58aaC_UFM")
