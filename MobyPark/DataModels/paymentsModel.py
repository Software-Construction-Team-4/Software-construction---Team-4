import datetime

class PaymentsModel:
    def __init__(self, id : int, amount : int, completed_at : datetime, created_at : datetime, payment_hash : str, initiator : str, parking_lot_id : int, 
                 session_id : int, bank : str, transaction_date : datetime, issuer_code : str, payment_method : str, transaction_hash : str):
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


