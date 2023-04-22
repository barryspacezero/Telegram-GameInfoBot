import time
import importlib

from modules.bot import dp, LOGGER

from modules.bot import ALL_MODULES

from telegram.ext import ContextTypes, CommandHandler
from telegram import Update


for module_name in ALL_MODULES:
    imported_module = importlib.import_module("bot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    message = update.effective_message
    await message.reply_text("bot working fine!")



def main():
    
    start_handler = CommandHandler("start", start)
    dp.add_handler(start_handler)

    LOGGER.info("bot is now deployed!!!----Using long polling...")
    dp.run_polling(timeout=15, drop_pending_updates=False)

if __name__ == "__main__":
    LOGGER.info("Successfully loaded all modules")
    main()