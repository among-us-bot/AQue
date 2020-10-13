"""
Created by Epic at 10/13/20
"""
from main import Bot
from asyncio import Lock

from discord.ext.commands import Cog, command, Context, has_permissions
from discord import PermissionOverwrite


class Setup(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.setup_lock = Lock()

    @command()
    @has_permissions(manage_guild=True)
    async def setup(self, ctx: Context):
        async with self.setup_lock:
            api = self.bot.get_cog("Api")
            old_settings = api.get_server_settings(ctx.guild)
            if old_settings is not None:
                return await ctx.send("This server is already configured. Join the support server for help")
            async with ctx.typing():
                # Creating roles
                configured_user_role = await ctx.guild.create_role(name="AQue verified")
                banned_user_role = await ctx.guild.create_role(name="AQue banned")

                roles = {
                    "configured": configured_user_role.id,
                    "banned": banned_user_role.id
                }

                matchmaking_category_permissions = {
                    configured_user_role: PermissionOverwrite(read_messages=True),
                    ctx.guild.default_role: PermissionOverwrite(read_messages=False)
                }

                matchmaking_category = await ctx.guild.create_category(name="Matchmaking! Join to queue!",
                                                                       overwrites=matchmaking_category_permissions)
                matchmaking_na_normal = await matchmaking_category.create_voice_channel(name="NA-Normal")
                matchmaking_eu_normal = await matchmaking_category.create_voice_channel(name="EU-Normal")
                matchmaking_asia_normal = await matchmaking_category.create_voice_channel(name="ASIA-Normal")

                matchmaking_channels = {
                    "na-normal": matchmaking_na_normal.id,
                    "eu-normal": matchmaking_eu_normal.id,
                    "asia-normal": matchmaking_asia_normal.id
                }

                lobby_category = await ctx.guild.create_category("Lobby! Waiting for players")
                in_game_category = await ctx.guild.create_category("In game! Leave when you are done")

                categories = {
                    "matchmaking": matchmaking_category.id,
                    "lobby": lobby_category.id,
                    "in_game": in_game_category.id
                }

                config = {
                    "roles": roles,
                    "matchmaking_channels": matchmaking_channels,
                    "categories": categories
                }
                api.set_server_settings(ctx.guild, config)
                await ctx.send("Done! Contact support if something isn't working!")


def setup(bot: Bot):
    bot.add_cog(Setup(bot))
