from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import json
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

import dotenv
import logging
from os import getenv

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.INFO)

client_id= getenv("CLIENT_ID")
access_token= getenv("CLIENT_TOKEN")

bot = Client(
    name='igdb_bot',
    api_id=getenv("API_ID"),
    api_hash=getenv("API_HASH"),
    bot_token=getenv("BOT_TOKEN")
)

@bot.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply("Hello, this bot can send game info and character info. Send /help to get more info.")

@bot.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply("Send /game `'game name'` to get info about a game.\nSend /character `'character name'` to get info about a character.")

#function to get game info and save it in key-value pairs
def search(query: str) -> dict:
    url = f"https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }
    data = f"search \"{query}\"; fields name,url,genres.name,summary,platforms.name,websites.category,websites.url,cover.url,cover.image_id,game_modes.name,storyline,first_release_date,rating,franchises.name;"
    response = requests.post(url, headers=headers, data=data)
    print(response.status_code)
    games = response.json()
    print(json.dumps(games, indent=4, sort_keys=True))
    return games

#function to get game info to telegram from the json file
@bot.on_message(filters.command("game"))
async def game_command(client: Client, message: Message):
    if len(message.text.split()) <= 1:
        await message.reply("You gotta enter a game name!")
        return
    game = message.text.split(maxsplit=1)[1]
    result = search(game)
    if not result:
        await message.reply("No game found")
        return
    result = result[0]
    game_id = result.get("id", "N/A")
    genres = result.get("genres", "N/A")
    storyline = result.get("storyline", "N/A")
    platforms = result.get("platforms", "N/A")
    game_name = result["name"]
    franchise = result.get("franchises", "N/A")
    modes = result.get("game_modes", "N/A")
    websites = result.get("websites", "N/A")
    if websites:
        websites = [website for website in websites if "category" in website and website["category"] == 13]
    else :
        websites = None
    summary = result.get("summary", "N/A")
    rating = result.get("rating")
    if rating:
        rating = int(rating)
    else:
        rating = ('No rating found')
    release_date = result.get("first_release_date")
    if release_date:
        release_date = datetime.fromtimestamp(release_date).strftime("%d/%m/%Y")
    cover_id = result.get("cover")
    url = result["url"]
    image_url = None
    if cover_id:
        image_url = f"https://images.igdb.com/igdb/image/upload/t_1080p_2x/{cover_id['image_id']}.jpg"
        print(image_url)
    text = f"""
**ID:** `{game_id}`
**Game:** `{game_name}`
**Rating:** `{rating}`
**Game Modes:** `{', '.join(mode['name'] for mode in modes if 'name' in mode)}`
**Genres:** `{', '.join(genre['name'] for genre in genres if 'name' in genre)}`
**Franchise:** `{', '.join(franch['name'] for franch in franchise if 'name' in franch)}`
**Platforms:** `{', '.join(platform['name'] for platform in platforms if 'name' in platform)}`
[­]({image_url})
**Storyline:** {storyline[:300]}...

**Summary:** __{summary[:300]}....[Read more]({url})__


**Release Date:** `{release_date}` 

        """
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Steam Link", url = websites[0]["url"] if websites else "not available")
            ]
        ]
    )
    
    await message.reply(text, disable_web_page_preview=False, reply_markup=buttons if websites else None)

#function to make a request to IGDB API to get character info
def search_characters(query: str) -> dict:
    url = f"https://api.igdb.com/v4/characters"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }
    data = f"search \"{query}\"; fields name,description,url,mug_shot,gender,species,akas;"
    response = requests.post(url, headers=headers, data=data)
    characters = response.json()
    print(json.dumps(characters, indent=4, sort_keys=True))
    return characters


#function to get character info to telegram from the json file
@bot.on_message(filters.command("character"))
async def character_command(client :Client, message: Message):

    #check if the user has entered a character name
    if len(message.text.split()) <= 1:
        await message.reply("You gotta enter a character name!")
        return
    
    #get the character name from the message
    character = message.text.split(maxsplit=1)[1]
    result = search_characters(character)

    #check if the character exists
    if not result:
        await message.reply("No character found")
        return
    result = result[0]
    name = result["name"]
    description = result.get("description", "N/A")
    gender = result.get("gender", "N/A")
    species = result.get("species", "N/A")
    url = result["url"]

    #assigning values to species of character
    if species == 1:
        species = "Human"
    elif species == 2:
        species = "Alien"
    elif species == 3:
        species = "Animal"
    elif species == 4:
        species = "Android"
    elif species == 5:
        species = "Unknown"

    #check gender of character
    if gender == 0:
        gender = "Male"
    elif gender == 1:
        gender = "Female"
    elif gender == 2:
        gender = "Other"

    
    text = f"""
**Name:** {name}
**Species:** {species}
**Gender:** {gender}

**Description:** __{description}__

**URL:** [More Info]({url})
"""
    await message.reply(text)

#function to get top 20 games list with their ratings
def get_top_games() -> dict:
    url = f"https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }
    data = f"fields name,rating; sort rating desc;where rating > 90;where rating_count > 400;"
    response = requests.post(url, headers=headers, data=data)
    games = response.json()
    print(json.dumps(games, indent=4, sort_keys=True))
    return games

#function to get top 20 games list with their ratings to telegram from the json file
@bot.on_message(filters.command("top"))
async def top_command(client: Client, message: Message):
    result = get_top_games()
    if not result:
        await message.reply("No games found")
        return
    text = ""
    for game in result:
        name = game["name"]
        rating = game.get("rating")
        if rating:
            rating = int(rating)
        else:
            rating = ('No rating found')
        text += "• " + f"{name} - `{rating}`\n"
    await message.reply(text)

#function to get artworks of a game from IGDB API
def get_art(game: str) -> dict:
    url = f"https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }
    data = f"fields name,artworks.image_id; search \"{game}\"; limit 1;"
    response = requests.post(url, headers=headers, data=data)
    art = response.json()
    print(json.dumps(art, indent=4, sort_keys=True))
    return art

#function to get artworks of a game to telegram from the json file
@bot.on_message(filters.command("art"))
async def art_command(client: Client, message: Message):
    if len(message.text.split()) <= 1:
        await message.reply("You gotta enter a game name!")
        return
    game = message.text.split(maxsplit=1)[1]
    result = get_art(game)
    if not result:
        await message.reply("No game found")
        return
    result = result[0]
    name = result["name"]
    artworks = result.get("artworks")
    if not artworks:
        await message.reply("No artworks found")
        return
    artworks = random.choice(artworks)
    image_id = (artworks["image_id"])
    image_url = f"https://images.igdb.com/igdb/image/upload/t_720p_2x/{image_id}.jpg"
    await message.reply_photo(image_url, caption=f"**{name}**")

#function to get screenshots of a game from IGDB API
def get_screenshots(game: str) -> dict:
    url = f"https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }
    data = f"fields name,screenshots.image_id; search \"{game}\"; limit 1;"
    response = requests.post(url, headers=headers, data=data)
    screenshots = response.json()
    print(json.dumps(screenshots, indent=4, sort_keys=True))
    return screenshots

#function to get screenshots of a game to telegram from the json file
@bot.on_message(filters.command("ss"))
async def screenshot_command(client: Client, message: Message):
    if len(message.text.split()) <= 1:
        await message.reply("You gotta enter a game name!")
        return
    game = message.text.split(maxsplit=1)[1]
    result = get_screenshots(game)
    if not result:
        await message.reply("No game found")
        return
    result = result[0]
    name = result["name"]
    screenshot = result.get("screenshots")
    if not screenshot:
        await message.reply("No screenshots found")
        return
    screenshot = random.choice(screenshot)
    image_id = (screenshot["image_id"])
    image_url = f"https://images.igdb.com/igdb/image/upload/t_720p_2x/{image_id}.jpg"
    await message.reply_photo(image_url, caption=f"**{name}**")

if __name__ == "__main__":
    bot.run()