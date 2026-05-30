import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import telebot

# التوكن الخاص بك
BOT_TOKEN = "8606943008:AAGcFvCT73iHY71OOhkw2USy8bNMki72g8s"

bot = telebot.TeleBot(BOT_TOKEN)

# أمر ترحيبي
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🤖 أهلاً بك في بوت نخبة العرب! البوت يعمل الآن بنجاح.")

# --- خادم وهمي لتخطي فحص Render ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write("Bot is alive!".encode('utf-8'))

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_health_server, daemon=True)
    server_thread.start()
    
    bot.infinity_polling()
