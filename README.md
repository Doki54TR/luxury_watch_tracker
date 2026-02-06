⌚ Luxury Watch Market Tracker
An automated, cloud-based data ecosystem designed to monitor, analyze, and visualize price trends in the luxury watch market. This project demonstrates a full-stack engineering approach, combining real-time web scraping, relational database management, and cloud deployment.

🚀 Key Features
Automated Scraping: Continuous data collection from multiple watch retailers using Selenium and Undetected-ChromeDriver to bypass anti-bot mechanisms.

Microservice Architecture: Fully containerized using Docker and Docker Compose, separating the scraper, database, and dashboard for scalability.

Cloud Deployment: Hosted on Google Cloud Platform (GCP), ensuring 24/7 uptime and remote accessibility.

Market Analysis (AI-ready): Calculations for price volatility and market sentiment (Buy/Hold) based on historical data stored in PostgreSQL.

Real-time Dashboard: Interactive data visualization using Streamlit, allowing users to filter by brand, price, and time-frame.

🛠️ Tech Stack
Language: Python 3.10

Automation: Selenium, Undetected-Chromedriver, Xvfb (Virtual Display)

Database: PostgreSQL 15

Infrastructure: Docker, Docker Compose

Cloud: Google Cloud Platform (Compute Engine)

Data Science: Pandas, NumPy

Visualization: Streamlit

🏗️ System Architecture
Scraper Service: Runs periodically to fetch live price data.

PostgreSQL Service: Stores structured data (Brands, Products, Prices) with relational integrity.

Dashboard Service: Provides a user-friendly web interface for market analysis.

⚙️ Installation & Deployment (Local/Cloud)
Clone the repository:

Bash

git clone https://github.com/yourusername/luxury_watch_tracker.git
cd luxury_watch_tracker
Configure Environment: Update the database connection parameters in scraper.py, setup_db.py, and dashboard.py.

Deploy with Docker:

Bash

docker-compose up --build -d
Initialize Database:

Bash

docker exec -it watch_tracker_app python setup_db.py
📈 Future Goals
Telegram Integration: Implement real-time push notifications for "Deep Deal" opportunities.

Advanced Analytics: Add Support Vector Machine (SVM) models to predict future price trends based on historical data.

Multi-Currency Support: Integrate an API to show prices in USD, EUR, and TRY dynamically.
