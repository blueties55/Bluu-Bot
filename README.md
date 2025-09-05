# Bluu Bot

Bluu Bot is a Discord bot that brings fun and engagement to your server with mini-games, an economy system, and role-based interactions.

## Features

- 🎲 Mini-games:
  - Rock Paper Scissors
  - Higher or Lower
  - Coin Flip
  - Roulette
  - Tic-Tac-Toe
- 💰 Economy system with coins and items
- 🔐 Optional role-based commands
- 📩 Customizable direct message responses
- 🏷️ Role shop for VIPs and event roles

## Prerequisites

Ensure you have the following installed:

- Python 3.10 or higher  
- pip (Python package installer)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/<your-username>/bluu-bot.git
   cd bluu-bot
2. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Copy the example configuration settings files:

    ```bash
    cp "Example Settings Files/settings.example.txt" settings.txt
    cp "Example Settings Files/auto_responses_settings.example.txt" auto_responses_settings.txt
    cp "Example Settings Files/role_selection_settings.example.txt" role_selection_settings.txt
    cp "Example Settings Files/shop_settings.example.txt" shop_settings.txt
    cp "Example Settings Files/OpenAIConfig.example.yml" OpenAIConfig.yml
    ```
    Note: On Windows, you can manually copy and rename the file instead if cp doesn't work.
   
5. Open `settings.txt` in a text editor and replace the placeholders with your actual values:

   - `DISCORD_API_TOKEN`: Your Discord bot token
   - `allowed_channel_id`: The ID of the text channel for music commands
   - `command_prefix`: Prefix for bot commands (default is ?)
   - `mentions_as_prefix`: Whether @mentions can be used as a command prefix (True or False)
   - `dm_response`: Message sent when the bot receives a DM

   Important: Do not change the parameter names (everything before the = sign).

Usage
-----

Run the bot with:

   ```bash
   python main.py
   ```

The bot will log in and load all cogs. It will only respond to commands in the channel specified by allowed_channel_id.

Commands
--------

- `?rps <rock|paper|scissors>` – Play Rock Paper Scissors
- `?higherlower <bet>` – Play Higher or Lower
- `?coinflip <bet>` – Flip a coin
- `?roulette <bet>` – Play Roulette
- `?tictactoe <@opponent>` – Play Tic-Tac-Toe
- `?balance` – Show your current coin balance
- `?shop` – View the item/role shop
- `?buy <item>` – Purchase an item or role

Note: Some commands may require certain roles or sufficient coins.

Contributing
------------

Contributions are welcome! Fork the repository, make your changes, and submit a pull request.
Ensure your code follows the existing style and includes appropriate testing.

License
-------

Bluu Music Bot is open-source software licensed under the MIT License.
