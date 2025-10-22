from database import SessionLocal
from models import User
from config import MAX_USER_ID, WELCOME_BONUS, PERCENT_BACK

def next_loyalty_id(db):
    # найти max loyalty_id и +1, если > MAX_USER_ID — вернуть ошибку
    max_id = db.query(User).order_by(User.loyalty_id.desc()).first()
    if not max_id:
        return 1
    next_id = max_id.loyalty_id + 1
    if next_id > MAX_USER_ID:
        raise Exception("Достигнут максимум пользователей (3000).")
    return next_id

def calc_bonus_from_amount(amount: float) -> int:
    # считаем 5% и округляем до целого (вы можете менять правило округления)
    bonus = amount * PERCENT_BACK
    return int(round(bonus))
