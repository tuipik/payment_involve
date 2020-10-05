from app.models import Payment


class PaymentDataProcessor:
    def __init__(self, request, db):
        self._req = request
        self._db = db
        self._payment = self._get_data_from_request(self._req)

    @staticmethod
    def _get_data_from_request(req):
        try:
            amount = float(req.form["amount"])
            currency = int(req.form["currency"])
            description = req.form["description"]

            return Payment(
                amount=amount, currency=currency, description=description
            )
        except Exception as e:
            print(e)
            raise TypeError(
                f"Can't create payment, check the entered data and try again"
            )

    @property
    def payment(self):
        return self._payment

    def save_payment_to_db(self):
        self._db.session.add(self._payment)
        self._db.session.commit()
