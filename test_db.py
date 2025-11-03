import os
import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector

print("Attempting to connect to the database...")

try:
    conn = psycopg2.connect(
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"],
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
    )
    conn.autocommit = True
    print("Connection successful.")

    register_vector(conn)
    print("register_vector(conn) executed.")

    with conn.cursor() as cur:
        print("Cursor created. Executing query...")
        # Use a numpy array and explicit cast
        embedding = np.array([0.1, 0.2, 0.3])
        cur.execute("SELECT %s::vector", (embedding,))
        result = cur.fetchone()[0]
        print("Query successful!")
        print(f"Successfully retrieved vector of type: {type(result)}")

except Exception as e:
    print("--- AN ERROR OCCURRED ---")
    print(type(e))
    print(e)

finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("Connection closed.")
