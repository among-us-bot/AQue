"""
Created by Epic at 10/13/20
"""
from config import BOT_TOKEN
from colorformat import basicConfig

from discord.ext.commands import Bot as BaseBot, MinimalHelpCommand
from discord import Intents
from pathlib import Path
from logging import getLogger, DEBUG


class Bot(BaseBot):
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
            cog_name = "cogs." + str(cog).split("/")[-1][:-3]
            try:
                self.unload_extension(cog_name)
            except:
                pass
            try:
                self.load_extension(cog_name)
                self.logger.debug(f"Loaded cog {cog_name}")
            except Exception as e:
                self.logger.error("A error occured while loading a cog", exc_info=e)


intents = Intents(guilds=True, voice_states=True, messages=True)
if __name__ == "__main__":
    bot = Bot("/", intents=intents)
    bot.run(BOT_TOKEN)
