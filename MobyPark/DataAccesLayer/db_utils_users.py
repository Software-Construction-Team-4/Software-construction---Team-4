import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="145.24.237.71",
        port=8001,
        user="vscode",
        password="StrongPassword123!",
        database="mobypark"
    )

# === LOAD USERS ===
def load_users():
    """Fetch all users from the database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return users
    except Exception as e:
        print(f"Error loading users: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# === SAVE SINGLE USER ===
def save_user(user_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO users
            (username, password, name, email, phone, role, created_at, birth_year, active)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            user_data.get("username"),
            user_data.get("password"),
            user_data.get("name"),
            user_data.get("email"),
            user_data.get("phone"),
            user_data.get("role"),
            user_data.get("created_at"),
            user_data.get("birth_year"),
            user_data.get("active")
        ))
        conn.commit()
    except Exception as e:
        print(f"Error saving user: {e}")
    finally:
        cursor.close()
        conn.close()

# === SAVE MULTIPLE USERS ===
def save_users(users_data):
    """Save a list of user dictionaries."""
    for user in users_data:
        save_user(user)



