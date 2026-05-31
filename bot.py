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

    # --- تم إيقاف شرط الوقت هنا مؤقتاً لغرض التجربة ---

    ws = sh.worksheet("المسجلين")
    if user.lower() not in [u.lower() for u in ws.col_values(1)]:
        ws.append_row([user])
        bot.reply_to(message, f"✅ تم تسجيلك بنجاح يا @{user} في قائمة السيرفر. (نسخة تجريبية)")
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

@bot.message_handler(func=lambda m: m.text and m.text.startswith("أضف"))
@bot.message_handler(func=lambda m: m.text and m.text.startswith("أضف"))
def add_to_list(message):
    if not is_moderator(message.from_user.username):
        bot.reply_to(message, "❌ ليس لديك صلاحية للإضافة.")
        return
    
    try:
        # الصيغة: أضف @user إلى قائمة [اسم القائمة]
        parts = message.text.split()
        if len(parts) < 5:
            bot.reply_to(message, "⚠️ الصيغة ناقصة. اكتب: أضف @user إلى قائمة [اسم القائمة]")
            return

        target = parts[1].replace("@", "")
        list_name = parts[4] 
        
        # محاولة الوصول للورقة
        ws = sh.worksheet(list_name)
        ws.append_row([target])
        bot.reply_to(message, f"✅ تم إضافة @{target} إلى قائمة {list_name} بنجاح.")
    except Exception as e:
        # هنا سيخبرك البوت بـ "اسم الخطأ" الحقيقي
        bot.reply_to(message, f"⚠️ خطأ: {e}\nتأكد أن اسم القائمة في ملف الإكسل مطابق تماماً لما كتبته.")



@bot.message_handler(func=lambda m: m.text and m.text.startswith("كود السيرفر"))
def send_server_code(message):
    if not is_moderator(message.from_user.username): return
    
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ يرجى كتابة الكود بعد الأمر.\nمثال: كود السيرفر XYZ123")
        return
        
    code = parts[1]
    ws = sh.worksheet("المسجلين")
    users = [u for u in ws.col_values(1)[1:] if u] # تجاهل الخلايا الفارغة
    
    if not users:
        bot.reply_to(message, "❌ قائمة المسجلين فارغة.")
        return

    msg = bot.reply_to(message, f"🔄 جاري إرسال الكود إلى {len(users)} لاعب...")
    success_count = 0
    for u in users:
        try:
            bot.send_message(u, f"🎮 كود السيرفر الجديد هو: `{code}`", parse_mode="Markdown")
            success_count += 1
            time.sleep(0.1)
        except:
            continue
    bot.edit_message_text(f"✅ تم الإرسال بنجاح إلى {success_count} لاعب.", message.chat.id, msg.message_id)

import os

# دالة رقم السيرفر
def get_and_increment_server_number():
    file_name = "server_number.txt"
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            f.write("111")
        num = 111
    else:
        with open(file_name, "r") as f:
            try:
                num = int(f.read().strip())
            except:
                num = 111
    with open(file_name, "w") as f:
        f.write(str(num + 1))
    return num


@bot.message_handler(func=lambda m: m.text and m.text.startswith("اضافة نتائج"))
def add_results(message):
    if not is_moderator(message.from_user.username): return
    try:
        raw_input = message.text.replace("اضافة نتائج", "").strip()
        parts = raw_input.split()
        if not parts:
            bot.reply_to(message, "⚠️ يرجى كتابة أسماء اللاعبين.")
            return

        points_map = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
        
        # الاتصال بورقة الأبطال وورقة النسخة الاحتياطية
        ws = sh.worksheet("الأبطال")
        try:
            ws_backup = sh.worksheet("نسخة احتياطية")
        except Exception:
            bot.reply_to(message, "⚠️ يرجى إنشاء ورقة جديدة في ملف الإكسل باسم 'نسخة احتياطية' أولاً.")
            return
        
        # قراءة البيانات التراكمية القديمة
        rows = ws.get_all_values()
        scores = {}
        for row in rows[1:]:
            if len(row) >= 2:
                name_key = row[0].strip().lower()
                try:
                    scores[name_key] = int(row[1])
                except:
                    scores[name_key] = 0

        # جلب رقم السيرفر (يبدأ من 111)
        server_num = get_and_increment_server_number()

        # إضافة النقاط الجديدة وتغيير العنوان كما طلبت
        log_text = f"🏆 **ترتيب الفائزين في سيرفر رقم {server_num}:**\n"
        for idx, name in enumerate(parts[:10]):
            user = name.replace("@", "").strip().lower()
            pts = points_map[idx]
            scores[user] = scores.get(user, 0) + pts
            log_text += f"المركز {idx+1}: @{user} (+{pts} ذهب)\n"

        # تجهيز البيانات للإكسل
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        data_to_write = [["username", "points"]]
        for user, pts in sorted_scores:
            data_to_write.append([user, pts])
        
        # 1. التحديث في الورقة الأساسية دفعة واحدة
        ws.clear()
        ws.update(data_to_write) 
        
        # 2. التحديث في ورقة النسخة الاحتياطية لحفظ البيانات
        ws_backup.clear()
        ws_backup.update(data_to_write)

        # النشر في القناة (رسالة السيرفر)
        bot.send_message(CHANNEL_ID, log_text, parse_mode="Markdown")

        # النشر في القناة (رسالة التراكمي بالعنوان الجديد)
        top_30_text = f"🏅 **ترتيب أبطال نخبة العرب:**\n\n"
        for i, (user, pts) in enumerate(sorted_scores[:30]):
            top_30_text += f"{i+1}. @{user} ({pts} ذهب)\n"
        
        bot.send_message(CHANNEL_ID, top_30_text, parse_mode="Markdown")
        bot.reply_to(message, f"✅ تم النشر بنجاح! وتم حفظ نسخة احتياطية للبيانات في الإكسل.")

    except Exception as e:
        bot.reply_to(message, f"❌ خطأ تقني: {e}")





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
