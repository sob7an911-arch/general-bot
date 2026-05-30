import os
import re
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import telebot

# التوكن الخاص بك
BOT_TOKEN = "8606943008:AAGcFvCT73iHY71OOhkw2USy8bNMki72g8s"

bot = telebot.TeleBot(BOT_TOKEN)

# ================== قاعدة البيانات ==================
def execute_query(query, params=(), fetch=False, fetchall=False):
    conn = sqlite3.connect('general_bot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetch:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

def init_db():
    execute_query('''
        CREATE TABLE IF NOT EXISTS players (
            username TEXT PRIMARY KEY,
            list_type TEXT
        )
    ''')

init_db()

def get_list_en(list_ar):
    if "مخرب" in list_ar:
        return "المخربين"
    elif "مشرف" in list_ar:
        return "المشرفين"
    elif "مسجل" in list_ar:
        return "المسجلين"
    return None

# ================== أوامر البوت ==================

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (
        "🤖 أهلاً بك في بوت إدارة مجتمع الجنرال (نخبة العرب).\n\n"
        "📌 <b>الأوامر المتاحة:</b>\n"
        "➕ أضف @اسم_اللاعب إلى قائمة المخربين\n"
        "➖ احذف @اسم_اللاعب من قائمة المخربين\n"
        "📋 عرض قائمة المخربين\n\n"
        "<i>(يمكنك استبدال 'المخربين' بـ: المشرفين، أو المسجلين)</i>"
    )
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("أضف"))
def handle_add_player(message):
    match = re.search(r"أضف\s+@?([\w_]+)\s+إلى\s+قائمة\s+([\u0600-\u06FF]+)", message.text.strip())
    if match:
        username = match.group(1).lower()
        list_ar = match.group(2)
        list_type = get_list_en(list_ar)
        
        if list_type:
            execute_query("INSERT OR REPLACE INTO players (username, list_type) VALUES (?, ?)", (username, list_type))
            bot.reply_to(message, f"✅ تم إضافة اللاعب @{username} إلى قائمة {list_type} بنجاح.")
        else:
            bot.reply_to(message, "❌ القائمة غير معروفة. (القوائم المتاحة: المخربين، المشرفين، المسجلين)")
    else:
        bot.reply_to(message, "❌ الصيغة غير صحيحة. مثال:\nأضف @PlayerName إلى قائمة المسجلين")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("احذف"))
def handle_remove_player(message):
    match = re.search(r"احذف\s+@?([\w_]+)\s+من\s+قائمة\s+([\u0600-\u06FF]+)", message.text.strip())
    if match:
        username = match.group(1).lower()
        list_ar = match.group(2)
        list_type = get_list_en(list_ar)
        
        if list_type:
            row = execute_query("SELECT list_type FROM players WHERE username = ?", (username,), fetch=True)
            if row and row[0] == list_type:
                execute_query("DELETE FROM players WHERE username = ?", (username,))
                bot.reply_to(message, f"✅ تم حذف اللاعب @{username} من قائمة {list_type} بنجاح.")
            else:
                bot.reply_to(message, f"ℹ️ اللاعب @{username} غير موجود في قائمة {list_type} بالأصل.")
        else:
            bot.reply_to(message, "❌ القائمة غير معروفة.")
    else:
        bot.reply_to(message, "❌ الصيغة غير صحيحة. مثال:\nاحذف @PlayerName من قائمة المسجلين")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("عرض قائمة"))
def handle_show_list(message):
    list_ar = message.text.replace("عرض قائمة", "").strip()
    list_type = get_list_en(list_ar)
    
    if list_type:
        rows = execute_query("SELECT username FROM players WHERE list_type = ?", (list_type,), fetchall=True)
        if rows:
            response = f"📋 <b>قائمة {list_type}:</b>\n\n"
            for i, row in enumerate(rows, 1):
                response += f"{i}. @{row[0]}\n"
            bot.reply_to(message, response, parse_mode="HTML")
        else:
            bot.reply_to(message, f"📭 قائمة {list_type} فارغة حالياً.")
    else:
        bot.reply_to(message, "❌ القائمة غير معروفة. الرجاء كتابة:\nعرض قائمة المسجلين")

# ================== إعدادات الخادم والتشغيل ==================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write("Bot is alive and running!".encode('utf-8'))

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_health_server, daemon=True)
    server_thread.start()
    bot.infinity_polling()
