from database import get_connection, create_tables


def create_admin():
    create_tables()

    connection = get_connection()
    cursor = connection.cursor()

    # Check whether an admin already exists
    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        ("admin",)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        print("Admin user already exists.")
    else:
        cursor.execute("""
            INSERT INTO users
            (full_name, username, password, role, phone)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "System Administrator",
            "admin",
            "admin123",
            "ADMIN",
            ""
        ))

        connection.commit()

        print("Admin user created successfully.")
        print("Username: admin")
        print("Password: admin123")

    connection.close()


if __name__ == "__main__":
    create_admin()