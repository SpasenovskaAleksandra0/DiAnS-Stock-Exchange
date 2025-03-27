import os

import psycopg2

# Database connection parameters
DB_HOST = "db"
DB_NAME = "pgstockdatabase"
DB_PORT = "5432"
DB_USER = "postgres"
DB_PASSWORD = "db_user_pass"

# Directory containing CSV files
CSV_DIR = "Stocks"

# Connect to the PostgreSQL database
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    print("Database connection established.")
except Exception as e:
    print(f"Error connecting to the database: {e}")
    exit()

# Create a cursor object
cur = conn.cursor()

# Loop through each CSV file in the directory
for file_name in os.listdir(CSV_DIR):
    if file_name.endswith(".csv"):
        # Extract table name from file name (without extension)
        table_name = os.path.splitext(file_name)[0]

        # SQL script to create the table
        CREATE_TABLE_SQL = f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            Date DATE PRIMARY KEY,
            Close NUMERIC(10, 2),
            High NUMERIC(10, 2),
            Low NUMERIC(10, 2),
            Open NUMERIC(10, 2),
            Volume BIGINT
        );
        """

        # Execute the SQL script to create the table
        try:
            cur.execute(CREATE_TABLE_SQL)
            conn.commit()
            print(f"Table '{table_name}' created or already exists.")
        except Exception as e:
            print(f"Error creating the table '{table_name}': {e}")

# Close the cursor and connection
cur.close()
conn.close()
print("Database connection closed.")