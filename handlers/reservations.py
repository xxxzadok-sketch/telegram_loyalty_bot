from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import SessionLocal
from models import Reservation, User

class ResStates(StatesGroup):
    DATE = State()
    TIME = State()
    GUESTS = State()
    CONFIRM = State()

async def start_reservation(message: types.Message):
    await message.answer("Здравствуйте! Для брони укажите дату (пример: 2025-11-01):")
    await ResStates.DATE.set()

async def res_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text.strip())
    await message.answer("Укажите время (пример: 19:00):")
    await ResStates.TIME.set()

async def res_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text.strip())
    await message.answer("Сколько человек придёт?")
    await ResStates.GUESTS.set()

async def res_guests(message: types.Message, state: FSMContext):
    try:
        guests = int(message.text.strip())
    except:
        await message.answer("Укажите число.")
        return
    await state.update_data(guests=guests)
    data = await state.get_data()
    summary = f"Проверьте бронь:\nДата: {data['date']}\nВремя: {data['time']}\nГостей: {data['guests']}\n\nЕсли всё верно — подтвердите."
    from keyboards import confirm_keyboard
    await message.answer(summary, reply_markup=confirm_keyboard())
    await ResStates.CONFIRM.set()

async def confirm_res(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    data = await state.get_data()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.tg_id == callback_query.from_user.id).first()
        uid = user.id if user else None
        res = Reservation(user_id=uid, date=data['date'], time=data['time'], guests=data['guests'], confirmed=True)
        db.add(res)
        db.commit()
        await callback_query.message.answer("Ваша бронь принята. Спасибо!")
        # уведомление админу
        await callback_query.bot.send_message(callback_query.bot.owner_id if hasattr(callback_query.bot, 'owner_id') else callback_query.bot.bot_id,
                                              "Новая бронь: " + f"{data['date']} {data['time']} x{data['guests']}")
    finally:
        db.close()
        await state.finish()

async def edit_res(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer("Начнём бронь заново. Укажите дату (пример: 2025-11-01):")
    await ResStates.DATE.set()

def register_reservation_handlers(dp: Dispatcher):
    dp.register_message_handler(start_reservation, lambda m: m.text and m.text.lower().startswith("забронировать"))
    dp.register_message_handler(res_date, state=ResStates.DATE)
    dp.register_message_handler(res_time, state=ResStates.TIME)
    dp.register_message_handler(res_guests, state=ResStates.GUESTS)
    dp.register_callback_query_handler(confirm_res, lambda c: c.data == "confirm_reg", state=ResStates.CONFIRM)
    dp.register_callback_query_handler(edit_res, lambda c: c.data == "edit_reg", state=ResStates.CONFIRM)
