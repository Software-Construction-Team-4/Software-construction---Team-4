import mysql.connector
from mysql.connector import Error
from MobyPark.DataModels.paymentsModel import PaymentsModel
import datetime

def get_db_connection():
    return mysql.connector.connect(
        host="145.24.237.71",
        port=8001,
        user="vscode",
        password="StrongPassword123!",
        database="mobypark"
    ) 

class PaymentsDataAccess:
    
    def get_all_payments(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_by_id(self, id : int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM payments WHERE id = {id}")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_by_payment_method(self, method : str):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM payments WHERE payment_method = {method}")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_by_bank(self, bank : str):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM payments WHERE bank = {bank}")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_by_transaction_date(self, date : datetime):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM payments WHERE transaction_date = {date}")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_by_created_date(self, date : datetime):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM payments WHERE created_at = {date}")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_before_transaction_date(self, date : datetime):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM payments WHERE transaction_date =< {date}")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_after_transaction_date(self, date : datetime):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM payments WHERE transaction_date => {date}")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_before_created_date(self, date : datetime):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM payments WHERE created_at =< {date}")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_after_created_date(self, date : datetime):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM payments WHERE created_at => {date}")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_by_parking_lot_id(self, id : int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM payments WHERE parking_lot_id = {id}")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_by_session_id(self, id : int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM payments WHERE session_id = {id}")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_by_initiator(self, name : str):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM payments WHERE initiator = {name}")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_by_transaction_date(self, code : str):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM payments WHERE issuer_code = {code}")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_between_dates(self, date_min : datetime, date_max : datetime):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM payments WHERE created_at => {date_min} AND created_at =< {date_max}")
            rows = cursor.fetchall()
            
            payments = [PaymentsModel(**row) for row in rows]
            return payments
        except Error as e:
            print("Error reading data from MySQL:", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def update_payment(self, updated_p: PaymentsModel):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            sql = """
                UPDATE payments
                SET 
                    amount = %s,
                    completed_at = %s,
                    created_at = %s,
                    payment_hash = %s,
                    initiator = %s,
                    parking_lot_id = %s,
                    session_id = %s,
                    bank = %s,
                    transaction_date = %s,
                    issuer_code = %s,
                    payment_method = %s,
                    transaction_hash = %s
                WHERE id = %s
            """

            cursor.execute(sql, (updated_p
            ))

            conn.commit()
            return True

        except Error as e:
            print("Error updating data:", e)
            return False

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
