import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers.registration import register_registration_handlers
from handlers.payments import register_payment_handlers
from handlers.redemptions import register_redemption_handlers
from handlers.reservations import register_reservation_handlers
from handlers.admin import register_admin_handlers

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# регистрируем хендлеры
register_registration_handlers(dp)
register_payment_handlers(dp)
register_redemption_handlers(dp)
register_reservation_handlers(dp)
register_admin_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
