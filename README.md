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
    cp "Example Settings Files/settings.example.json" settings.json
    ```
    Note: On Windows, you can manually copy and rename the file instead if cp doesn't work.
   
5. Open `settings.txt` in a text editor and replace the placeholders with your actual values:

   - `allowed_channel_id`: The ID of the text channel for music commands
   - `command_prefix`: Prefix for bot commands (default is ?)
   - `mentions_as_prefix`: Whether @mentions can be used as a command prefix (True or False)
   - `dm_response`: Message sent when the bot receives a DM
   - `owner_role`: Role that is assigned to only the server owner
   - `net_user_roles`: List of roles that are given to ever new member of the server
   - `channels`: List of the different required channels for different command types
   -   `roles_channel_id`: Role selection message channel
   -   `bot_commands_channel_id`: General commands channel
   -   `mini_games_channel_id`: Mini-Games channel
   -   `shop_channel_id`: Shopping commands channel

   Important: Do not change the parameter names.

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
