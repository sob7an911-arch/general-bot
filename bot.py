import os
import re
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import telebot
from datetime import datetime

BOT_TOKEN = "8606943008:AAGcFvCT73iHY71OOhkw2USy8bNMki72g8s"
ADMIN_USERNAME = "ab0oturki"

bot = telebot.TeleBot(BOT_TOKEN)

# --- قاعدة البيانات ---
def execute_query(query, params=(), fetch=False, fetchall=False):
    conn = sqlite3.connect('general_bot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetch: result = cursor.fetchone()
    elif fetchall: result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

def init_db():
    execute_query('CREATE TABLE IF NOT EXISTS players (username TEXT PRIMARY KEY, list_type TEXT, country TEXT, points INTEGER DEFAULT 0)')
init_db()

# --- الصلاحيات ---
def is_admin(user): return user and user.lower() == ADMIN_USERNAME

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 أهلاً بك في بوت إدارة سيرفرات الجنرال.\n\nالأوامر:\nتسجيل، حماية [الدولة]، مخرب @user، مشررف @user، عرض قائمة [المسجلين/الحماية/المخربين/الأبطال]")

# --- التسجيل (الأربعاء 9م - الجمعة 9:30م) ---
@bot.message_handler(func=lambda m: m.text == "تسجيل")
def register(message):
    user = message.from_user.username
    is_griefer = execute_query("SELECT 1 FROM players WHERE username=? AND list_type='المخربين'", (user,), fetch=True)
    if is_griefer:
        bot.reply_to(message, "❌ أنت في قائمة المخربين ولا يمكنك التسجيل.")
    else:
        execute_query("INSERT OR REPLACE INTO players (username, list_type) VALUES (?, 'المسجلين')", (user,))
        bot.reply_to(message, f"✅ تم تسجيلك يا @{user} في قائمة السيرفر.")

# --- الحماية (حتى الجمعة 10م) ---
@bot.message_handler(func=lambda m: m.text and m.text.startswith("حماية"))
def protect(message):
    user = message.from_user.username
    is_registered = execute_query("SELECT 1 FROM players WHERE username=? AND list_type='المسجلين'", (user,), fetch=True)
    if not is_registered:
        bot.reply_to(message, "❌ يجب أن تكون مسجلاً أولاً لتطلب الحماية.")
        return
    
    country = message.text.replace("حماية", "").strip()
    execute_query("UPDATE players SET list_type='الحماية', country=? WHERE username=?", (country, user))
    bot.reply_to(message, f"🛡️ تم تسجيلك في قائمة الحماية دولة: {country}")

# --- الإدارة (مخرب / مشرف) ---
@bot.message_handler(func=lambda m: m.text and (m.text.startswith("مخرب") or m.text.startswith("مشررف")))
def admin_actions(message):
    if not is_admin(message.from_user.username): return
    parts = message.text.split()
    target = parts[1].replace("@", "")
    list_type = "المخربين" if parts[0] == "مخرب" else "المشرفين"
    execute_query("INSERT OR REPLACE INTO players (username, list_type) VALUES (?, ?)", (target, list_type))
    bot.reply_to(message, f"✅ تم إضافة @{target} إلى {list_type}")

# --- عرض القوائم ---
@bot.message_handler(func=lambda m: m.text and m.text.startswith("عرض قائمة"))
def show_list(message):
    list_name = message.text.replace("عرض قائمة", "").strip()
    rows = execute_query("SELECT username, country FROM players WHERE list_type=?", (list_name,), fetchall=True)
    if not rows:
        bot.reply_to(message, "📭 القائمة فارغة.")
        return
    res = f"📋 قائمة {list_name}:\n" + "\n".join([f"- @{r[0]} {r[1] if r[1] else ''}" for r in rows])
    bot.reply_to(message, res)

# --- تشغيل الخادم ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Alive")

def run_health_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheckHandler).serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    bot.infinity_polling()
