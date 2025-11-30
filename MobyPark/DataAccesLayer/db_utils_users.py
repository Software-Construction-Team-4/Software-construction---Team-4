import mysql.connector
from DataModels.userModel import userModel

def get_db_connection():
    return mysql.connector.connect(
        host="145.24.237.71",
        port=8001,
        user="vscode",
        password="StrongPassword123!",
        database="mobypark"
    )

#  Laat alle dubbele users zien

# def find_duplicate_users():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     try:
#         sql = """
#         SELECT username, COUNT(*) AS count
#         FROM users
#         GROUP BY username
#         HAVING COUNT(*) > 1
#         ORDER BY count DESC;
#         """

#         cursor.execute(sql)
#         duplicates = cursor.fetchall()

#         if not duplicates:
#             print("No duplicate users found.")
#             return

#         print("Duplicate usernames:")
#         for row in duplicates:
#             print(f"{row['username']}: {row['count']}")

#     except Exception as e:
#         print(f"Error detecting duplicates: {e}")

#     finally:
#         cursor.close()
#         conn.close()

# DUBBELE USERS WORDEN INACTIVE

# def deactivate_duplicate_users():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     try:
#         sql = """
#         UPDATE users u
#         JOIN (
#             SELECT username, MIN(id) AS keep_id
#             FROM users
#             GROUP BY username
#         ) x ON u.username = x.username
#         SET u.active = 0
#         WHERE u.id <> x.keep_id;
#         """
#         cursor.execute(sql)
#         conn.commit()
#         print("Duplicate users have been set to inactive (active = 0).")

#     except Exception as e:
#         print(f"Error deactivating duplicate users: {e}")
#         conn.rollback()

#     finally:
#         cursor.close()
#         conn.close()

# def load_users():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     users_list = []

#     try:
#         cursor.execute("SELECT * FROM users")
#         rows = cursor.fetchall()

#         for row in rows:
#             user = userModel(
#                 id=row["id"],
#                 username=row["username"],
#                 password=row["password"],
#                 name=row["name"],
#                 email=row["email"],
#                 phone=row["phone"],
#                 role=row["role"],
#                 created_at=row["created_at"],
#                 birth_year=row["birth_year"],
#                 active=row["active"]
#             )
#             users_list.append(user)

#         return users_list

#     except Exception as e:
#         print(f"Error loading users: {e}")
#         return []

#     finally:
#         cursor.close()
#         conn.close()


def save_user(user: userModel):
    if not isinstance(user, userModel):
        raise TypeError("user must be a of type userModel")

    data = user.to_dict()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """
        INSERT INTO users
            (username, password, name, email, phone, role, created_at, birth_year, active)
        VALUES
            (%(username)s, %(password)s, %(name)s, %(email)s, %(phone)s,
             %(role)s, %(created_at)s, %(birth_year)s, %(active)s)
        """

        cursor.execute(sql, data)
        conn.commit()

    except Exception as e:
        print(f"Error saving user: {e}")

    finally:
        cursor.close()
        conn.close()



def update_user_data(user: userModel):
    if not isinstance(user, userModel):
        raise TypeError("Expected userModel instance")
    if user.id is None:
        raise ValueError("User must have an 'id' to update")

    conn = get_db_connection()
    cursor = conn.cursor()

    fields = {
        "username": user.username,
        "password": user.password,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "birth_year": user.birth_year,
        "active": user.active
    }

    updates = {k: v for k, v in fields.items() if v is not None}

    if not updates:
        return

    sql = f"UPDATE users SET {', '.join(f'{k}=%s' for k in updates)} WHERE id=%s"
    values = list(updates.values()) + [user.id]

    try:
        cursor.execute(sql, values)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


