import psycopg2
import os

db_host = os.getenv("DB_HOST", "localhost")

DB_PARAMS = {
    "host": db_host,
    "database": "postgres",
    "user": "postgres",
    "password": "1234",
    "port": "5432"
}

try:
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    # Finding the first product to insert a fake old high price
    cur.execute("SELECT id, name FROM products LIMIT 1")
    first_product = cur.fetchone()
    
    if first_product:
        p_id = first_product[0]
        print(f"🧪 Chosen watch for test: {first_product[1]}")
        
        # Inserting a fake old high price
        # We set it to 500,000 TL for testing purposes
        cur.execute("""
            INSERT INTO prices (product_id, price, scraped_at) 
            VALUES (%s, 500000.00, NOW() - INTERVAL '1 day')
        """, (p_id,))
        
        conn.commit()
        print("✅ Fake old high price inserted successfully.")
    
    cur.close()
    conn.close()
except Exception as e:
    print(e)