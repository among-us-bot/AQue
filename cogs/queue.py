"""
Created by Epic at 10/14/20
"""
from main import Bot
from utils import get_matchmaking_type_by_id
from config import DEFAULT_LOBBY_USER_REQUIREMENT, DEFAULT_LOBBY_DELETION_THRESHOLD
from .api import Api
from .analytics import Analytics

from discord.ext.commands import Cog
from discord.ext.tasks import loop
from discord import VoiceState, Member, Guild, PermissionOverwrite, HTTPException
from asyncio import Lock
from typing import Dict
from logging import getLogger


class Queue(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = getLogger("AQue.cogs.queue")
        self.locks: Dict[int, Dict[str, Lock]] = {}
        self.lobby_channels: Dict[int, Dict[str, int]] = {}
        self.game_channels = []
        self.is_queue_enabled = True
        self.in_matchmaking = 0
        self.waiting_for_game = 0

    def is_lobby_vc(self, channel: int, guild_id: int):
        return any([channel_id == channel for channel_id in list(self.lobby_channels[guild_id].values())])

    async def get_game_category(self, guild: Guild):
        for channel in guild.channels:
            if channel.name != "In Game!":
                continue
            if len(channel.channels) == 50:
                continue
            return channel
        overrides = {
            guild.default_role: PermissionOverwrite(view_channel=False)
        }
        return await guild.create_category_channel(name="In Game!", overwrites=overrides,
                                                   reason="[AQue] Automatically scaled categories")

    async def clean_up_categories(self, guild: Guild):
        channels = guild.channels.copy()
        category_count = 0
        for channel in channels:
            if channel.name == "In Game!" and len(channel.channels) == 0:
                category_count += 1
                if category_count == 1:
                    continue
                self.logger.debug(category_count)
                await channel.delete(reason="[AQue] Automatically scaled categories")

    @Cog.listener("on_voice_state_update")
    async def move_to_lobbies(self, member: Member, before: VoiceState, after: VoiceState):
        if before.channel == after.channel or after.channel is None or member.bot:
            return
        guild = member.guild
        api: Api = self.bot.get_cog("Api")
        analytics: Analytics = self.bot.get_cog("Analytics")
        guild_config = api.get_server_settings(guild)

        if guild_config is None:
            return
        match_type = get_matchmaking_type_by_id(after.channel.id, guild_config["matchmaking_channels"])
        if match_type is None:
            return
        self.in_matchmaking += 1
        analytics.update_metric("in_matchmaking", "How many people is in the matchmaking channels",
                                self.in_matchmaking)
        guild_locks = self.locks.get(guild.id, None)
        if guild_locks is None:
            guild_locks = {}
            self.locks[guild.id] = {}
        game_lock = guild_locks.get(match_type, None)
        if game_lock is None:
            game_lock = Lock()
            self.locks[guild.id][match_type] = game_lock
        if not self.is_queue_enabled:
            await member.move_to(None, reason="[AQue] Queue is disabled.")
            return
        async with game_lock:
            await self.clean_up_categories(guild)
            guild_lobbies = self.lobby_channels.get(guild.id, {})
            lobby_vc = guild_lobbies.get(match_type, None)
            if lobby_vc is None:
                lobby_category = self.bot.get_channel(guild_config["categories"]["lobby"])
                lobby_vc = (await lobby_category.create_voice_channel(name=match_type)).id
                guild_lobbies[match_type] = lobby_vc
                self.lobby_channels[guild.id] = guild_lobbies
            voice = self.bot.get_channel(lobby_vc)
            await member.move_to(voice, reason="[AQue] Assembling lobby")
            self.in_matchmaking -= 1
            analytics.update_metric("in_matchmaking", "How many people is in the matchmaking channels",
                                    self.in_matchmaking)
            self.waiting_for_game += 1
            analytics.update_metric("waiting_for_game", "How many people are waiting in the lobby channels",
                                    self.in_matchmaking)

    @Cog.listener("on_voice_state_update")
    async def start_games(self, member: Member, before: VoiceState, after: VoiceState):
        if before.channel == after.channel or after.channel is None or member.bot:
            return

        guild = member.guild
        api: Api = self.bot.get_cog("Api")
        guild_config = api.get_server_settings(guild)

        if guild_config is None:
            return
        lobby_category_id = guild_config["categories"]["lobby"]
        voice_channel = after.channel

        if voice_channel.category_id != lobby_category_id:
            return
        game_type = voice_channel.name
        async with self.locks[guild.id][game_type]:
            voice_channel = self.bot.get_channel(voice_channel.id)  # Refresh it
            lobby_users = guild_config["lobby_config"].get(game_type, {}).get("lobby_size",
                                                                              DEFAULT_LOBBY_USER_REQUIREMENT)
            if len(voice_channel.members) < lobby_users:
                return
            category = await self.get_game_category(guild)
            game_voice = await category.create_voice_channel(name="Use /code <code>", reason="[AQue] Lobby found")
            members_to_move = voice_channel.members[:lobby_users]
            moved = 0
            for member in members_to_move:
                try:
                    await member.move_to(game_voice, reason="[AQue] Moving to lobby")
                    moved += 1
                    user_data = api.get_user(member)
                    if user_data is None:
                        continue
                    ign = user_data.get("ign", None)
                    if ign is not None:
                        await member.edit(nick=ign)
                except HTTPException:
                    pass
            self.waiting_for_game -= moved
            analytics: Analytics = self.bot.get_cog("Analytics")
            analytics.update_metric("waiting_for_game", "How many people are waiting in the lobby channels",
                                    self.in_matchmaking)

    @Cog.listener("on_voice_state_update")
    async def delete_lobbies_on_empty(self, member: Member, before: VoiceState, after: VoiceState):
        if after.channel is not None and before.channel != after.channel and not member.bot:
            return
        guild = member.guild
        api: Api = self.bot.get_cog("Api")
        guild_config = api.get_server_settings(guild)

        if guild_config is None:
            return
        if before.channel.category.name != "In Game!":
            return
        await member.edit(nick=None)
        lobby_deletion_threshold = guild_config.get("lobby_deletion_threshold", DEFAULT_LOBBY_DELETION_THRESHOLD)
        if len(before.channel.members) <= lobby_deletion_threshold:
            await before.channel.delete(reason="[AQue] Lobby is empty.")


def setup(bot: Bot):
    bot.add_cog(Queue(bot))
