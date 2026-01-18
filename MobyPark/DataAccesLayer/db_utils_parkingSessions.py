import mysql.connector
from DataModels.parkingSessionModel import ParkingSession


from environment import Environment
def get_db_connection():
    return mysql.connector.connect(
        host=Environment.get_var("DB_HOST"),
        port=int(Environment.get_var("DB_PORT")),
        user=Environment.get_var("DB_USER"),
        password=Environment.get_var("DB_PASSWORD"),
        database=Environment.get_var("DB_NAME")
    )


def create_parking_session_from_row(row):
    return ParkingSession(
        id=row["id"],
        parking_lot_id=row["parking_lot_id"],
        session=row["session"],
        user_id=row["user"],
        licenseplate=row["licenseplate"],
        started=row["started"],
        stopped=row["stopped"],
        duration_minutes=row["duration_minutes"],
        cost=row["cost"],
        payment_status=row["payment_status"]
    )


def find_active_session_by_licenseplate(connection, licenseplate):
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute(
        """
        SELECT licenseplate
        FROM parking_sessions
        WHERE licenseplate = %s AND stopped IS NULL
        LIMIT 1
        """,
        (licenseplate,)
    )
    return cursor.fetchone()


def get_next_session_number(connection, parking_lot_id):
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute(
        "SELECT COALESCE(MAX(session), 0) + 1 AS next_num FROM parking_sessions WHERE parking_lot_id=%s",
        (parking_lot_id,)
    )
    return cursor.fetchone()["next_num"]


def insert_parking_session(connection, session_data):
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute(
        """
        INSERT INTO parking_sessions
          (parking_lot_id, licenseplate, started, stopped, user,
           duration_minutes, cost, payment_status, session)
        VALUES
          (%s, %s, %s, %s, %s, 0, %s, 'pending', %s)
        """,
        (
            session_data["parking_lot_id"],
            session_data["licenseplate"],
            session_data["started"],
            session_data["stopped"],
            session_data["user_id"],
            session_data["cost"],
            session_data["session_number"]
        )
    )
    return cursor.lastrowid


def increase_active_sessions(connection, parking_lot_id):
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE parking_lots SET active_sessions = COALESCE(active_sessions,0) + 1 WHERE id=%s",
        (parking_lot_id,)
    )


def find_active_session_by_user(connection, user_id):
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute(
        "SELECT * FROM parking_sessions WHERE user = %s AND stopped IS NULL",
        (user_id,)
    )
    return cursor.fetchone()


def update_session_on_stop(connection, session_id, stopped, minutes, price):
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE parking_sessions
        SET stopped = %s,
            duration_minutes = %s,
            cost = %s,
            payment_status = 'unpaid'
        WHERE id = %s
        """,
        (stopped, minutes, price, session_id)
    )


def decrease_active_sessions(connection, parking_lot_id):
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE parking_lots SET active_sessions = GREATEST(COALESCE(active_sessions,0)-1,0) WHERE id=%s",
        (parking_lot_id,)
    )


def get_parking_lot(connection, lot_id):
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT * FROM parking_lots WHERE id=%s", (lot_id,))
    return cursor.fetchone()


def get_session_by_id(connection, session_id):
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT * FROM parking_sessions WHERE id=%s", (session_id,))
    return cursor.fetchone()


def load_sessions_by_user(connection, user_id):
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT * FROM parking_sessions WHERE user=%s", (user_id,))
    return cursor.fetchall()


def mark_sessions_as_paid(connection, user_id):
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE parking_sessions
        SET payment_status = %s
        WHERE user = %s AND stopped IS NOT NULL
        """,
        ("paid", user_id)
    )


def get_unpaid_session_for_user(connection, user_id):
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute(
        """
        SELECT * FROM parking_sessions
        WHERE user=%s AND payment_status=%s AND stopped IS NOT NULL
        LIMIT 1
        """,
        (user_id, "unpaid")
    )
    return cursor.fetchone()


def mark_session_as_refunded(connection, session_id):
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE parking_sessions SET payment_status=%s WHERE id=%s",
        ("refunded", session_id)
    )

def delete_parking_session_by_id(connection, session_id):
    try:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM parking_sessions WHERE id = %s",
            (session_id,)
        )
        connection.commit()
    finally:
        connection.close()