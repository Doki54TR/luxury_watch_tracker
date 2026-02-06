"""
This script connects to the PostgreSQL database, retrieves combined brand, product, and price data 
using a multi-table SQL JOIN operation, and displays a formatted list of all scraped records.
"""

import psycopg2
import os

# --- Settings ---
db_host = os.getenv("DB_HOST", "localhost")

DB_PARAMS = {
    "host": db_host,
    "database": "postgres",
    "user": "postgres",
    "password": "1234",
    "port": "5432"
}

def analyze_data():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # SQL Query (JOINING brands, products and prices tables)
        # b: aliases of brands table
        # p: aliases of products table
        # pr: aliases of prices table
        query = """
        SELECT 
            b.name as brand,
            p.name as product, 
            pr.price, 
            pr.scraped_at 
        FROM prices pr
        JOIN products p ON pr.product_id = p.id
        JOIN brands b ON p.brand_id = b.id
        ORDER BY pr.scraped_at DESC;
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        
        print(f"\n📊 Total records: {len(rows)}")
        print("-" * 85)
        # Tablo başlıklarına BRAND sütununu da ekledik
        print(f"{'BRAND':<20} | {'PRODUCT NAME':<40} | {'PRICE (TL)':<15} | {'DATE'}")
        print("-" * 85)
        
        for row in rows:
            brand = row[0]
            # Ürün ismi çok uzunsa kısalt
            name = row[1][:37] + "..." if len(row[1]) > 37 else row[1]
            price = f"{row[2]:,.2f}"
            date = row[3].strftime("%Y-%m-%d %H:%M")
            
            # Artık markayı da yazdırıyoruz
            print(f"{brand:<20} | {name:<40} | {price:<15} | {date}")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_data()