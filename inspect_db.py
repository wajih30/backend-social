import psycopg2
from app.core.config import settings

def inspect_users_table():
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users';
        """)
        columns = cur.fetchall()
        print("Columns in 'users' table:")
        for col in columns:
            print(f" - {col[0]}: {col[1]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_users_table()
