import psycopg2
import os

#db_host = os.getenv("DB_HOST", "localhost")

DB_PARAMS = {
    "host": "db",           # "localhost" yerine doğrudan Docker servis adını yazıyoruz
    "database": "postgres", # docker-compose'daki POSTGRES_DB ile aynı
    "user": "postgres",     # docker-compose'daki POSTGRES_USER ile aynı
    "password": "1234",     # docker-compose'daki POSTGRES_PASSWORD ile aynı
    "port": "5432"
}

def setup_relational_db():
    print("🔌 Connecting to database...")
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # First, drop existing tables if they exist
        # Order matters due to foreign key constraints
        cur.execute("DROP TABLE IF EXISTS prices;")
        cur.execute("DROP TABLE IF EXISTS products;")
        cur.execute("DROP TABLE IF EXISTS brands;")
        
        # 1. BRANDS TABLE 
        print("🛠️ 'brands' tablosu oluşturuluyor...")
        cur.execute("""
        CREATE TABLE brands (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        );
        """)
        
        # 2. PRODUCTS TABLE (Connects to BRANDS with Foreign Key (brand_id))
        print("🛠️ 'products' tablosu oluşturuluyor...")
        cur.execute("""
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            brand_id INTEGER REFERENCES brands(id), --- (Foreign Key)
            name VARCHAR(255) NOT NULL,
            url TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 3. PRICES TABLE
        print("🛠️ 'prices' tablosu oluşturuluyor...")
        cur.execute("""
        CREATE TABLE prices (
            id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(id),
            price DECIMAL(12, 2),
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.commit()
        print("\n✅ Perfect Database is now Relational.")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    setup_relational_db()