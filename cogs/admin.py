"""
Created by Epic at 10/13/20
"""
from main import Bot
from .api import Api
from .queue import Queue

from discord.ext.commands import Cog, is_owner, command


class Admin(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    @is_owner()
    async def cleanup(self, ctx):
        api: Api = self.bot.get_cog("Api")
        for guild_config in api.server_settings_table.find():
            guild = self.bot.get_guild(guild_config["_id"])
            if guild is None:
                continue
            channels_copy = guild.channels.copy()
            for channel in channels_copy:
                if channel.category_id == guild_config["categories"]["lobby"] or getattr(channel.category, "name",
                                                                                         None) == "In Game!":
                    await channel.delete()
        queue: Queue = self.bot.get_cog("Queue")
        queue.locks = {}
        queue.lobby_channels = {}
        await ctx.send("Done")

    @command()
    @is_owner()
    async def toggle_queue(self, ctx):
        queue: Queue = self.bot.get_cog("Queue")
        queue.is_queue_enabled = not queue.is_queue_enabled
        await ctx.send("Toggled queue. Queue is currently: " + ["disabled", "enabled"][queue.is_queue_enabled])

def setup(bot: Bot):
    bot.add_cog(Admin(bot))
