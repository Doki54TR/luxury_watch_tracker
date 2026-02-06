import requests

# The token of SaatMessager Bot: 8385351744:AAGTca5jynDIDoLj8nx8KZwJDG6TDJQq2yc
TOKEN = "8385351744:AAGTca5jynDIDoLj8nx8KZwJDG6TDJQq2yc" 

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
response = requests.get(url).json()

try:
    chat_id = response["result"][0]["message"]["chat"]["id"]
    print(f"\n✅ Your chat id: {chat_id}")
    print("Don't forget to save this ID!")
except:
    print("❌ Error. I couldn't retrieve your chat ID. Please send a message to the bot first.")