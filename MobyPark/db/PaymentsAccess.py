from mysql.connector import Error
from paymentsModel import PaymentsModel
from database_utils import get_db_connection 
 

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
