"""
Created by Epic at 10/13/20
"""
from main import Bot
from config import MONGO_URI, MONGO_DATABASE
from utils import cacheable, remove_cache

from discord.ext.commands import Cog
from discord import User, Guild
from pymongo import MongoClient


class Api(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.mongo = MongoClient(host=MONGO_URI)
        self.database = self.mongo[MONGO_DATABASE]

        self.users_table = self.database["users"]
        self.bans_table = self.database["bans"]
        self.server_settings_table = self.database["server_settings"]

    @cacheable("user")
    def get_user(self, user: User):
        return self.users_table.find_one({"_id": user.id})

    @cacheable("is_banned")
    def get_ban_status(self, user: User, server: Guild):
        return self.bans_table.find_one({"user_id": user.id, "guild_id": server.id}) is None

    @cacheable("server_settings")
    def get_server_settings(self, guild: Guild):
        return self.server_settings_table.find_one({"_id": guild.id})

    def set_server_settings(self, guild: Guild, settings: dict):
        settings["_id"] = guild.id
        self.server_settings_table.insert_one(settings)
        remove_cache("server_settings", [guild])

    def delete_server_settings(self, guild: Guild):
        self.server_settings_table.delete_one({"_id": guild.id})
        remove_cache("server_settings", [guild])

    def update_server_settings(self, guild: Guild, changes: dict):
        self.server_settings_table.update_one({"_id": guild.id}, {"$set": changes})
        remove_cache("server_settings", [guild])




def setup(bot: Bot):
    bot.add_cog(Api(bot))
