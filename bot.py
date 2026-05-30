import os
import re
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import telebot

# ضع توكن البوت الخاص بك هنا مباشرة أو استخدم المتغيرات البيئية
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE" # استبدله بالتوكن الخاص بك إذا لم تكن تستخدم Environment Variables

bot = telebot.TeleBot(BOT_TOKEN)

# إعداد قاعدة البيانات للاعبين والقوائم
def init_db():
    conn = sqlite3.connect('general_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            username TEXT PRIMARY KEY,
            list_type TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# دالة مساعدة للتحقق من نوع القائمة باللغة العربية
def get_list_en(list_ar):
    if "مخرب" in list_ar:
        return "المخربين"
    elif "مشرف" in list_ar:
        return "المشرفين"
    elif "مسجل" in list_ar:
        return "المسجلين"
    return None

# أمر حذف لاعب من القوائم (للمشرفين والمالك)
# الصيغة: احذف @اسم_اللاعب من قائمة المخربين
@bot.message_handler(func=lambda message: message.text and message.text.startswith("احذف"))
def handle_remove_player(message):
    text = message.text.strip()
    
    # استخراج اسم المستخدم والقائمة باستخدام الـ Regex
    match = re.search(r"احذف\s+@?([\w_]+)\s+من\s+قائمة\s+([؀-ۿ]+)", text)
    
    if match:
        username = match.group(1).lower()
        list_ar = match.group(2)
        list_type = get_list_en(list_ar)
        
        if not list_type:
            bot.reply_to(message, "❌ لم أتعرف على القائمة المحددة. القوائم المتاحة هي: (المخربين، المشرفين، المسجلين).")
            return
            
        # هنا يمكنك إضافة تحقق من صلاحية الشخص المرسل (هل هو مشرف أو المالك)
        # لتسهيل الأمر حالياً، سننفذ الحذف مباشرة
        conn = sqlite3.connect('general_bot.db')
        cursor = conn.cursor()
        
        # التحقق إذا كان موجوداً في تلك القائمة فعلاً
        cursor.execute("SELECT list_type FROM players WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row and row[0] == list_type:
            cursor.execute("DELETE FROM players WHERE username = ?", (username,))
            conn.commit()
            bot.reply_to(message, f"✅ تم حذف اللاعب @{username} من قائمة {list_type} بنجاح.")
        else:
            bot.reply_to(message, f"ℹ️ اللاعب @{username} غير موجود في قائمة {list_type} بالأصل.")
            
        conn.close()
    else:
        bot.reply_to(message, "❌ الصيغة غير صحيحة. الصيغة الصحيحة هي:\n`احذف @اسم_اللاعب من قائمة المخربين`")

# إضافة لاعب للقوائم (مثال للتوضيح والتشغيل)
@bot.message_handler(func=lambda message: message.text and message.text.startswith("أضف"))
def handle_add_player(message):
    text = message.text.strip()
    match = re.search(r"أضف\s+@?([\w_]+)\s+إلى\s+قائمة\s+([؀-ۿ]+)", text)
    if match:
        username = match.group(1).lower()
        list_ar = match.group(2)
        list_type = get_list_en(list_ar)
        
        if list_type:
            conn = sqlite3.connect('general_bot.db')
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO players (username, list_type) VALUES (?, ?)", (username, list_type))
            conn.commit()
            conn.close()
            bot.reply_to(message, f"✅ تم إضافة @{username} إلى قائمة {list_type}.")
        else:
            bot.reply_to(message, "❌ القائمة غير معروفة.")

# أمر ترحيبي وفحص حالة البوت
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🤖 أهلاً بك في بوت إدارة مجتمع الجنرال.\n\nالأوامر المتاحة للحذف:\n• `احذف @اسم_اللاعب من قائمة المخربين`\n• `احذف @اسم_اللاعب من قائمة المشرفين`\n• `احذف @اسم_اللاعب من قائمة المسجلين`")

# --- خادم وهمي لتخطي فحص المنصات السحابية (مثل Render) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write("Bot is alive and running!".encode('utf-8'))

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"قناة الفحص تعمل على المنفذ {port}")
    server.serve_forever()

if __name__ == "__main__":
    # تشغيل خادم الفحص في خلفية منفصلة لكي لا يغلق Render البوت
    server_thread = threading.Thread(target=run_health_server, daemon=True)
    server_thread.start()
    
    print("🤖 البوت يعمل الآن وبانتظار الأوامر...")
    # تشغيل البوت للأبد
    bot.infinity_polling()
