import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Des2106Sta123!",
        database="mobypark"
    )

def load_parking_lot_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM parking_lots")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {str(row['id']): row for row in rows}

def load_parking_lot_by_id(lid):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM parking_lots WHERE id = %s", (lid,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row
