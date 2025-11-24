import mysql.connector
from mysql.connector import Error
from DataModels.paymentsModel import PaymentsModel
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
            return [PaymentsModel(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()
    
    def get_by_id(self, id: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE id = %s", (id,))
            row = cursor.fetchone()
            if row:
                return PaymentsModel(**row)
            else:
                return None
        finally:
            cursor.close()
            conn.close()
    
    def get_by_payment_method(self, method: str):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE payment_method = %s", (method,))
            rows = cursor.fetchall()
            return [PaymentsModel(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_by_bank(self, bank: str):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE bank = %s", (bank,))
            rows = cursor.fetchall()
            return [PaymentsModel(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()
    
    def get_by_transaction_date(self, date: datetime.datetime):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE transaction_date = %s", (date,))
            rows = cursor.fetchall()
            return [PaymentsModel(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_by_created_date(self, date: datetime.datetime):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE created_at = %s", (date,))
            rows = cursor.fetchall()
            return [PaymentsModel(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_before_transaction_date(self, date: datetime.datetime):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE transaction_date <= %s", (date,))
            rows = cursor.fetchall()
            return [PaymentsModel(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_after_transaction_date(self, date: datetime.datetime):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE transaction_date >= %s", (date,))
            rows = cursor.fetchall()
            return [PaymentsModel(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_before_created_date(self, date: datetime.datetime):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE created_at <= %s", (date,))
            rows = cursor.fetchall()
            return [PaymentsModel(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_after_created_date(self, date: datetime.datetime):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE created_at >= %s", (date,))
            rows = cursor.fetchall()
            return [PaymentsModel(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_by_parking_lot_id(self, id: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE parking_lot_id = %s", (id,))
            rows = cursor.fetchall()
            return [PaymentsModel(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_by_session_id(self, id: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE session_id = %s", (id,))
            rows = cursor.fetchall()
            return [PaymentsModel(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_by_initiator(self, name: str):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE initiator = %s", (name,))
            rows = cursor.fetchall()
            return [PaymentsModel(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_by_issuer_code(self, code: str):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE issuer_code = %s", (code,))
            rows = cursor.fetchall()
            return [PaymentsModel(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_between_dates(self, date_min: datetime.datetime, date_max: datetime.datetime):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM payments WHERE created_at >= %s AND created_at <= %s",
                (date_min, date_max),
            )
            rows = cursor.fetchall()
            return [PaymentsModel(**row) for row in rows]
        finally:
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

            cursor.execute(sql, updated_p.to_update_tuple())
            conn.commit()
            return True

        except Error as e:
            print("Error updating data:", e)
            return False

        finally:
            cursor.close()
            conn.close()

    def delete_payment(self, id : int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM payments WHERE id = %s", (id,))
            conn.commit()

        except Error as e:
            print("Error updating data:", e)
            return False
        
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def insert_payment(self, payment : PaymentsModel):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            sql = """
            INSERT INTO payments (
                amount,
                completed_at,
                created_at,
                payment_hash,
                initiator,
                parking_lot_id,
                session_id,
                bank,
                transaction_date,
                issuer_code,
                payment_method,
                transaction_hash
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(sql, payment.to_tuple())
            conn.commit()
            return cursor.lastrowid

        except Error as e:
            print("Error updating data:", e)
            return False

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
