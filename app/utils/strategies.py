import hashlib
from abc import ABC, abstractmethod

import requests
from flask import json, redirect, render_template

from app.config import (
    SHOP_SECRET_KEY,
    SHOP_ID,
    USD_PAYMENT_API_URL,
    RUB_PAYMENT_API_URL,
)
from app.utils.payment_data_processor import PaymentDataProcessor


class BaseStrategy(ABC):
    @staticmethod
    def make_hashed_sign(data: dict):
        ordered_data = dict(sorted(data.items()))
        hash_string = (
            ":".join([str(i) for i in ordered_data.values()])
            + SHOP_SECRET_KEY
        )
        new_hash = hashlib.sha256()
        new_hash.update(hash_string.encode())
        data["sign"] = new_hash.hexdigest()
        return data

    @staticmethod
    @abstractmethod
    def data_processor(payment: PaymentDataProcessor):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def request_payment(payload: dict):
        raise NotImplementedError()


class ApiCurrencyStrategy(BaseStrategy):
    @staticmethod
    def check_response(resp: dict):
        if not resp["data"]:
            raise RuntimeError(
                f"Can't create payment, check the entered data and try again"
            )
        return resp


class EurCurrencyStrategy(BaseStrategy):
    @staticmethod
    def data_processor(payment: PaymentDataProcessor):
        data = {
            "currency": payment.currency.value,
            "amount": payment.amount,
            "shop_id": SHOP_ID,
            "shop_order_id": payment.id,
        }
        return data

    @staticmethod
    def request_payment(payload: dict):
        return render_template(
            "EUR_payment_request_form.html", context=payload
        )


class UsdCurrencyStrategy(ApiCurrencyStrategy):
    @staticmethod
    def data_processor(payment: PaymentDataProcessor):
        data = {
            "payer_currency": payment.currency.value,
            "shop_amount": payment.amount,
            "shop_currency": payment.currency.value,
            "shop_id": SHOP_ID,
            "shop_order_id": payment.id,
        }
        return data

    @staticmethod
    def request_payment(payload: dict):
        req = requests.post(
            USD_PAYMENT_API_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
        )
        response = UsdCurrencyStrategy.check_response(req.json())
        return redirect(response["data"]["url"])


class RubCurrencyStrategy(ApiCurrencyStrategy):
    @staticmethod
    def data_processor(payment: PaymentDataProcessor):
        data = {
            "currency": payment.currency.value,
            "amount": payment.amount,
            "shop_id": SHOP_ID,
            "shop_order_id": payment.id,
            "payway": "payeer_rub",
        }
        return data

    @staticmethod
    def request_payment(payload: dict):
        req = requests.post(
            RUB_PAYMENT_API_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
        )
        response = RubCurrencyStrategy.check_response(req.json())

        return render_template(
            "RUB_payment_request_form.html", context=response
        )


class CurrencyContext(object):
    def __init__(self, payment: PaymentDataProcessor):
        pass

    @classmethod
    def run(cls, payment):
        currency = payment.currency.name
        if currency == "EUR":
            processor = EurCurrencyStrategy
        elif currency == "USD":
            processor = UsdCurrencyStrategy
        elif currency == "RUB":
            processor = RubCurrencyStrategy
        else:
            raise RuntimeError(f"Can't create {payment}")

        raw_data = processor.data_processor(payment=payment)
        hashed_data = processor.make_hashed_sign(raw_data)

        return processor.request_payment(hashed_data)
