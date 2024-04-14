from pyrogram import Client, filters
from pyrogram.types import Message,CallbackQuery,InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import requests,io
import json,sys
from datetime import datetime
import random
import traceback
import dotenv
import logging
from os import getenv
import redis
from constants import *

dotenv.load_dotenv()
REDIS = redis.Redis(host=getenv("REDIS_HOST"), port=int(getenv("REDIS_PORT")),password=getenv("REDIS_PASSWORD"), decode_responses=True)
try:
    REDIS.ping()
except Exception:
    traceback.print_exc()
    sys.exit(0)

Database = {}

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

#function to get someone else's user ID
@bot.on_message(filters.command("id"))
async def id_command(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply("Reply to a message to get the ID")
        return
    if not message.from_user.id == 1035576679:
        return await message.reply_text("You are not my master!")
    await message.reply_text(f"**User ID:** `{message.reply_to_message.from_user.id}`")


def free()->list:
    url=f"https://api.qewertyy.dev/freegames"
    response=requests.get(url)
    if response.status_code != 200:
        print("failed to fetch data, Status code :", response.status_code)
        return None
    data = response.json()['content']
    print(json.dumps(data,sort_keys=True, indent=2))
    games = []
    if len(data['epicGames']) > 0:
        for game in data['epicGames']:
            games.append(game)
    if len(data['steam']) > 0:
        for game in data['steam']:
            games.append(game)
    if len(data['standalone']) > 0:
        for game in data['standalone']:
            games.append(game)
    return games

#@bot.on_message(filters.command("free"))
async def free_command(client: Client, message: Message):
    result = free()
    if not result:
        await message.reply("No free games found")
        return
    text = ""
    buttons = []
    for i in result:
        buttons.append([InlineKeyboardButton(
            text=i['name'],
            url=i['url']
        )])
    await message.reply("Free Games:", disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(buttons))


@bot.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply("Hello, this bot can send game info and character info. Send /help to get more info.")

@bot.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply("Send /game `'game name'` to get info about a game.\nSend /character `'character name'` to get info about a character.\n Send /ss `'game name'` to get a screenshot of a game.\nSend /art `'game name'` to get an artwork of a game.\nSend `/top` to get the list of top rated games.")

#function to get game info and save it in key-value pairs
def search(payload : str) -> dict:
    url = f"https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(url, headers=headers, data=payload)
    print(response.status_code)
    games = response.json()
    print(json.dumps(games, indent=4, sort_keys=True))
    return games

@bot.on_callback_query(filters.regex(r"^game.(.*?)"))
async def gameInfo(client: Client,query: CallbackQuery):
    data = query.data.split('.')
    if int(data[-1]) != query.from_user.id:
        return await query.answer("Not for you!",show_alert=True)
    gameId = data[1]
    payload = f"fields name,url,similar_games.name,genres.name,summary,platforms.name,websites.category,websites.url,cover.url,cover.image_id,game_modes.name,storyline,first_release_date,rating,franchises.name; where id={gameId};"
    game = search(payload)
    result = game[0]
    game_id = result.get("id", "N/A")
    genres = result.get("genres", "N/A")
    storyline = result.get("storyline", "N/A")
    platforms = result.get("platforms", "N/A")
    game_name = result["name"]
    modes = result.get("game_modes", "N/A")
    websites = result.get("websites")
    if websites is None:
        websites = []
    else:
        websites = [website for website in websites if website["category"] == 13 or website["category"] == 15]
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
    similar_games = result.get("similar_games", "N/A")
    if cover_id:
        image_url = f"https://images.igdb.com/igdb/image/upload/t_720p_2x/{cover_id['image_id']}.jpg"
        print(image_url)
    text = f"""
**ID:** `{game_id}`
**Game:** `{game_name}`
**Rating:** `{rating}`
**Game Modes:** `{', '.join(mode['name'] for mode in modes if 'name' in mode)}`
**Genres:** `{', '.join(genre['name'] for genre in genres if 'name' in genre)}`
**Platforms:** `{', '.join(platform['name'] for platform in platforms if 'name' in platform)}`

**Similar Games:** {', '.join(game['name'] for game in similar_games[:5] if 'name' in game)}
[­]({image_url})
**Storyline:** {storyline[:300]}...

**Summary:** __{summary[:300]}....[Read more]({url})__


**Release Date:** `{release_date}`

        """
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Steam/Itch-io Link",
                                    url=websites[0]["url"]
                                    if websites
                                    else websites[1]["url"]
                                    if len(websites) > 1
                                    else None),
            ]
        ]
    )

    await query.edit_message_text(text, disable_web_page_preview=False, reply_markup=buttons if websites else None)


#function to get game info to telegram from the json file
@bot.on_message(filters.command("game"))
async def game_command(client: Client, message: Message):
    if len(message.text.split()) <= 1:
        await message.reply("You gotta enter a game name!")
        return
    game = message.text.split(maxsplit=1)[1]
    data = f"search \"{game}\"; fields id,name; limit 5;"
    result = search(data)
    if not result:
        await message.reply("No game found")
        return
    buttons = []
    for i in result:
        buttons.append([InlineKeyboardButton(
            text=i['name'],
            callback_data=f"game.{i['id']}.{message.from_user.id}"
        )])
    await message.reply("Games Found:", disable_web_page_preview=False, reply_markup=InlineKeyboardMarkup(buttons))

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
    data = f"fields name,rating; sort rating desc;where rating > 90;where rating_count > 420;limit 30;"
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
def get_screenshots(payload: str) -> dict:
    url = f"https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(url, headers=headers, data=payload)
    result = response.json()
    print(json.dumps(result, indent=4, sort_keys=True))
    games = []
    if "search" in payload:
        for ss in result:
            games.append( {
                    "id":ss['id'],
                    "name":ss['name']
                })
    else:
        games = result
    return games

def paginate_screenshots(index: int, user_id: int,total: int) -> list:
    btns = []
    if index == 0:
        btns.append(
            [
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=f"ss.{index+1}.{user_id}"
                )
            ]
        )
    elif index == total-1:
        btns.append(
            [
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=f"ss.0.{user_id}"
                )
            ]
        )
    else:
        btns.append(
            [
                InlineKeyboardButton(
                    text="⬅️",
                    callback_data=f"ss.{index-1}.{user_id}"
                ),
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=f"ss.{index+1}.{user_id}"
                )
            ]
        )
    btns.append(
            [
                InlineKeyboardButton(
                    text="Close",
                    callback_data=f"ss.{-1}.{user_id}"
                )
            ]
        )
    return btns

#function to get screenshots of a game to telegram from the json file
@bot.on_message(filters.command("ss"))
async def screenshot_command(client: Client, message: Message):
    if len(message.text.split()) <= 1:
        await message.reply("You gotta enter a game name!")
        return
    game = message.text.split(maxsplit=1)[1]
    payload = f"fields name,screenshots.image_id; search \"{game}\"; limit 5;"
    results = get_screenshots(payload)
    if not results:
        await message.reply("No game found")
        return
    buttons = []
    for i in results:
        buttons.append([InlineKeyboardButton(
            text=i['name'],
            callback_data=f"ssgames.{i['id']}.{message.from_user.id}"
        )])
    await message.reply("Games Found:", disable_web_page_preview=False, reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex(r"^ssgames.(.*?)"))
async def sendBtns(client: Client,query: CallbackQuery):
    data = query.data.split('.')
    user_id = int(data[-1])
    if user_id != query.from_user.id:
        return await query.answer("Not for you!",show_alert=True)
    gameId = data[1]
    payload = f"fields id,name,screenshots.image_id; where id={gameId};"
    game = get_screenshots(payload)
    if not game:
        await query.answer("No game found!")
        await query.message.delete()
        return
    game = game[0]
    Database[user_id] = game
    btns = paginate_screenshots(0,user_id,len(game['screenshots']))
    await client.send_photo(
        query.message.chat.id,
        photo=imageUrl.format(game['screenshots'][0]['image_id']),
        reply_markup=InlineKeyboardMarkup(btns)
    )
    await query.message.delete()

@bot.on_callback_query(filters.regex(r"^ss.(.*?)"))
async def sendScreenshot(client: Client,query: CallbackQuery):
    data = query.data.split('.')
    user_id = int(data[-1])
    if user_id != query.from_user.id:
        return await query.answer("Not for you!",show_alert=True)
    index = int(data[1])
    if index == -1:
        del Database[user_id]
        return await query.message.delete()
    game = Database.get(user_id,None)
    if game is None:
        return await query.message.delete()
    imageId = game['screenshots'][index]['image_id']
    btns = paginate_screenshots(
        index,user_id,len(game['screenshots'])
    )
    await query.edit_message_media(
        media=InputMediaPhoto(media=imageUrl.format(imageId)),
        reply_markup=InlineKeyboardMarkup(btns)
    )
    return

def getUserInfo(username):
    url = f"https://backloggd-api.vercel.app/user/{username}"
    response = requests.get(url)
    if response.status_code == 404:
        return 404
    if response.status_code != 200:
        print("failed to fetch data, Status code :", response.status_code)
        return None
    data = response.json()
    print(json.dumps(data,sort_keys=True, indent=2))
    return data['content']

def setBackloggdUsername(userId,username):
    REDIS.set(userId,username)

def getBackloggdUsername(userId):
    return REDIS.get(userId)

def userExists(userId):
    return REDIS.get(userId) is not None

def formatLastKeys(data):
    last3Items = list(data.items())[-3:]
    return "\n".join([f"**{key}**: `{value}`" for key, value in last3Items])

def createFlexMmessage(data):
    favorite_games = ", ".join([i['name'] for i in data['favoriteGames']] if len(data['favoriteGames']) > 0 else ["No favorite games found."])
    recently_played_games = ", ".join([i['name'] for i in data['recentlyPlayed']] if len(data['recentlyPlayed']) > 0 else ["No games played recently."])
    lastItems = formatLastKeys(data)
    message = flexMessage.format(
        username=data['username'],
        bio=data['bio'],
        favorite_games=favorite_games,
        recently_played_games=recently_played_games,
        remaining_info=lastItems
    )
    return message

def getImageContent(image_url):
    response = requests.get(image_url)
    if response.status_code != 200:
        print("failed to fetch data, Status code :", response.status_code)
        return None
    return response.content

@bot.on_message(filters.command(["uname","username"]))
async def setUsername(client: Client, message: Message):
    if len(message.text.split()) <= 1:
        await message.reply("You gotta enter a username!")
        return
    username = message.text.split(maxsplit=1)[1]
    if (userExists(message.from_user.id)):
        await message.reply("Username already set!, you can use /change to change it.")
        return
    setBackloggdUsername(message.from_user.id,username)
    await message.reply("Username set successfully!")

@bot.on_message(filters.command(["change"]))
async def changeUsername(client: Client, message: Message):
    if len(message.text.split()) <= 1:
        await message.reply("You gotta enter a username!")
        return
    username = message.text.split(maxsplit=1)[1]
    if not (userExists(message.from_user.id)):
        await message.reply("Username not set!, you can use /uname to set it.")
        return
    setBackloggdUsername(message.from_user.id,username)
    await message.reply("Username changed successfully!")

@bot.on_message(filters.command("flex"))
async def flex(client: Client, message: Message):
    if not userExists(message.from_user.id):
        await message.reply("You gotta set your username by using /uname")
        return
    username = getBackloggdUsername(message.from_user.id)
    data = getUserInfo(username)
    if data == 404:
        await message.reply("User not found!")
        return
    elif not data:
        return
    image = getImageContent(data['profile'])
    text = createFlexMmessage(data)
    await message.reply_photo(io.BytesIO(image), caption=text)
    return


if __name__ == "__main__":
    bot.run()
