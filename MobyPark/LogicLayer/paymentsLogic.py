import random
from DataAccesLayer.PaymentsAccess import PaymentsDataAccess

def create_issuer_code():
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    code = ""

    list = [1,2,3,4,5,6,7,8]

    for i in list:
        code += random.choice(characters)

    return code

def get_by_id(id):
    payments_instance = PaymentsDataAccess()
    return payments_instance.get_by_id(id)

def insert_payment(payment):
    data_access = PaymentsDataAccess()
    return data_access.insert_payment(payment)

def update_payment(payment):
    data_access = PaymentsDataAccess()
    return data_access.update_payment(payment)

def get_by_initiator(username):
    data_access = PaymentsDataAccess()
    return data_access.get_by_initiator(username)