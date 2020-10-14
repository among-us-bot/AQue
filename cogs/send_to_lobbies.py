"""
Created by Epic at 10/13/20
"""
from main import Bot
from .api import Api

from discord.ext.commands import Cog
from discord import VoiceState, Member, VoiceChannel
from asyncio import Lock, sleep
from typing import Dict, List, Any
from time import time
from random import choice


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
                    channel = await lobby_category.create_voice_channel(name="Use /code <code>")
                    lobby_data = {
                        "code": code,
                        "channel_id": channel.id,
                        "lobby_create_time": time(),
                        "game_create_time": time(),
                        "game_size": self.target_users,
                        "has_set_code": False
                    }
                    game_queues.append(lobby_data)
                guild_queues[matchmaking_type] = game_queues
                self.queues[guild.id] = guild_queues

            for lobby in game_queues:
                lobby_channel: VoiceChannel = self.bot.get_channel(lobby["channel_id"])
                if len(lobby_channel.members) > len(lobby["game_size"]):
                    continue
                await member.move_to(lobby_channel, reason="Queue")
                return

            try:
                await member.send("We are seing a ton of people queueing at the moment. Please try again later.")
            except:
                pass


def setup(bot: Bot):
    bot.add_cog(SendToLobbies(bot))
