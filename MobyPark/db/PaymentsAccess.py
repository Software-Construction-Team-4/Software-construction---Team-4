from mysql.connector import Error
from MobyPark.DataModels.paymentsModel import PaymentsModel
from database_utils import get_db_connection 
 


conn = get_db_connection()
cursor = conn.cursor(dictionary=True)

class PaymentsDataAccess:
    
    def get_all_payments(self):
        try:
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
