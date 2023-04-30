
# Telegram-GameInfoBot

![Python Version](https://img.shields.io/badge/Python-3.11-blue)
![Pyrogram Version](https://img.shields.io/badge/Pyrogram-2.0.104-blue)

A Telegram bot that provides information about games using the IGDB API.

## Features

- Get information about any game and character by name
- Displays game title, rating, release date, platforms, genres, storyline, cover image, and link to Steam store page (if available)
- Monospace formatting for better readability
- Inline keyboard for quick access to Steam store page

## Installation

1. Clone this repository:

```sh
git clone https://github.com/barryspacezero/telegram-gameinfobot.git
```
2. Install the required Packages:
```sh
pip install -r requirements.txt
```
3. Create a new bot on Telegram using BotFather

4. Obtain the bot token from BotFather and add it to the .env file:

```sh
BOT_TOKEN=your-bot-token-here
```
5. Start the bot:
```sh
python bot.py
```
## Usage
1. Open Telegram and search for your bot.
2. Send a message in the following format:

```bash
/game <game-name>
```
The bot will display information about the game, including title, rating, release date, cover image, and link to the Steam store page (if available).

<a href="https://t.me/GameInfoBot" class="btn">Try the Game Info Bot now!</a>

## Credits
<a href="https://t.me/barryspace" class="btn">@barryspace</a>
<a href="https://t.me/EverythingSuckz" class="btn">@EverythingSuckz</a>
