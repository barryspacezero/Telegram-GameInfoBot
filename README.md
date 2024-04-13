
# Telegram-GameInfoBot

![Python Version](https://img.shields.io/badge/Python-3.11-blue)
![Pyrogram Version](https://img.shields.io/badge/Pyrogram-2.0.104-blue)

A Telegram bot that provides information about games using the IGDB API.

## Features

- Game search: Users can search for games by name and get detailed information about the game, including release date, genres, platforms, rating, and more.
- Character information: Users can retrieve information about a specific character, including name, description, gender, species, and additional details.
- Screenshots: Users can request screenshots of a specific game to get a visual preview.
- Artworks: Users can request artworks of a game to explore the visual elements.
- Top-rated games: Users can get a list of the top-rated games based on ratings and popularity.

## How to Use

1. Start the bot by searching for "@TheGameInfoBot" on Telegram or by clicking [here](https://t.me/TheGameIntoBot).
2. Use the following commands to interact with the bot:
   - `/start`: Displays a welcome message and provides basic information about the bot.
   - `/help`: Provides a list of available commands and their usage instructions.
   - `/game <game name>`: Retrieves detailed information about a specific game.
   - `/character <character name>`: Retrieves information about a specific character.
   - `/ss <game name>`: Sends a screenshot of a specific game.
   - `/art <game name>`: Sends an artwork of a specific game.
   - `/top`: Retrieves a list of the top-rated games.

## Development

To set up the development environment and run the bot locally, follow these steps:

1. Clone the repository:
```git clone https://github.com/your-username/igdb-telegram-bot.git```

2. Install the required dependencies:
```
cd igdb-telegram-bot
pip install -r requirements.txt
```

3. Obtain the necessary credentials:
- Register and create an application on the <a href="https://dev.twitch.tv/console/apps/create" class="btn">Twitch Dev Console</a> to obtain the Client ID and secret credentials.
- Make a POST request to ```https://id.twitch.tv/oauth2/token``` with the following query string parameters, substituting your Client ID and Client Secret accordingly to get the Auth token.
```client_id=Client ID```
```client_secret=Client Secret```
```grant_type=client_credentials```
- Create a new Telegram bot and obtain the bot token.

4. Set up the environment variables:
- Create a `.env` file in the project root directory.
- Add the following environment variables to the file:
  ```
  CLIENT_ID=your_igdb_client_id
  CLIENT_TOKEN=your_igdb_client_token
  API_ID=your_telegram_api_id
  API_HASH=your_telegram_api_hash
  BOT_TOKEN=your_telegram_bot_token
  REDIS_PASSWORD=password
  REDIS_PORT=port
  REDIS_HOST=host
  ```

5. Run the bot:
```
python bot.py
```

<a href="https://t.me/TheGameInfoBot" class="btn">Try the Game Info Bot now!</a>


## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Credits
<a href="https://t.me/barryspace" class="btn">@barryspace</a>
<a href="https://t.me/EverythingSuckz" class="btn">@EverythingSuckz</a>
<a href="https://t.me/Qewertyy" class="btn">@Qewertyy</a>
