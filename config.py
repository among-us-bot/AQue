"""
Created by Epic at 10/13/20
"""
from os import environ as env

BOT_TOKEN = env["token"]
ALLOWED_GUILDS = [int(guild_id) for guild_id in env["allowed_guilds"].split("|")]
