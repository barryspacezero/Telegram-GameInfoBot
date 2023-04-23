import telegram
from telegram.ext import  CommandHandler
import requests
from IGDB import dp

client_id= "8kc80zi43ry7ov5f6pyx9rg067c9zb"
access_token= "4063beydegyr3e2gpm62cls6m77u0x"


def get_game_info(update, context):
    game_name = " ".join(context.args)
    url = f"https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": "{client_id}",
        "Authorization": f"Bearer {access_token}"
    }
    data = f"search \"{game_name}\"; fields name, url, summary;"
    response = requests.post(url, headers=headers, data=data)
    games = response.json()
    if games:
        game = games[0]
        game_name = game["name"]
        game_summary = game["summary"]
        game_url = game["url"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{game_name}\n\n{game_summary}\n\n{game_url}")
        cover_image_id = game["cover"]["image_id"] if "cover" in game else None
        if cover_image_id:
            cover_image_url = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{cover_image_id}.jpg"
            response = requests.get(cover_image_url)
            if response.status_code == 200:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=response.content, caption=f"{game_name}\n\n{game_summary}\n\n{game_url}")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{game_name}\n\n{game_summary}\n\n{game_url}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Game not found.")

dp.add_handler(Commandhandler("game", game))
