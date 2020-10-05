import pytest

from app import create_app, db
from app.config import TestingConfig, SHOP_ID
from app.models import CurrencyType, Payment
from utils.strategies import RubCurrencyStrategy, UsdCurrencyStrategy

app = create_app(config_class=TestingConfig)


CURRENCIES = CurrencyType


@pytest.fixture
def client():
    yield app.test_client()
    with app.app_context():
        db.drop_all()


@pytest.fixture
def create_payment(
    amount=100, currency=CURRENCIES.USD.value, description="Test text",
):
    with app.app_context():
        payment = Payment(
            amount=amount, currency=currency, description=description
        )
        db.session.add(payment)
        db.session.commit()
        yield payment
        db.drop_all()


def test_config():
    assert not create_app().testing
    assert create_app(config_class=TestingConfig).testing


def test_get_main_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_hash_sign_creation():
    data = {
        "currency": CURRENCIES.RUB.value,
        "amount": 12.34,
        "shop_id": SHOP_ID,
        "shop_order_id": 123456,
        "payway": "payeer_rub",
    }
    equals_hash = (
        "b2ab7f0ae2788055305cf7f53a0a0904179b3a05b14fd945bf7da06bbaafc67a"
    )
    rub_hash_sign = RubCurrencyStrategy.make_hashed_sign(data)
    assert rub_hash_sign["sign"] == equals_hash


def test_rub_data_creation(create_payment):
    usd_data = UsdCurrencyStrategy.data_processor(create_payment)
    equals = {
        "payer_currency": CURRENCIES.USD.value,
        "shop_amount": 100.0,
        "shop_currency": CURRENCIES.USD.value,
        "shop_id": SHOP_ID,
        "shop_order_id": 1,
    }
    assert usd_data == equals
