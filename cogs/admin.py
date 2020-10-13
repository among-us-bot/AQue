"""
Created by Epic at 10/13/20
"""
from main import Bot
from .api import Api
from .send_to_lobbies import SendToLobbies

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
                if channel.category_id in [guild_config["categories"]["lobby"], guild_config["categories"]["in_game"]]:
                    await channel.delete()
        send_to_lobbies: SendToLobbies = self.bot.get_cog("SendToLobbies")
        send_to_lobbies.queues = {}
        await ctx.send("Done")


def setup(bot: Bot):
    bot.add_cog(Admin(bot))
