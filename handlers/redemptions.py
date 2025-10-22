from aiogram import types, Dispatcher
from database import SessionLocal
from models import User, RedemptionRequest
from keyboards import confirm_redemption_buttons
from config import ADMIN_TELEGRAM_ID

async def request_redemption(message: types.Message):
    # пользователь нажал кнопку "списать баллы" и отправил количество
    parts = message.text.split()
    try:
        amount = int(parts[-1])
    except:
        await message.reply("Укажите количество баллов числом.")
        return
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.tg_id == message.from_user.id).first()
        if not user:
            await message.reply("Вы не зарегистрированы.")
            return
        if amount > user.bonus:
            await message.reply("У вас недостаточно баллов.")
            return
        # создаём запрос
        req = RedemptionRequest(user_id=user.id, amount=amount, confirmed=False)
        db.add(req)
        db.commit()
        # уведомляем администратора
        # передаём id запроса в callback_data
        kb = confirm_redemption_buttons(req.id)
        await message.reply("Запрос на списание отправлен администратору. Ожидайте подтверждения.")
        await message.bot.send_message(ADMIN_TELEGRAM_ID, f"Пользователь {user.first_name} (ID {user.loyalty_id}) хочет списать {amount} баллов.", reply_markup=kb)
    finally:
        db.close()

async def handle_confirm_redemption(callback_query: types.CallbackQuery):
    data = callback_query.data  # например "confirm_red_3"
    db = SessionLocal()
    try:
        if data.startswith("confirm_red_"):
            req_id = int(data.split("_")[-1])
            req = db.query(RedemptionRequest).filter(RedemptionRequest.id==req_id).first()
            if not req:
                await callback_query.answer("Запрос не найден.")
                return
            if req.confirmed:
                await callback_query.answer("Уже подтверждено.")
                return
            user = db.query(User).filter(User.id==req.user_id).first()
            if not user:
                await callback_query.answer("Пользователь не найден.")
                return
            if req.amount > user.bonus:
                await callback_query.answer("У пользователя недостаточно баллов.")
                return
            user.bonus -= req.amount
            req.confirmed = True
            db.add(user); db.add(req); db.commit()
            await callback_query.message.answer(f"Списано {req.amount} баллов у пользователя {user.first_name} (ID {user.loyalty_id}).")
            # уведомление пользователю
            try:
                await callback_query.bot.send_message(user.tg_id, f"С вашего баланса списано {req.amount} бонусных баллов. Текущий баланс: {user.bonus}")
            except:
                pass
        elif data.startswith("decline_red_"):
            req_id = int(data.split("_")[-1])
            req = db.query(RedemptionRequest).filter(RedemptionRequest.id==req_id).first()
            if req:
                db.delete(req)
                db.commit()
            await callback_query.answer("Запрос отклонён.")
    finally:
        db.close()

def register_redemption_handlers(dp: Dispatcher):
    dp.register_message_handler(request_redemption, lambda m: m.text and m.text.lower().startswith("списать"))
    dp.register_callback_query_handler(handle_confirm_redemption)
