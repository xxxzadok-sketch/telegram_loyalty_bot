from aiogram import types, Dispatcher
from database import SessionLocal
from models import User, Transaction
from utils import calc_bonus_from_amount
from config import ADMIN_TELEGRAM_ID

async def start_add_bonus(message: types.Message):
    # команда для админа: ввести username или loyalty id, затем сумму
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        await message.reply("Доступно только администратору.")
        return
    await message.reply("Введите loyalty id или Телеграм ID пользователя и сумму через пробел\nПример: 25 1500 (25 — loyalty id, 1500 — сумма в руб.)")

async def process_add_bonus(message: types.Message):
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.reply("Неверный формат. Пример: 25 1500")
        return
    user_identifier = parts[0]
    try:
        amount = float(parts[1].replace(',', '.'))
    except:
        await message.reply("Неверная сумма.")
        return
    db = SessionLocal()
    try:
        # пробуем найти по loyalty_id, если нет — по tg_id
        user = None
        if user_identifier.isdigit():
            user = db.query(User).filter(User.loyalty_id == int(user_identifier)).first()
        if not user:
            user = db.query(User).filter(User.tg_id == int(user_identifier)).first()
        if not user:
            await message.reply("Пользователь не найден.")
            return
        bonus = calc_bonus_from_amount(amount)
        user.bonus = user.bonus + bonus
        db.add(user)
        tr = Transaction(user_id=user.id, amount=amount, bonus_added=bonus)
        db.add(tr)
        db.commit()
        await message.reply(f"Начислено {bonus} бонусов пользователю {user.first_name} (ID {user.loyalty_id}). Текущий баланс: {user.bonus}")
        # уведомление пользователю
        try:
            await message.bot.send_message(user.tg_id, f"Вам начислено {bonus} бонусных баллов за покупку {amount}. Текущий баланс: {user.bonus}")
        except Exception as e:
            # пользователь мог заблокировать бота
            pass
    finally:
        db.close()

def register_payment_handlers(dp: Dispatcher):
    dp.register_message_handler(start_add_bonus, commands=["addbonus"])
    dp.register_message_handler(process_add_bonus, lambda m: m.text and m.text.split()[0].isdigit() and len(m.text.split())==2)
