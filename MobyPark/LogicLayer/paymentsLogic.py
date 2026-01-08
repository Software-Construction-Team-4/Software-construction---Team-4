from DataModels.paymentsModel import PaymentsModel
from datetime import datetime
import session_calculator as sc
from DataAccesLayer.PaymentsAccess import PaymentsDataAccess

class paymentsLogic:
    def create_payment(session, amount, bank, payment_method, initiator):
        payment = PaymentsModel(
            amount=amount,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            completed_at=None,
            payment_hash=sc.generate_payment_hash(),
            initiator=initiator,
            parking_lot_id=session.parking_lot_id,
            session_id=session.id,
            bank=bank,
            transaction_date=None,
            issuer_code=None,
            payment_method=payment_method,
            transaction_hash=sc.generate_transaction_validation_hash(
                session.id, session.licenseplate
            )
        )

        return PaymentsDataAccess().insert_payment(payment)
