"""
This script launches a web-based Dashboard using Streamlit to visualize the collected data.

It connects to the PostgreSQL database, retrieves comprehensive product information 
(joining Brands, Products, and Prices tables), and provides an interactive interface for:
- Filtering watches by Brand and Specific Models.
- Viewing real-time price metrics (Current, Lowest, and Highest prices).
- Visualizing price trends over time with dynamic line charts.
- Inspecting raw data logs in a tabular format.

To run the dashboard, use the command:
python -m streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import psycopg2
import yfinance as yf
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Multi-Brand Watch Tracker", page_icon="⌚", layout="wide")

# --- DATABASE PARAMETERS ---
db_host = os.getenv("DB_HOST", "localhost")

DB_PARAMS = {
    "host": db_host,
    "database": "postgres",
    "user": "postgres",
    "password": "1234",
    "port": "5432"
}

@st.cache_data
def load_data():
    """
    Fetches data by joining 3 tables: prices -> products -> brands
    """
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        
        # UPDATED QUERY: 3-Table Join
        query = """
        SELECT 
            b.name as brand,
            p.name as product, 
            p.url, 
            pr.price, 
            pr.scraped_at
        FROM prices pr
        JOIN products p ON pr.product_id = p.id
        JOIN brands b ON p.brand_id = b.id
        ORDER BY pr.scraped_at DESC
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database Error: {e}")
        return pd.DataFrame()

def main():
    st.title("⌚ Luxury Watch Market Tracker")
    st.markdown("Real-time price tracking for multiple brands.")
    st.markdown("---")

    df = load_data()
    
    if df.empty:
        st.warning("No data found. Please run the scraper.")
        return

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("🔍 Filters")
    
    # 1. Filter by Brand
    brand_list = ["All"] + list(df['brand'].unique())
    selected_brand = st.sidebar.selectbox("Select Brand:", brand_list)
    
    # Apply Brand Filter
    if selected_brand != "All":
        filtered_df = df[df['brand'] == selected_brand]
    else:
        filtered_df = df

    # 2. Filter by Product (Dependent on Brand)
    product_list = filtered_df['product'].unique()
    selected_product = st.sidebar.selectbox("Select Watch:", product_list)
    
    # Final Data for Charts
    product_data = df[df['product'] == selected_product].sort_values(by="scraped_at")

    # --- METRICS ---
    if not product_data.empty:

        st.markdown("---")
        st.subheader("💶 Price vs Euro/TRY Correlation")
        
        # Prepare data for chart
        watch_chart = product_data.set_index("scraped_at")["price"]
        
        # Take the euro data from the start date of the watch data
        # Finding the watch data start date
        start_date = product_data["scraped_at"].min().strftime("%Y-%m-%d")
        
        try:
            # EURTRY=X means Euro to Turkish Lira exchange rate
            currency_data = yf.download("EURTRY=X", start=start_date, progress=False)
            
            # Prepare data for chart
            if not currency_data.empty:
                # Two-axis chart requires careful handling in Streamlit
                chart_df = pd.DataFrame({
                    "Watch Price (TL)": watch_chart,
                })
                
                # Euro data needs to be resampled to match the watch data frequency, but for simplicity we'll keep it as is.
                # Streamlit's dual-axis charts are tricky, so we'll show two separate charts.
                
                st.line_chart(watch_chart)
                st.caption("👆 Watch Price Trend")
                
                st.line_chart(currency_data["Close"])
                st.caption("👆 Euro/TL Exchange Rate Trend")
                
                st.info("💡 Compare the peaks. Did the price increase because Euro went up?")
            else:
                st.warning("Could not fetch currency data.")
                
        except Exception as e:
            st.error(f"Currency API Error: {e}")
        current_price = product_data.iloc[-1]['price']
        min_price = product_data['price'].min()
        max_price = product_data['price'].max()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"₺{current_price:,.2f}")
        col2.metric("Lowest Price", f"₺{min_price:,.2f}")
        col3.metric("Highest Price", f"₺{max_price:,.2f}")
        
        # --- CHART ---
        st.subheader(f"📉 Price History: {selected_product}")
        st.line_chart(product_data.set_index("scraped_at")["price"])
    
    # --- RAW DATA ---
    st.subheader("📄 Latest Data Logs")
    st.dataframe(filtered_df)
    
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()