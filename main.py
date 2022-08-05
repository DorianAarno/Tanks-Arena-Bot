from asyncio import tasks
from disnake import *
from disnake.ext import commands
import os, traceback
import aiosqlite
from random import randint


class MyBot(commands.InteractionBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.db = None

    # async def db_main(self):
    #     self.db = await aiosqlite.connect("main.sqlite")
    #     print("Main DataBase Connected")

    async def commit(self):
        async with aiosqlite.connect("main.sqlite") as db:
            await db.commit()

    async def execute(self, query, *values):
        async with aiosqlite.connect("main.sqlite") as db:
            async with db.cursor() as cur:
                await cur.execute(query, tuple(values))
            await db.commit()

    async def executemany(self, query, values):
        async with aiosqlite.connect("main.sqlite") as db:
            async with db.cursor() as cur:
                await cur.executemany(query, values)
            await db.commit()

    async def fetchval(self, query, *values):
        async with aiosqlite.connect("main.sqlite") as db:
            async with db.cursor() as cur:
                exe = await cur.execute(query, tuple(values))
                val = await exe.fetchone()
            return val[0] if val else None

    async def fetchrow(self, query, *values):
        async with aiosqlite.connect("main.sqlite") as db:
            async with db.cursor() as cur:
                exe = await cur.execute(query, tuple(values))
                row = await exe.fetchmany(size=1)
            if len(row) > 0:
                row = [r for r in row[0]]
            else:
                row = None
            return row

    async def fetchmany(self, query, size, *values):
        async with aiosqlite.connect("main.sqlite") as db:
            async with db.cursor() as cur:
                exe = await cur.execute(query, tuple(values))
                many = await exe.fetchmany(size)
            return many

    async def fetch(self, query, *values):
        async with aiosqlite.connect("main.sqlite") as db:
            async with db.cursor() as cur:
                exe = await cur.execute(query, tuple(values))
                all = await exe.fetchall()
            return all

    def determine_stats(self, tank_stats_range: dict, advantage: str):
        def decrease_highTQ_chances(ignore_stat: str):
            hp_max = tank_stats_range["HP"]["max"]
            atk_max = tank_stats_range["ATTACK"]["max"]
            def_max = tank_stats_range["DEFENCE"]["max"]

            if ignore_stat != "HP":
                hp = hp_max - ((30 / 100) * hp_max)
            else:
                hp = hp_max

            if ignore_stat != "ATTACK":
                attack = atk_max - ((30 / 100) * atk_max)
            else:
                attack = atk_max

            if ignore_stat != "DEFENCE":
                defence = def_max - ((30 / 100) * def_max)
            else:
                defence = def_max

            if randint(0, 9):  # If number between 1-9
                return (round(hp), round(attack), round(defence))
            else:  # If number is 0
                return (hp_max, atk_max, def_max)

        max_ranges = decrease_highTQ_chances(advantage)

        hp = randint(tank_stats_range["HP"]["min"], max_ranges[0])
        attack = randint(tank_stats_range["ATTACK"]["min"], max_ranges[1])
        defence = randint(tank_stats_range["DEFENCE"]["min"], max_ranges[2])

        return (hp, attack, defence)

    def get_TQ(self, tank_stats_range: dict, hp, defence, attack):
        tank_quality = (
            (hp + defence + attack)
            / (
                tank_stats_range["HP"]["max"]
                + tank_stats_range["ATTACK"]["max"]
                + tank_stats_range["DEFENCE"]["max"]
            )
        ) * 100
        return tank_quality


bot = MyBot(intents=Intents.default())


async def setuptable(bot):
    await bot.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER,
            money INTEGER,
            PRIMARY KEY("user_id")
        )
        """
    )
    await bot.execute(
        """
        CREATE TABLE IF NOT EXISTS user_tanks(
            user_id INTEGER, 
            tank_type TEXT,
            serial INTEGER,  
            hp INTEGER, 
            atk INTEGER, 
            def INTEGER
        )
        """
    )


@bot.event
async def on_ready():
    print("*********\nBot is Ready.\n*********")
    await setuptable(bot)


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
