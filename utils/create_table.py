# pyrefly: ignore [missing-import]
import mysql.connector

def create_database_and_table():
    # Connection parameters (same as mcp/db_connector.py)
    host = "localhost"
    user = "root"
    password = "P@ssw0rd"
    database = "qna_chatbot"
    port = 3306

    print(f"Connecting to MySQL server at {host}:{port} as {user}...")
    try:
        # First connect without specifying the database to ensure it exists
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        cursor = conn.cursor()
        
        # Create database if not exists
        print(f"Creating database '{database}' if it doesn't exist...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        conn.commit()
        cursor.close()
        conn.close()

        # Connect directly to the database now
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        cursor = conn.cursor()

        # SQL to create the transactions table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS transactions (
            id INT PRIMARY KEY,
            trans_date_trans_time DATETIME,
            cc_num VARCHAR(50),
            merchant VARCHAR(255),
            category VARCHAR(100),
            amt DECIMAL(10, 2),
            first VARCHAR(100),
            last VARCHAR(100),
            gender CHAR(1),
            street VARCHAR(255),
            city VARCHAR(100),
            state VARCHAR(50),
            zip VARCHAR(20),
            lat DECIMAL(9, 6),
            `long` DECIMAL(9, 6),
            city_pop INT,
            job VARCHAR(255),
            dob DATE,
            trans_num VARCHAR(100) UNIQUE,
            unix_time BIGINT,
            merch_lat DECIMAL(9, 6),
            merch_long DECIMAL(9, 6),
            is_fraud TINYINT(1)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """

        print("Creating 'transactions' table...")
        cursor.execute(create_table_sql)
        conn.commit()
        print("Table 'transactions' created successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    create_database_and_table()
