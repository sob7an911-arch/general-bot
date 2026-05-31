import telebot
import gspread
import time
import threading
import os
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# --- خادم ويب وهمي لخداع Render (مهم للباقة المجانية) ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("البوت يعمل بكفاءة!".encode('utf-8'))

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()
# ==========================================

# --- بيانات الربط مع Google Sheets ---
CREDENTIALS_DICT = {
  "type": "service_account",
  "project_id": "rare-mechanic-466808-s2",
  "private_key_id": "52b5890bec4b761f97bec22f635c7bcbcf579713",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDo0Tbc5msNoXEN\nA10lOWFNYGki9xXYXBmhma68h/AIzFENKr8Mzx5JNBPaONAlB9dsnVRMFM/eMwlr\nPy+Hf2UFgB8eXrxIRy3JNl97K+cwm2C+RQXMqUSBYGOEyfsbskhSgicnsVMykGtV\nSthJdJ1/yUwi8fk4y4DSIQAeBqe9f2ncy51TEF92LAUpNArrz+9JIK+nFJFnF+tI\nP3TZVctQUf+dxpDv74WIrjsHAsq1xKqGvlo9N8O3B8LVANgA8UlDS802cNp2VUW3\nNu/6KW7iCwO/5KtZQln4T0uKMU4CCM4L+pLJmlvckHmaJiu7Fo7ewdw5pRpkc5Hc\nYQqjFLbFAgMBAAECggEAIpAOmkAtw94D87fcX96TGqLVsN5oFJDlsDcpuOzgXloA\nrVj7eFoWJ61uxg55ngm6OjJoFYxgaJ8AhragZnfr5iNlW0OapYtFmZG0Hou/vFhQ\nxiZmjEHTvPYzh/7ZQ70VngQa7npVfNPyTzz3e34vtI0Me8Ka6krR0sAZ7Zs00z16\n1ZJBAz8iyXLSaozFcKz699CQDhkpBniGPp1qRsiDDdAIHsnCOosinEjLkxtYHVPh\nQhA/t5fSSnfDiez8cy7uJYo4LK0wSJCP4Z2Lgj74tTgl3Z+DNE+3uSAVy9gklboL\ngbxLS93tF7sA59jGJPY0mp7ofFmHxblQt3Kt6RctqQKBgQD6qDjsQr9TNc0sZJva\naALAm6pOYxharwYzqOJvYwAriZHirCJMdvebvLqty0nIeH24kDN3HoYtqxaGWwrP\nrtoFJuX3dtxASrCDFteasGeP0DwNV1DYuUHuRCFnZ6VT2qZpicOsbU0W+LoGN70G\nDm09/7IW6Xa3djrgYSD2LlErTQKBgQDtx6TWo0mHOGNtvTBu8UNhZnAWj3aYmQTu\nK8naMV5e5rKyDEQ0/i22JcVxYln4FbdxDbDQ0uL6QaT+8JpiEV2SGgh/y4eoVvHZ\nt644l+YrqPNiHHjUrOjxS8oyDD+lkBkFWVmV2NAYcAjFBclMrSigc4JigolAzaGY\niXSGNfDNWQKBgHaaVqTkSGd1E6onyN8lS/gbMBB7LzDplEOpa8tMyu3O4GqjDG+l\n8y+Ls8E8aaMj8Ej+YnvAw7ikNbpJJepzT9IUP8hCQ6FgNfkxO7+ELNyNqXyejjCe\nKCY3sp6dGkt9MDTL7PyPk2SFOHBsu1I8TVCCxp+0xGm21dEJ5HDYJawZAoGBANaC\nPBgSWPvvB+vxOCdt6h6NXmNL627A5OzEfiYkUYGF2AG+BS5VfAGN07B1TLr9RG9u\nLWxGQ9QGsoX3ox8DkYmDiNVZVLmuLiL+jOKrTk9m7KI/E1ax4rgEapV57VU8SQZF\nVAdWAG17bL3peW9961/MtPyPzKi0marVnlSRhvqJAoGBALIdA1I3/YAh9JMpzWqD\nSG8QQ6g/yEMcL1f0nzJSxOaTuX50mxYQu6x4/hK+869t4QDDFlR2OPpa25OvMJGp\nLn+j3bdxRB2sDbU0V+jXhP9OEC9ftzZ7lztmPAvWaMXwJwJNUvziCfI4uWpSoZCf\nSF0CSDFAwwRrl9bY2SDGjBHk\n-----END PRIVATE KEY-----\n",
  "client_email": "general-bot-service@rare-mechanic-466808-s2.iam.gserviceaccount.com",
  "token_uri": "https://oauth2.googleapis.com/token"
}

# --- تهيئة البوت وقاعدة البيانات ---
gc = gspread.service_account_from_dict(CREDENTIALS_DICT)
sh = gc.open("General_Bot_Data")
bot = telebot.TeleBot("8606943008:AAGcFvCT73iHY71OOhkw2USy8bNMki72g8s")

MAIN_ADMIN = "ab0oturki"  
CHANNEL_ID = "@abo_turky_genaral"  

def get_ksa_time():
    return datetime.now(timezone(timedelta(hours=3)))

def is_main_admin(username):
    return username and username.lower().replace("@", "") == MAIN_ADMIN.lower()

def check_user_in_list(username, list_name):
    try:
        ws = sh.worksheet(list_name)
        users = [u.lower() for u in ws.col_values(1)]
        return username.lower().replace("@", "") in users
    except:
        return False

def is_moderator(username):
    return is_main_admin(username) or check_user_in_list(username, "المشرفين")

@bot.message_handler(func=lambda m: m.text == "تسجيل")
def register_player(message):
    user = message.from_user.username
    if not user:
        bot.reply_to(message, "❌ يجب أن يكون لديك اسم مستخدم (Username) في التليجرام للتسجيل.")
        return
    
    if check_user_in_list(user, "المخربين"):
        bot.reply_to(message, "❌ أنت في قائمة المخربين ولا يمكنك التسجيل في السيرفر.")
        return

    ksa = get_ksa_time()
    weekday = ksa.weekday()  
    hour = ksa.hour
    minute = ksa.minute

    allowed = False
    if weekday == 2 and hour >= 21: allowed = True
    elif weekday == 3: allowed = True
    elif weekday == 4:
        if hour < 21 or (hour == 21 and minute <= 30): allowed = True

    if not allowed:
        bot.reply_to(message, "❌ التسجيل مغلق حالياً. يفتح من الأربعاء 9:00 مساءً حتى الجمعة 9:30 مساءً.")
        return

    ws = sh.worksheet("المسجلين")
    if user.lower() not in [u.lower() for u in ws.col_values(1)]:
        ws.append_row([user])
        bot.reply_to(message, f"✅ تم تسجيلك بنجاح يا @{user} في قائمة السيرفر.")
    else:
        bot.reply_to(message, "⚠️ أنت مسجل بالفعل في القائمة.")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("حماية"))
def protect_player(message):
    user = message.from_user.username
    if not user: return

    if not check_user_in_list(user, "المسجلين"):
        bot.reply_to(message, "❌ يجب أن تكون مسجلاً أولاً في قائمة التسجيل لتتمكن من طلب الحماية.")
        return

    ksa = get_ksa_time()
    weekday = ksa.weekday()
    hour = ksa.hour

    if weekday == 4 and hour >= 22:
        bot.reply_to(message, "❌ انتهى وقت طلب الحماية (يغلق الجمعة الساعة 10:00 مساءً).")
        return
    elif weekday in [5, 6, 0, 1]: 
        bot.reply_to(message, "❌ طلب الحماية مغلق حالياً.")
        return

    country = message.text.replace("حماية", "").strip()
    if not country:
        bot.reply_to(message, "⚠️ يرجى كتابة اسم الدولة بعد كلمة حماية. مثال: حماية مصر")
        return

    ws = sh.worksheet("الحماية")
    users = [u.lower() for u in ws.col_values(1)]
    if user.lower() in users:
        row_idx = users.index(user.lower()) + 1
        ws.update_cell(row_idx, 2, country)
    else:
        ws.append_row([user, country])
    
    bot.reply_to(message, f"🛡️ تم تسجيل حمايتك يا @{user} لدولة: {country}")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("مشررف"))
def add_mod(message):
    if not is_main_admin(message.from_user.username): return
    try:
        target = message.text.split()[1].replace("@", "")
        ws = sh.worksheet("المشرفين")
        ws.append_row([target])
        bot.reply_to(message, f"✅ تم إضافة @{target} إلى قائمة المشرفين بنجاح.")
    except:
        bot.reply_to(message, "⚠️ الصيغة خاطئة، اكتب: مشررف @user")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("مخرب"))
def add_griefer(message):
    if not is_moderator(message.from_user.username): return
    try:
        target = message.text.split()[1].replace("@", "")
        ws = sh.worksheet("المخربين")
        ws.append_row([target])
        bot.reply_to(message, f"🚫 تم إضافة @{target} إلى قائمة المخربين وتم منعه من التسجيل.")
    except:
        bot.reply_to(message, "⚠️ الصيغة خاطئة، اكتب: مخرب @user")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("كود السيرفر"))
def send_server_code(message):
    if not is_moderator(message.from_user.username): return
    code = message.text.replace("كود السيرفر", "").strip()
    if not code:
        bot.reply_to(message, "⚠️ يرجى كتابة الكود بعد الأمر. مثال: كود السيرفر XYZ123")
        return

    ws = sh.worksheet("المسجلين")
    users = ws.col_values(1)[1:] 
    success_count = 0
    
    bot.reply_to(message, f"🔄 جاري إرسال الكود إلى {len(users)} لاعب مسجل...")
    for u in users:
        try:
            bot.send_message(u, f"🎮 كود سيرفر الجنرال الجديد هو: `{code}`", parse_mode="Markdown")
            success_count += 1
            time.sleep(0.1) 
        except:
            continue
    bot.reply_to(message, f"📊 تم إرسال الكود بنجاح إلى {success_count} لاعب من أصل {len(users)} (الذين فعلوا البوت خاص).")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("اضافة نتائج"))
def add_results(message):
    if not is_moderator(message.from_user.username): return
    try:
        parts = message.text.replace("اضافة نتائج", "").strip().split()
        if len(parts) < 1:
            bot.reply_to(message, "⚠️ يرجى ذكر أسماء الحسابات بالترتيب من الأول للعاشر متبوعة بمسافات.")
            return

        points_map = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
        ws = sh.worksheet("الأبطال")
        
        current_data = ws.get_all_values()[1:]
        scores = {row[0].lower(): int(row[1]) for row in current_data if len(row) >= 2}

        log_text = "🏆 نتائج السيرفر الحالي وتم إضافة الذهب التراكمي:\n"
        for idx, mention in enumerate(parts[:10]):
            user = mention.replace("@", "").lower()
            pts = points_map[idx]
            scores[user] = scores.get(user, 0) + pts
            log_text += f"المركز {idx+1}: @{user} (+{pts} ذهب)\n"

        ws.clear()
        ws.append_row(["username", "points"])
        for user, pt in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            ws.append_row([user, pt])

        bot.reply_to(message, "✅ تم تحديث نقاط الأبطال تراكمياً بنجاح ونشرها!")
        bot.send_message(CHANNEL_ID, log_text)
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء معالجة النتائج: {e}")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("حذف من"))
def delete_from_list(message):
    sender = message.from_user.username
    try:
        parts = message.text.split()
        list_name = parts[2]
        target = parts[3].replace("@", "").lower()

        if list_name == "المشرفين" and not is_main_admin(sender):
            bot.reply_to(message, "❌ صلاحية حذف المشرفين حكر على المدير العام فقط.")
            return
        
        if not is_moderator(sender): return

        ws = sh.worksheet(list_name)
        users = [u.lower() for u in ws.col_values(1)]
        if target in users:
            row_idx = users.index(target) + 1
            ws.delete_rows(row_idx)
            bot.reply_to(message, f"🗑️ تم حذف @{target} من قائمة {list_name} بنجاح.")
        else:
            bot.reply_to(message, f"❓ المستخدم @{target} غير موجود في قائمة {list_name}.")
    except:
        bot.reply_to(message, "⚠️ الصيغة الصحيحة: حذف من المسجلين @user")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("عرض قائمة"))
def view_list(message):
    list_name = message.text.replace("عرض قائمة", "").strip()
    try:
        ws = sh.worksheet(list_name)
        data = ws.get_all_values()[1:]
        if not data:
            bot.reply_to(message, f"📭 قائمة {list_name} فارغة حالياً.")
            return
        
        text = f"📋 قائمة {list_name}:\n"
        for r in data:
            # هنا يتم تنظيف الاسم من أي @ موجودة مسبقاً في الإكسل لمنع التكرار
            clean_user = r[0].replace("@", "")
            if len(r) == 1: text += f"- @{clean_user}\n"
            elif len(r) == 2: text += f"- @{clean_user} ({r[1]})\n"
        bot.reply_to(message, text)
    except:
        bot.reply_to(message, "❌ اسم القائمة غير صحيح.")

def auto_post_scheduler():
    posted_today = ""
    while True:
        try:
            ksa = get_ksa_time()
            weekday = ksa.weekday()
            hour = ksa.hour
            minute = ksa.minute
            day_str = ksa.strftime("%Y-%m-%d")

            if weekday == 3 and hour == 21 and minute == 0 and posted_today != f"thurs_9_{day_str}":
                ws = sh.worksheet("المسجلين")
                users = ws.col_values(1)[1:]
                text = "📢 قائمة المسجلين الحالية (الخميس 9م):\n" + "\n".join([f"- @{u}" for u in users])
                bot.send_message(CHANNEL_ID, text)
                posted_today = f"thurs_9_{day_str}"

            if weekday == 4 and hour == 20 and minute == 0 and posted_today != f"fri_8_{day_str}":
                ws = sh.worksheet("المسجلين")
                users = ws.col_values(1)[1:]
                text = "📢 قائمة المسجلين النهائية قبل الإغلاق (الجمعة 8م):\n" + "\n".join([f"- @{u}" for u in users])
                bot.send_message(CHANNEL_ID, text)
                posted_today = f"fri_8_{day_str}"

            if weekday == 4 and hour == 22 and minute == 0 and posted_today != f"fri_10_{day_str}":
                ws = sh.worksheet("الحماية")
                data = ws.get_all_values()[1:]
                text = "🛡️ قائمة الحماية المعتمدة للسيرفر (الجمعة 10م):\n"
                for r in data:
                    if len(r) >= 2: text += f"- @{r[0]} -> دولة: {r[1]}\n"
                bot.send_message(CHANNEL_ID, text)
                
                sh.worksheet("المسجلين").clear()
                sh.worksheet("المسجلين").append_row(["username"])
                sh.worksheet("الحماية").clear()
                sh.worksheet("الحماية").append_row(["username", "country"])
                
                posted_today = f"fri_10_{day_str}"

        except Exception as e:
            print(f"خطأ في المجدل التلقائي: {e}")
        
        time.sleep(30) 

threading.Thread(target=auto_post_scheduler, daemon=True).start()
bot.infinity_polling()
