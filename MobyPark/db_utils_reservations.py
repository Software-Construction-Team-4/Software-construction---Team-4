import mysql.connector
import os

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Kikkervis66!",
        database="mobypark"
    )


def load_parking_lot_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM parking_lots")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def save_parking_lot_data(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM parking_lots")
    
    if data:
        keys = data[0].keys()
        columns = ", ".join(keys)
        placeholders = ", ".join(["%s"] * len(keys))
        sql = f"INSERT INTO parking_lots ({columns}) VALUES ({placeholders})"
        values = [tuple(d[k] for k in keys) for d in data]
        cursor.executemany(sql, values)
    
    conn.commit()
    cursor.close()
    conn.close()

def load_reservation_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reservations")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def save_reservation_data(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservations")
    if data:
        keys = data[0].keys()
        columns = ", ".join(keys)
        placeholders = ", ".join(["%s"] * len(keys))
        sql = f"INSERT INTO reservations ({columns}) VALUES ({placeholders})"
        values = [tuple(d[k] for k in keys) for d in data]
        cursor.executemany(sql, values)
    conn.commit()
    cursor.close()
    conn.close()
