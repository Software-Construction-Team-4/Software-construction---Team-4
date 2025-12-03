import datetime

class PaymentsModel:
    def __init__(
        self,
        amount: int = None,
        completed_at=None,
        created_at=None,
        payment_hash: str = None,
        initiator: str = None,
        parking_lot_id: int = None,
        session_id: int = None,
        bank: str = None,
        transaction_date=None,
        issuer_code: str = None,
        payment_method: str = None,
        transaction_hash: str = None,
        id: int = None
    ):
        self.id = id
        self.amount = amount
        self.completed_at = completed_at
        self.created_at = created_at
        self.payment_hash = payment_hash
        self.initiator = initiator
        self.parking_lot_id = parking_lot_id
        self.session_id = session_id
        self.bank = bank
        self.transaction_date = transaction_date
        self.issuer_code = issuer_code
        self.payment_method = payment_method
        self.transaction_hash = transaction_hash


    def to_tuple(self):
        return (
            self.amount,
            self.completed_at,
            self.created_at,
            self.payment_hash,
            self.initiator,
            self.parking_lot_id,
            self.session_id,
            self.bank,
            self.transaction_date,
            self.issuer_code,
            self.payment_method,
            self.transaction_hash,
        )

    def to_update_tuple(self):
        return self.to_tuple() + (self.id,)
    
    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "completed_at": self.completed_at,
            "created_at": self.created_at,
            "payment_hash": self.payment_hash,
            "initiator": self.initiator,
            "parking_lot_id": self.parking_lot_id,
            "session_id": self.session_id,
            "bank": self.bank,
            "transaction_date": self.transaction_date,
            "issuer_code": self.issuer_code,
            "payment_method": self.payment_method,
            "transaction_hash": self.transaction_hash,
        }



