from aiogram import types, Dispatcher
from database import SessionLocal
from models import User
from config import ADMIN_TELEGRAM_ID

async def start_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        await message.reply("Только админ может отправлять рассылки.")
        return
    # формат: /broadcast Текст (бот должен ожидать следующее сообщение — файл или текст)
    text = message.get_args()
    if not text:
        await message.reply("Отправьте /broadcast <текст сообщения> чтобы начать.")
        return
    await message.reply("Прикрепите фото/видео (опционально) или напишите команду /send чтобы отправить текстовую рассылку.")
    # для простоты: сохраняем состояние в памяти — можно реализовать FSM для админа
    # но здесь покажем простую имплементацию: если админ прислал /send — будет разослан текст из args
    # более сложная реализация — хранение промежуточного контента

async def send_broadcast(message: types.Message):
    # простая реализация: /send <текст>
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        return
    text = message.get_args()
    if not text:
        await message.reply("Укажите текст: /send <текст>")
        return
    db = SessionLocal()
    try:
        users = db.query(User).all()
        count = 0
        for u in users:
            try:
                await message.bot.send_message(u.tg_id, text)
                count += 1
            except:
                pass
        await message.reply(f"Рассылка отправлена {count} пользователям.")
    finally:
        db.close()

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(start_broadcast, commands=["broadcast"])
    dp.register_message_handler(send_broadcast, commands=["send"])
