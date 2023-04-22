import telegram
from telegram.ext import Updater, CommandHandler
import requests

TELEGRAM_BOT_TOKEN = "6224611303:AAEAyRrctyK_GDXXeeyULbPAeS5RN7u-Tco"
api_id= 7102532,  
api_hash="57f974d1f2772172d7801c9addda08a6"  
client_id= "8kc80zi43ry7ov5f6pyx9rg067c9zb"
access_token= "4063beydegyr3e2gpm62cls6m77u0x"

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, I'm a bot. Send me /game followed by the name of a game to get information about it.")

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
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"{game_name}\n\n{game_summary}\n\n{game_url}")
        cover_image_id = game["cover"]["image_id"] if "cover" in game else None
        if cover_image_id:
            cover_image_url = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{cover_image_id}.jpg"
            response = requests.get(cover_image_url)
            if response.status_code == 200:
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=response.content, caption=f"{game_name}\n\n{game_summary}\n\n{game_url}")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"{game_name}\n\n{game_summary}\n\n{game_url}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Game not found.")

updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('game', get_game_info))
updater.start_polling()
updater.idle()
