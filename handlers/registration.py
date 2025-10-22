from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import SessionLocal
from models import User
from config import WELCOME_BONUS
from utils import next_loyalty_id

class RegStates(StatesGroup):
    FIRSTNAME = State()
    LASTNAME = State()
    PHONE = State()
    CONFIRM = State()

async def start_reg(message: types.Message):
    await message.answer("Пожалуйста, введите ваше Имя:")
    await RegStates.FIRSTNAME.set()

async def first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text.strip())
    await message.answer("Введите вашу Фамилию:")
    await RegStates.LASTNAME.set()

async def last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text.strip())
    await message.answer("Введите номер мобильного телефона (пример: +79001234567):")
    await RegStates.PHONE.set()

async def phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    # простая валидация
    if len(phone) < 6:
        await message.answer("Неверный номер, попробуйте заново.")
        return
    await state.update_data(phone=phone)
    data = await state.get_data()
    summary = (f"Проверьте данные:\n\n"
               f"Имя: {data['first_name']}\n"
               f"Фамилия: {data['last_name']}\n"
               f"Телефон: {data['phone']}\n\n"
               "Если всё верно — нажмите 'Подтвердить', иначе 'Исправить'.")
    from keyboards import confirm_keyboard
    await message.answer(summary, reply_markup=confirm_keyboard())
    await RegStates.CONFIRM.set()

async def confirm_reg(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    data = await state.get_data()
    db = SessionLocal()
    try:
        # проверка на существование tg_id
        existing = db.query(User).filter(User.tg_id==callback_query.from_user.id).first()
        if existing:
            await callback_query.message.answer("Вы уже зарегистрированы.")
            await state.finish()
            return
        # получить следующий loyalty id
        lid = next_loyalty_id(db)
        user = User(
            loyalty_id=lid,
            tg_id=callback_query.from_user.id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            bonus=WELCOME_BONUS,
            confirmed=True
        )
        db.add(user)
        db.commit()
        await callback_query.message.answer(f"Благодарим за регистрацию! Вам начислено {WELCOME_BONUS} бонусных баллов.\nВаш ID: {lid}")
    except Exception as e:
        await callback_query.message.answer(f"Ошибка: {e}")
    finally:
        db.close()
        await state.finish()

async def edit_reg(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer("Давайте начнём заново. Введите ваше Имя:")
    await RegStates.FIRSTNAME.set()

def register_registration_handlers(dp: Dispatcher):
    dp.register_message_handler(start_reg, lambda msg: msg.text and msg.text.lower() in ["регистрация", "начать", "/start"], state="*")
    dp.register_message_handler(first_name, state=RegStates.FIRSTNAME, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(last_name, state=RegStates.LASTNAME, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(phone, state=RegStates.PHONE, content_types=types.ContentTypes.TEXT)
    dp.register_callback_query_handler(confirm_reg, lambda c: c.data == "confirm_reg", state=RegStates.CONFIRM)
    dp.register_callback_query_handler(edit_reg, lambda c: c.data == "edit_reg", state=RegStates.CONFIRM)
