"""
Created by Epic at 10/13/20
"""
from config import BOT_TOKEN
from colorformat import basicConfig

from discord.ext.commands import AutoShardedBot, MinimalHelpCommand
from pathlib import Path
from logging import getLogger, DEBUG


class Bot(AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help_command = MinimalHelpCommand()
        self.logger = getLogger("AQue")
        self.logger.setLevel(DEBUG)
        basicConfig(self.logger)
        self.load_extension("jishaku")
        self.load_cogs()

    def load_cogs(self):
        cogs_dir = Path("./cogs/")
        for cog in cogs_dir.glob("*.py"):
            cog_name = "cogs." + str(cog).split("/")[-1]
            try:
                self.unload_extension(cog_name)
            except:
                pass
            try:
                self.load_extension(cog_name)
            except Exception as e:
                self.logger.error("A error occured while loading a cog", exc_info=e)


bot = Bot("/")
bot.run(BOT_TOKEN)
