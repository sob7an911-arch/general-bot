import os
import sqlite3
import telebot

BOT_TOKEN = "8606943008:AAGcFvCT73iHY71OOhkw2USy8bNMki72g8s"
bot = telebot.TeleBot(BOT_TOKEN)

# نستخدم مساراً ثابتاً لقاعدة البيانات في المجلد الرئيسي
DB_PATH = '/tmp/general_bot.db'

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS players (username TEXT PRIMARY KEY, list_type TEXT)')
    return conn

@bot.message_handler(func=lambda m: m.text and m.text.startswith("أضف"))
def add_player(message):
    try:
        # استخراج الاسم من الرسالة
        parts = message.text.split()
        username = parts[1].replace("@", "").lower()
        list_type = parts[3] # "المشرفين" أو "المخربين"
        
        conn = get_db()
        conn.execute("INSERT OR REPLACE INTO players (username, list_type) VALUES (?, ?)", (username, list_type))
        conn.commit()
        bot.reply_to(message, f"✅ تم إضافة @{username} إلى قائمة {list_type} بنجاح.")
    except Exception as e:
        bot.reply_to(message, "❌ خطأ في الصيغة، تأكد من كتابة: أضف @الاسم إلى قائمة المشرفين")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("عرض قائمة"))
def show_list(message):
    list_type = message.text.replace("عرض قائمة", "").strip()
    conn = get_db()
    cursor = conn.execute("SELECT username FROM players WHERE list_type = ?", (list_type,))
    rows = cursor.fetchall()
    
    if rows:
        text = f"📋 قائمة {list_type}:\n" + "\n".join([f"- @{r[0]}" for r in rows])
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, f"📭 قائمة {list_type} فارغة.")

bot.infinity_polling()
