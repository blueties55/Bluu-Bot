import os
import json
import logging
from logging.config import dictConfig
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch the Discord token from .env
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")

# Load all other bot settings from settings.json
with open("settings.json", "r", encoding="utf-8") as f:
    config = json.load(f)

bot_settings = config.get("bot_settings", {})

COMMAND_PREFIX = bot_settings.get("command_prefix", "!")
DM_RESPONSE = bot_settings.get("dm_response", "")
OWNER_ROLE = bot_settings.get("owner_role", "Owner 👑")
NEW_USER_ROLES = bot_settings.get("new_user_roles", [])
CHANNELS = bot_settings.get("channels", {})

# Example channel access
ROLES_CHANNEL_ID = CHANNELS.get("roles_channel_id")
BOT_COMMANDS_CHANNEL_ID = CHANNELS.get("bot_commands_channel_id")
MINI_GAMES_CHANNEL_ID = CHANNELS.get("mini_games_channel_id")
SHOP_CHANNEL_ID = CHANNELS.get("shop_channel_id")

# Log directory setup
log_dir = './logs'
os.makedirs(log_dir, exist_ok=True)

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard": {"format": "%(levelname)-10s - %(name)-15s : %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
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
        "discord": {
            "handlers": ["console2", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Apply the logging configuration
dictConfig(LOGGING_CONFIG)