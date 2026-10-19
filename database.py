import sqlite3
from pathlib import Path


# ==================================================
# DATABASE LOCATION
# ==================================================

DATABASE_DIR = Path("database")
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "shop.db"


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():
    """Create and return a database connection."""

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# ==================================================
# CREATE TABLES
# ==================================================

def create_tables():
    """Create all system tables if they do not exist."""

    connection = get_connection()
    cursor = connection.cursor()

    # ==================================================
    # USERS / WORKERS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'WORKER',
            phone TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ==================================================
    # PRODUCTS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL DEFAULT 'Other',
            brand TEXT,
            name TEXT NOT NULL UNIQUE,
            unit TEXT NOT NULL DEFAULT 'piece',
            reorder_percentage REAL NOT NULL DEFAULT 25.0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ==================================================
    # PURCHASES / STOCK IN
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL CHECK(quantity > 0),
            buying_price REAL NOT NULL CHECK(buying_price >= 0),
            purchase_date TEXT NOT NULL,
            user_id INTEGER,
            notes TEXT,

            FOREIGN KEY (product_id)
                REFERENCES products(id),

            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)

    # ==================================================
    # SALES
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL CHECK(quantity > 0),
            selling_price REAL NOT NULL CHECK(selling_price >= 0),
            cost_price REAL NOT NULL DEFAULT 0,
            profit REAL NOT NULL DEFAULT 0,
            sale_date TEXT NOT NULL,
            user_id INTEGER,
            notes TEXT,

            FOREIGN KEY (product_id)
                REFERENCES products(id),

            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)

    # ==================================================
    # EXPENSES
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL CHECK(amount > 0),
            expense_date TEXT NOT NULL,
            user_id INTEGER,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)

    # ==================================================
    # LOW STOCK ALERTS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            stock_quantity REAL NOT NULL,
            threshold_quantity REAL NOT NULL,
            alert_date TEXT NOT NULL,
            notification_sent INTEGER NOT NULL DEFAULT 0,
            resolved INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (product_id)
                REFERENCES products(id)
        )
    """)

    connection.commit()
    connection.close()


# ==================================================
# UPDATE PRODUCTS TABLE
# ==================================================

def update_products_table():
    """Add category and brand to an existing products table."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "PRAGMA table_info(products)"
    )

    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]

    if "category" not in columns:

        cursor.execute("""
            ALTER TABLE products
            ADD COLUMN category TEXT
            NOT NULL DEFAULT 'Other'
        """)

    if "brand" not in columns:

        cursor.execute("""
            ALTER TABLE products
            ADD COLUMN brand TEXT
        """)

    connection.commit()
    connection.close()


# ==================================================
# UPDATE SALES TABLE
# ==================================================

def update_sales_table():
    """Add cost price and profit to an existing sales table."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "PRAGMA table_info(sales)"
    )

    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]

    if "cost_price" not in columns:

        cursor.execute("""
            ALTER TABLE sales
            ADD COLUMN cost_price REAL
            NOT NULL DEFAULT 0
        """)

    if "profit" not in columns:

        cursor.execute("""
            ALTER TABLE sales
            ADD COLUMN profit REAL
            NOT NULL DEFAULT 0
        """)

    connection.commit()
    connection.close()


# ==================================================
# INITIALIZE DATABASE


if __name__ == "__main__":

    create_tables()

    update_products_table()

    update_sales_table()

    print("Database updated successfully.")