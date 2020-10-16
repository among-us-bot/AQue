"""
Created by Epic at 10/16/20
"""
from main import Bot
from .api import Api

from discord.ext.commands import Cog, command, Context


class Verification(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def link(self, ctx: Context, ign: str):
        api: Api = self.bot.get_cog("Api")
        guild_config = api.get_server_settings(ctx.guild)
        if guild_config is None:
            return await ctx.send("Please wait while the staff is setting me up :)")
        configured_role = ctx.guild.get_role(guild_config["roles"]["configured"])
        if configured_role is None:
            return await ctx.send("The server staff has disabled this. Sorry!")

        user = api.get_user(ctx.author)
        if user is None:
            user = {}
            api.create_user(ctx.author, {})

        if user.get("ign", None) is not None:
            return await ctx.send(f"{ctx.author.mention}, You have already linked a account. "
                                  f"Please contact the staff if you need it changed")
        user["ign"] = ign
        api.update_user(ctx.author, user)
        await ctx.author.add_roles(configured_role, reason=f"[AQue] User verified with IGN: {ign}")
        await ctx.send("Linked!")


def setup(bot: Bot):
    bot.add_cog(Verification(bot))
