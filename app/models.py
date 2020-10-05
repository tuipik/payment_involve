import enum
from datetime import datetime

from sqlalchemy_utils import ChoiceType

from app import db


class CurrencyType(enum.Enum):
    EUR = 978
    USD = 840
    RUB = 643


class Payment(db.Model):
    __tablename__ = "payment"
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(ChoiceType(CurrencyType, impl=db.Integer()))
    description = db.Column(db.String(300), nullable=True)
    created = db.Column(db.Integer, default=datetime.utcnow)

    def __repr__(self):
        return f"<Payment {self.id}>"
