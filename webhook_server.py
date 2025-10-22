import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_webhook
from config import BOT_TOKEN, WEBHOOK_URL, HOST, PORT
from handlers.registration import register_registration_handlers
from handlers.payments import register_payment_handlers
from handlers.redemptions import register_redemption_handlers
from handlers.reservations import register_reservation_handlers
from handlers.admin import register_admin_handlers

logging.basicConfig(level=logging.INFO)

WEBHOOK_PATH = '/webhook'
WEBAPP_HOST = HOST
WEBAPP_PORT = PORT
WEBHOOK_URL_FULL = WEBHOOK_URL + WEBHOOK_PATH

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

register_registration_handlers(dp)
register_payment_handlers(dp)
register_redemption_handlers(dp)
register_reservation_handlers(dp)
register_admin_handlers(dp)

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL_FULL)

async def on_shutdown(dp):
    logging.warning('Shutting down..')
    await bot.delete_webhook()
    await bot.close()

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
