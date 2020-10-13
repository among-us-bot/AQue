"""
Created by Epic at 10/13/20
"""
from main import Bot
from .api import Api

from discord.ext.commands import Cog
from discord import VoiceState, Member
from asyncio import Lock
from typing import Dict, List, Any
from time import time


class SendToLobbies(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        if not hasattr(self, "queues"):
            self.queues: Dict[int, Dict[str, List[Dict[str, Any]]]] = {}
            self.queue_lock = Lock()
            self.target_lobbies = 3
            self.target_users = 10

    def get_matchmaking_type_by_id(self, channel_id, config):
        for match_type, voice_id in config.items():
            if voice_id == channel_id:
                return match_type

    @Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        guild = member.guild
        api: Api = self.bot.get_cog("Api")

        if before.channel == after.channel:
            return
        if after.channel is None:
            return

        guild_config = api.get_server_settings(guild)

        if guild_config is None:
            return

        matchmaking_type = self.get_matchmaking_type_by_id(after.channel.id, guild_config["matchmaking_channels"])
        if matchmaking_type is None:
            return

        async with self.queue_lock:
            guild_queues = self.queues.get(guild.id, {})
            game_queues = guild_queues.get(matchmaking_type, [])

            if len(game_queues) == 0:
                lobby_category = guild.get_channel(guild_config["categories"]["lobby"])
                for i in range(self.target_lobbies):
                    code = "code-here"
                    channel = await lobby_category.create_voice_channel(name=matchmaking_type + "-" + code)
                    lobby_data = {
                        "code": code,
                        "channel_id": channel,
                        "lobby_create_time": time(),
                        "game_create_time": time()
                    }
                    game_queues.append(lobby_data)
                guild_queues[matchmaking_type] = game_queues
                self.queues[guild.id] = guild_queues


def setup(bot: Bot):
    bot.add_cog(SendToLobbies(bot))
