
import mysql.connector
import pandas as pd
from mysql.connector import Error


# 1. Connect to MySQL
def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="YOUR_MYSQL_PASSWORD",
            database="personal_finance"
        )

        if connection.is_connected():
            return connection

    except Error as e:
        print("Database connection failed:", e)

    return None


# 2. Create the database if it does not exist
def create_database():
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="YOUR_MYSQL_PASSWORD"
        )

        cursor = connection.cursor()
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS personal_finance"
        )

        print("Database created or already exists.")

    except Error as e:
        print("Error creating database:", e)

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# 3. Create the transactions table
def create_table():
    connection = get_connection()

    if connection is None:
        return

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INT AUTO_INCREMENT PRIMARY KEY,
            transaction_date DATE NOT NULL,
            description VARCHAR(255),
            category VARCHAR(100),
            transaction_type ENUM('Income', 'Expense') NOT NULL,
            amount DECIMAL(12, 2) NOT NULL,
            payment_method VARCHAR(50)
        )
        """

        cursor.execute(query)
        connection.commit()

        print("Transactions table is ready.")

    except Error as e:
        print("Error creating table:", e)

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


# 4. Insert one transaction
def insert_transaction(date, description, category,
                       transaction_type, amount, payment_method):

    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
        INSERT INTO transactions
        (transaction_date, description, category,
         transaction_type, amount, payment_method)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            date,
            description,
            category,
            transaction_type,
            amount,
            payment_method
        )

        cursor.execute(query, values)
        connection.commit()

        print("Transaction inserted successfully.")
        return True

    except Error as e:
        connection.rollback()
        print("Error inserting transaction:", e)
        return False

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


# 5. Insert transactions from a Pandas DataFrame
def insert_dataframe(df):
    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:
        required_columns = [
            "transaction_date",
            "description",
            "category",
            "transaction_type",
            "amount",
            "payment_method"
        ]

        missing = set(required_columns) - set(df.columns)

        if missing:
            raise ValueError(
                f"Missing columns: {sorted(missing)}"
            )

        data = df[required_columns].copy()

        data["transaction_date"] = pd.to_datetime(
            data["transaction_date"],
            errors="raise"
        ).dt.date

        data["amount"] = pd.to_numeric(
            data["amount"],
            errors="raise"
        )

        if data["amount"].isna().any() or (
            data["amount"] < 0
        ).any():
            raise ValueError("Amounts must be non-negative.")

        if not data["transaction_type"].isin(
            ["Income", "Expense"]
        ).all():
            raise ValueError(
                "transaction_type must be Income or Expense."
            )

        if data["transaction_date"].isna().any():
            raise ValueError("Transaction dates cannot be empty.")

        query = """
        INSERT INTO transactions
        (transaction_date, description, category,
         transaction_type, amount, payment_method)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = list(data.itertuples(index=False, name=None))

        cursor = connection.cursor()
        cursor.executemany(query, values)
        connection.commit()

        print(f"{cursor.rowcount} transactions inserted.")
        return True

    except (Error, ValueError, TypeError) as e:
        connection.rollback()
        print("Error importing transactions:", e)
        return False

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


# 6. Fetch all transactions
def fetch_transactions():
    connection = get_connection()

    if connection is None:
        return pd.DataFrame()

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM transactions
            ORDER BY transaction_date DESC
        """)

        records = cursor.fetchall()
        return pd.DataFrame(records)

    except Error as e:
        print("Error fetching transactions:", e)
        return pd.DataFrame()

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


# 7. Display all transactions
def display_transactions():
    df = fetch_transactions()

    if df.empty:
        print("No transactions found.")
    else:
        print(df.to_string(index=False))


# 8. Initialize database and table
if __name__ == "__main__":
    create_database()
    create_table()

    # Example transaction
    # Uncomment to insert a test record.
    #
    # insert_transaction(
    #     "2026-10-01",
    #     "Monthly salary",
    #     "Salary",
    #     "Income",
    #     25000,
    #     "Bank Transfer"
    # )

    display_transactions()
