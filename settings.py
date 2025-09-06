import os
import logging
from logging.config import dictConfig
from dotenv import load_dotenv
import asyncio
import asyncpg
import json

# -----------------------
# Environment Variables
# -----------------------
load_dotenv()

DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")
PG_USER = os.getenv("DB_USER")
PG_PASSWORD = os.getenv("DB_PASSWORD")
PG_DATABASE = os.getenv("DB_NAME")
PG_HOST = os.getenv("DB_HOST", "localhost")
PG_PORT = int(os.getenv("DB_PORT", 5432))

# -----------------------
# Logging Configuration
# -----------------------
log_dir = './logs'
os.makedirs(log_dir, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"},
        "standard": {"format": "%(levelname)-10s - %(name)-15s : %(message)s"},
    },
    "handlers": {
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "standard"},
        "console2": {"level": "WARNING", "class": "logging.StreamHandler", "formatter": "standard"},
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(log_dir, "infos.log"),
            "mode": "w",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "bot": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "discord": {"handlers": ["console2", "file"], "level": "INFO", "propagate": False},
    },
}

dictConfig(LOGGING_CONFIG)

# -----------------------
# Database Connection
# -----------------------
pool = None

async def init_db():
    """Initialize the asyncpg connection pool."""
    global pool
    pool = await asyncpg.create_pool(
        user=PG_USER,
        password=PG_PASSWORD,
        database=PG_DATABASE,
        host=PG_HOST,
        port=PG_PORT,
    )

async def load_bot_settings():
    """Load bot settings from the database."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM bot_settings WHERE id = 1;")
        if not row:
            raise ValueError("No settings found in bot_settings table!")
        
        # Parse JSON fields
        channels = row["channels"]
        if isinstance(channels, str):
            channels = json.loads(channels)

        new_user_roles = row["new_user_roles"]
        if isinstance(new_user_roles, str):
            new_user_roles = json.loads(new_user_roles)

        return {
            "COMMAND_PREFIX": row["command_prefix"],
            "DM_RESPONSE": row["dm_response"],
            "OWNER_ROLE": row["owner_role"],
            "NEW_USER_ROLES": new_user_roles,  # list
            "CHANNELS": channels,              # dict
        }


# -----------------------
# Global settings variables
# -----------------------
COMMAND_PREFIX = None
DM_RESPONSE = None
OWNER_ROLE = None
NEW_USER_ROLES = None
CHANNELS = None
ROLES_CHANNEL_ID = None
BOT_COMMANDS_CHANNEL_ID = None
MINI_GAMES_CHANNEL_ID = None
SHOP_CHANNEL_ID = None

# -----------------------
# Initialization function
# -----------------------
async def init_settings():
    """Call this once at bot startup to load settings from DB."""
    await init_db()
    settings = await load_bot_settings()

    global COMMAND_PREFIX, DM_RESPONSE, OWNER_ROLE, NEW_USER_ROLES
    global CHANNELS, ROLES_CHANNEL_ID, BOT_COMMANDS_CHANNEL_ID, MINI_GAMES_CHANNEL_ID, SHOP_CHANNEL_ID

    COMMAND_PREFIX = settings["COMMAND_PREFIX"]
    DM_RESPONSE = settings["DM_RESPONSE"]
    OWNER_ROLE = settings["OWNER_ROLE"]
    NEW_USER_ROLES = settings["NEW_USER_ROLES"]
    CHANNELS = settings["CHANNELS"]

    ROLES_CHANNEL_ID = CHANNELS.get("roles_channel_id")
    BOT_COMMANDS_CHANNEL_ID = CHANNELS.get("bot_commands_channel_id")
    MINI_GAMES_CHANNEL_ID = CHANNELS.get("mini_games_channel_id")
    SHOP_CHANNEL_ID = CHANNELS.get("shop_channel_id")