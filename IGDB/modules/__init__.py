import logging
import os

from telegram.ext import ApplicationBuilder, Application

# Enable Logging========================================================================================X
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs.txt"), logging.StreamHandler()],
    level=logging.INFO,
)
LOGGER = logging.getLogger(__name__)
#=======================================================================================================x
# Variables

TELEGRAM_BOT_TOKEN = "6224611303:AAEAyRrctyK_GDXXeeyULbPAeS5RN7u-Tco"

#=======================================================================================================x

# Build dispatcher object for python-telegram-bot
dp = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
