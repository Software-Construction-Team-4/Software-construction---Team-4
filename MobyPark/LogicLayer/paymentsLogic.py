import random

def create_issuer_code():
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    code = ""

    list = [1,2,3,4,5,6,7,8]

    for i in list:
        code += random.choice(characters)

    return code

# class paymentsLogic:
#     def create_payment(session, amount, bank, payment_method, initiator):
#         payment = PaymentsModel(
#             amount=amount,
#             created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             completed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             payment_hash=sc.generate_payment_hash(),
#             initiator=initiator,
#             parking_lot_id=session.parking_lot_id,
#             session_id=session.id,
#             bank=bank,
#             transaction_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             issuer_code=create_issuer_code(),
#             payment_method=payment_method,
#             transaction_hash=sc.generate_transaction_validation_hash(
#                 session.id, session.licenseplate
#             )
#         )

#         return PaymentsDataAccess().insert_payment(payment)