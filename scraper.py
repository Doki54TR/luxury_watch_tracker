"""
This script is the data collection engine (Scraper) for the project.
Uses 'pyvirtualdisplay' to bypass Cloudflare in Docker.
"""

import time
import random
import os
import psycopg2
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# --- SADECE DOCKER/LINUX İÇİN GEREKLİ ---
if os.name == 'posix':
    from pyvirtualdisplay import Display

# --- DATABASE CONFIGURATION ---
db_host = os.getenv("DB_HOST", "localhost")

DB_PARAMS = {
    "host": "db",           # "localhost" yerine doğrudan Docker servis adını yazıyoruz
    "database": "postgres", # docker-compose'daki POSTGRES_DB ile aynı
    "user": "postgres",     # docker-compose'daki POSTGRES_USER ile aynı
    "password": "1234",     # docker-compose'daki POSTGRES_PASSWORD ile aynı
    "port": "5432"
}

TARGET_URLS = [
    {"brand_name": "Longines", "url": "https://www.konyalisaat.com.tr/isvicre-mekanizma/longines"},
    {"brand_name": "Frederique Constant", "url": "https://www.konyalisaat.com.tr/isvicre-mekanizma/frederique-constant"},
]

# --- HELPER FUNCTIONS ---

def clean_price(price_text):
    if not price_text: return 0.0
    clean_text = price_text.replace("TL", "").strip().replace(".", "").replace(",", ".")
    try: return float(clean_text)
    except: return 0.0

def get_or_create_brand_id(conn, brand_name):
    cur = conn.cursor()
    cur.execute("SELECT id FROM brands WHERE name = %s", (brand_name,))
    result = cur.fetchone()
    if result: return result[0]
    else:
        cur.execute("INSERT INTO brands (name) VALUES (%s) RETURNING id", (brand_name,))
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id

def save_to_db(brand_name, name, url, price):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        brand_id = get_or_create_brand_id(conn, brand_name)
        
        cur.execute("SELECT id FROM products WHERE url = %s", (url,))
        result = cur.fetchone()
        
        product_id = None
        if result: product_id = result[0]
        else:
            cur.execute("INSERT INTO products (brand_id, name, url) VALUES (%s, %s, %s) RETURNING id", (brand_id, name, url))
            product_id = cur.fetchone()[0]
            conn.commit()
            print(f"   🆕 New Product: {name[:20]}...")
            
        cur.execute("INSERT INTO prices (product_id, price) VALUES (%s, %s)", (product_id, price))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ DB Error: {e}")

# --- MAIN LOGIC ---

def start_scraping():
    print("🌍 Initializing Browser...")
    
    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    
    # --- DOCKER AYARLARI (SANAL EKRANLI) ---
    if os.name == 'posix': # Docker/Linux
        print("🐧 Running in Linux/Docker Mode (With Virtual Display)...")
        
        # 1. Sanal Ekranı Başlat (Sanki monitör takmışız gibi)
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        
        # 2. Headless modunu KAPAT (Artık ekranımız var!)
        # options.add_argument("--headless=new")  <-- BU SATIRI SİLDİK
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        driver = uc.Chrome(options=options)
    else:
        print("🪟 Running in Windows Mode...")
        driver = uc.Chrome(options=options, use_subprocess=True)

    wait = WebDriverWait(driver, 15)
    
    for target in TARGET_URLS:
        current_brand = target["brand_name"]
        current_url = target["url"]
        
        print(f"\n🚀 STARTING SCRAPE FOR: {current_brand}")
        
        scraped_urls = set()
        try:
            driver.get(current_url)
            # Cloudflare'in bizi "insan" olarak işaretlemesi için biraz bekleyelim
            time.sleep(10) 
            
            print(f"   👀 Page Title: {driver.title}")
            
            while True:
                products = driver.find_elements(By.CSS_SELECTOR, "li[data-productid]")
                
                if len(products) == 0:
                    print("   ⚠️  WARNING: 0 items found!")
                    driver.save_screenshot(f"debug_{current_brand}.png")
                    print(f"   📸 Screenshot saved.")
                    break 

                for p in products:
                    try:
                        try: link = p.find_element(By.TAG_NAME, "a").get_attribute("href")
                        except: continue
                        if link in scraped_urls: continue
                        scraped_urls.add(link)
                        
                        raw_text = p.text.split("\n")
                        name = raw_text[0]
                        price_text = next((line for line in raw_text if "TL" in line), "0,00TL")
                        save_to_db(current_brand, name, link, clean_price(price_text))
                    except: pass
                
                print(f"   📊 {current_brand}: {len(scraped_urls)} items scraped.")

                try:
                    time.sleep(random.uniform(2, 4))
                    btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Daha Fazla')]")
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", btn)
                    try:
                        wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "li[data-productid]")) > len(products))
                    except TimeoutException: break
                except NoSuchElementException:
                    print(f"🏁 Finished scraping {current_brand}.\n")
                    break
                except: break
                
        except Exception as e:
            print(f"❌ Error scraping {current_brand}: {e}")

    # Docker'daysa sanal ekranı kapat
    if os.name == 'posix':
        display.stop()
        
    driver.quit()
    print("\n🎉 ALL OPERATIONS COMPLETED!")

if __name__ == "__main__":
    start_scraping()