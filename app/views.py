from flask import Blueprint, render_template, request

from app import db
from app.utils.strategies import CurrencyContext
from app.utils.payment_data_processor import PaymentDataProcessor

bp = Blueprint('payment', __name__)


@bp.route("/", methods=["GET", "POST"])
def make_payment():
    if request.method == "POST":

        try:
            payment = PaymentDataProcessor(request, db)
            payment.save_payment_to_db()
            return CurrencyContext.run(payment.payment)
        except Exception as e:
            return render_template("index.html", context=e)
    return render_template("index.html")
