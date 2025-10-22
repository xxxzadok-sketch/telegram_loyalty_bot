from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📝 Мой профиль"), KeyboardButton("💳 Баланс"))
    kb.add(KeyboardButton("➕ Начислить (админ)"), KeyboardButton("➖ Списать баллы"))
    kb.add(KeyboardButton("🍽️ Забронировать стол"), KeyboardButton("📣 Новости"))
    return kb

def confirm_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_reg"),
           InlineKeyboardButton("✏️ Исправить", callback_data="edit_reg"))
    return kb

def confirm_redemption_buttons(request_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Подтвердить списание", callback_data=f"confirm_red_{request_id}"),
           InlineKeyboardButton("❌ Отклонить", callback_data=f"decline_red_{request_id}"))
    return kb
