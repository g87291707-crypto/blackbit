import asyncio
from telegram import Bot
from telegram.error import TelegramError
import logging

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token, admin_id):
        self.token = token
        self.admin_id = admin_id
        self.bot = Bot(token=token)
    
    async def send_message(self, text, parse_mode='HTML'):
        try:
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=text,
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    def send_sync(self, text, parse_mode='HTML'):
        try:
            asyncio.run(self.send_message(text, parse_mode))
            return True
        except Exception as e:
            logger.error(f"Error: {e}")
            return False

bot = None

def init_bot(token, admin_id):
    global bot
    bot = TelegramBot(token, admin_id)
    return bot
