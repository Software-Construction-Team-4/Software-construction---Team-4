import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="145.24.237.71",
        port=8001,
        user="vscode",
        password="StrongPassword123!",
        database="mobypark"
    )

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


def update_user_data(user):
    if "id" not in user:
        raise ValueError("User must have an 'id' to update")

    conn = get_db_connection()
    cursor = conn.cursor()

    db_columns = [
        "username",
        "password",
        "name",
        "email",
        "phone",
        "role",
        "birth_year",
        "active"
    ]

    updates = {col: user[col] for col in db_columns if col in user}

    if not updates:
        print(f"No fields to update for user {user['id']}")
        cursor.close()
        conn.close()
        return

    set_clause = ", ".join(f"{col}=%s" for col in updates.keys())
    sql = f"UPDATE users SET {set_clause} WHERE id=%s"

    values = list(updates.values())
    values.append(user["id"])

    try:
        cursor.execute(sql, values)
        conn.commit()
        print(f"User {user['id']} updated successfully!")
    except mysql.connector.Error as e:
        print("Error updating user:", e)
    finally:
        cursor.close()
        conn.close()


