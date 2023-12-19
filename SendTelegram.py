import os
from dotenv import load_dotenv
import telegram
import asyncio
import tracemalloc
tracemalloc.start()


async def send_telegram_async(bot_token, chat_id, content):
    bot = telegram.Bot(bot_token)
    await bot.sendMessage(chat_id=chat_id, text=content)


def send_telegram(content, dot_env_path='.env'):
    load_dotenv(dot_env_path)

    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    asyncio.run(send_telegram_async(bot_token, chat_id, content))
