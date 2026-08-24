from config import get_connection

try:
    conn = get_connection()
    print("✅ Connected to PostgreSQL successfully!")

    conn.close()

except Exception as e:
    print("❌ Connection failed.")
    print(e)