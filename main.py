from disnake import *
from disnake.ext import commands
import os, traceback
import aiosqlite

class MyBot(commands.InteractionBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = None

    async def db_main(self):
        self.db = await aiosqlite.connect("main.sqlite")
        print("Main DataBase Connected")

    async def commit(self):
        await self.db.commit()

    async def execute(self, query, *values):
        async with self.db.cursor() as cur:
            await cur.execute(query, tuple(values))
        await self.commit()

    async def executemany(self, query, values):
        async with self.db.cursor() as cur:
            await cur.executemany(query, values)
        await self.commit()

    async def fetchval(self, query, *values):
        async with self.db.cursor() as cur:
            exe = await cur.execute(query, tuple(values))
            val = await exe.fetchone()
        return val[0] if val else None

    async def fetchrow(self, query, *values):
        async with self.db.cursor() as cur:
            exe = await cur.execute(query, tuple(values))
            row = await exe.fetchmany(size=1)
        if len(row) > 0:
            row = [r for r in row[0]]
        else:
            row = None
        return row

    async def fetchmany(self, query, size, *values):
        async with self.db.cursor() as cur:
            exe = await cur.execute(query, tuple(values))
            many = await exe.fetchmany(size)
        return many

    async def fetch(self, query, *values):
        async with self.db.cursor() as cur:
            exe = await cur.execute(query, tuple(values))
            all = await exe.fetchall()
        return all


bot = MyBot(intents=Intents.default())


@bot.event
async def on_ready():
    print("*********\nBot is Ready.\n*********")


# bot.remove_command('help')


@bot.slash_command()
async def ping(ctx):
    await ctx.send(f"📶 {round(bot.latency * 1000)}ms")


# @bot.event
# async def on_command_error(ctx,error):
#     if isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
#         return
#     else:
#         print

for file in os.listdir("./cogs"):
    if file.endswith(".py") and file != "__init__.py":
        try:
            bot.load_extension("cogs." + file[:-3])
            print(f"{file[:-3]} Loaded successfully.")
        except:
            print(f"Unable to load {file[:-3]}.")
            print(traceback.format_exc())


bot.run("MTAwMzk1NDc3OTM0NjcxODcyMA.GvdCkj.bfHjQKiRlkzRTm1KdRSXUV0-Sug4P58aaC_UFM")
