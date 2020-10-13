"""
Created by Epic at 10/13/20
"""
from os import environ as env

# Generic
BOT_TOKEN = env["token"]
ALLOWED_GUILDS = [int(guild_id) for guild_id in env["allowed_guilds"].split("|")]

# Mongo
MONGO_URI = env["mongo_uri"]
MONGO_DATABASE = env["mongo_database"]

# Redis
REDIS_HOST = env["redis_host"]
REDIS_DB = int(env.get("redis_db", 0))
REDIS_PASSWORD = env.get("redis_password", None)
REDIS_USERNAME = env.get("redis_username", None)
