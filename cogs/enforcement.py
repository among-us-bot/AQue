"""
Created by Epic at 10/13/20

Enforces that server owners must contact us before adding their bot to their server
"""
from main import Bot
from config import ALLOWED_GUILDS

from discord.ext.commands import Cog
from discord import Guild
from logging import getLogger


class Enforcement(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = getLogger("AQue.cogs.enforcement")

    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        if guild.id not in ALLOWED_GUILDS:
            self.logger.warning(f"Left guild with name {guild.name}")
            await guild.leave()
            return
        self.logger.info(f"Joined guild {guild.name}")


def setup(bot: Bot):
    bot.add_cog(Enforcement(bot))
