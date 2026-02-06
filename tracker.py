import psycopg2
import requests
import os
import statistics

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8385351744:AAGTca5jynDIDoLj8nx8KZwJDG6TDJQq2yc"
CHAT_ID = "5659670640"
db_host = os.getenv("DB_HOST", "localhost")

DB_PARAMS = {
    "host": db_host,
    "database": "postgres",
    "user": "postgres",
    "password": "1234",
    "port": "5432"
}

def send_telegram_message(message):
    """Sends a formatted notification to the Telegram bot."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try: 
        requests.post(url, json=payload)
    except Exception as e: 
        print(f"❌ Telegram API Error: {e}")

def calculate_insights(price_history):
    """
    Performs statistical analysis on the price history.
    Returns z-score and a recommendation status.
    """
    if len(price_history) < 3:
        return None, "Collecting more data..."

    prices = [float(p[0]) for p in price_history]
    current_price = prices[0]
    avg_price = statistics.mean(prices)
    
    # Standard deviation might be 0 if all prices are same
    try:
        stdev = statistics.stdev(prices)
    except statistics.StatisticsError:
        stdev = 0

    if stdev == 0:
        return 0, "Stable Price"

    # Z-Score formula
    z_score = (current_price - avg_price) / stdev
    
    if z_score < -1.2:
        status = "🔥 STRONG BUY (Deep Discount)"
    elif z_score < 0:
        status = "✅ Good Deal"
    elif z_score > 1.2:
        status = "⚠️ Overpriced (Wait)"
    else:
        status = "📊 Fair Market Value"
        
    return z_score, status

def check_price_changes():
    """Analyzes price history and sends AI-driven insights."""
    print("🔍 Analyzing market data for insights...\n")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Join brands and products to get full context
        cur.execute("""
            SELECT p.id, p.name, b.name, p.url 
            FROM products p
            JOIN brands b ON p.brand_id = b.id
        """)
        products = cur.fetchall()
        
        for product in products:
            p_id, p_name, brand_name, p_url = product
            
            # Fetch ALL price history for this product to do statistics
            cur.execute("""
                SELECT price FROM prices 
                WHERE product_id = %s 
                ORDER BY scraped_at DESC
            """, (p_id,))
            price_history = cur.fetchall()
            
            if len(price_history) >= 2:
                current_price = float(price_history[0][0])
                old_price = float(price_history[1][0])
                
                # Perform Statistical Analysis
                z_score, deal_status = calculate_insights(price_history)

                # Only notify if price changed OR it's a 'Strong Buy'
                if current_price != old_price:
                    diff = current_price - old_price
                    percent = abs((diff / old_price) * 100)
                    
                    title = "🚨 <b>PRICE MOVEMENT DETECTED</b>"
                    icon = "📉" if current_price < old_price else "📈"
                    
                    msg = (
                        f"{title}\n\n"
                        f"🏷️ <b>{brand_name}</b>\n" 
                        f"⌚ {p_name}\n"
                        f"❌ Old: {old_price:,.0f} TL\n"
                        f"✅ New: <b>{current_price:,.0f} TL</b> (%{percent:.1f})\n"
                        f"---------------------------\n"
                        f"🧠 <b>AI INSIGHT:</b> {deal_status}\n"
                        f"📉 <b>Z-Score:</b> {z_score:.2f} (vs History)\n"
                        f"---------------------------\n"
                        f"🔗 <a href='{p_url}'>Check Watch</a>"
                    )
                    
                    print(f"SENT: {brand_name} - {deal_status}")
                    send_telegram_message(msg)

        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error in tracker: {e}")

if __name__ == "__main__":
    check_price_changes()