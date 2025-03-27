import os

import psycopg2

DB_HOST = "localhost"
DB_NAME = "stocks_data"
DB_USER = "postgres"
DB_PASSWORD = "Borealis"
CSV_DIR = "Stocks"

try:
    with psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
    ) as conn:
        print("Database connection established.")

        with conn.cursor() as cur:
            for file_name in os.listdir(CSV_DIR):
                if file_name.endswith(".csv"):
                    # Sanitize table name
                    table_name = os.path.splitext(file_name)[0] \
                        .replace(" ", "_").replace("-", "_")
                    csv_path = os.path.join(CSV_DIR, file_name)

                    # Check if table exists using information_schema.tables
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = %s
                        );
                    """, (table_name,))
                    table_exists = cur.fetchone()[0]

                    if not table_exists:
                        # Create new table and import data
                        try:
                            cur.execute(f"""
                                CREATE TABLE "{table_name}" (
                                    Date DATE PRIMARY KEY,
                                    Close NUMERIC(10, 2),
                                    High NUMERIC(10, 2),
                                    Low NUMERIC(10, 2),
                                    Open NUMERIC(10, 2),
                                    Volume BIGINT
                                );
                            """)
                            with open(csv_path, 'r', encoding='utf-8') as f:
                                cur.copy_expert(
                                    f'COPY "{table_name}" FROM STDIN WITH CSV HEADER',
                                    f
                                )
                            conn.commit()
                            print(f"Created '{table_name}' and imported data")

                        except Exception as e:
                            print(f"Error creating {table_name}: {e}")
                            conn.rollback()
                    else:
                        # Append new dates using temporary table
                        try:
                            # Create temp table without constraints
                            cur.execute(f"""
                                CREATE TEMP TABLE temp_import 
                                (LIKE "{table_name}" EXCLUDING CONSTRAINTS);
                            """)

                            # Import CSV to temp table
                            with open(csv_path, 'r', encoding='utf-8') as f:
                                cur.copy_expert(
                                    'COPY temp_import FROM STDIN WITH CSV HEADER',
                                    f
                                )

                            # Insert new records with conflict handling
                            cur.execute(f"""
                                INSERT INTO "{table_name}"
                                SELECT * FROM temp_import
                                ON CONFLICT (Date) DO NOTHING;
                            """)
                            conn.commit()
                            print(f"Updated {table_name} with new data")

                        except Exception as e:
                            print(f"Error updating {table_name}: {e}")
                            conn.rollback()

except Exception as e:
    print(f"Database connection failed: {e}")
finally:
    print("Database connection closed")
