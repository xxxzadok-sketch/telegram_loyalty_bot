from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)  # internal DB id
    loyalty_id = Column(Integer, unique=True, index=True, nullable=False)  # 1..3000
    tg_id = Column(Integer, unique=True, index=True, nullable=False)
    first_name = Column(String(128))
    last_name = Column(String(128))
    phone = Column(String(32))
    bonus = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    confirmed = Column(Boolean, default=False)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)  # потраченная сумма
    bonus_added = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class RedemptionRequest(Base):
    __tablename__ = "redemptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)  # бонусы которые хочет списать
    confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(String(64))  # можно использовать Date/Time, но для простоты - строка
    time = Column(String(64))
    guests = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    confirmed = Column(Boolean, default=False)