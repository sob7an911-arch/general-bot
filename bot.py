import telebot
import gspread
import time
import threading
import os
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# --- خادم ويب وهمي لخداع Render ---
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

# --- الذاكرة المؤقتة لعداد الرسائل (لتخفيف الضغط على جوجل شيت) ---
message_counts = {}

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

# ==========================================
# 1. أوامر التسجيل وعرض القوائم (الأساسية)
# ==========================================
@bot.message_handler(func=lambda m: m.text == "تسجيل")
def register_player(message):
    user = message.from_user.username
    chat_id = message.from_user.id
    if not user:
        bot.reply_to(message, "❌ يجب أن يكون لديك اسم مستخدم (Username) للتسجيل.")
        return
    if check_user_in_list(user, "المخربين"):
        bot.reply_to(message, "❌ أنت في قائمة المخربين ولا يمكنك التسجيل.")
        return
    ws = sh.worksheet("المسجلين")
    usernames = [u.lower() for u in ws.col_values(1)]
    if user.lower() not in usernames:
        ws.append_row([user, str(chat_id)])
        bot.reply_to(message, f"✅ تم تسجيلك بنجاح يا @{user} في القائمة.")
    else:
        bot.reply_to(message, "⚠️ أنت مسجل بالفعل.")

@bot.message_handler(func=lambda m: m.text == "عرض قائمة المسجلين")
def view_registered(message):
    try:
        ws = sh.worksheet("المسجلين")
        usernames = ws.col_values(1)
        if len(usernames) <= 1:
            bot.reply_to(message, "📋 القائمة فارغة حالياً.")
            return
        text = "📋 **قائمة المسجلين:**\n\n"
        for u in usernames[1:]:
            if u.strip(): text += f"- @{u}\n"
        bot.reply_to(message, text, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

# ==========================================
# 2. أوامر السيرفر والنتائج
# ==========================================
@bot.message_handler(func=lambda m: m.text and m.text.startswith("كود السيرفر"))
def send_server_code(message):
    if not is_moderator(message.from_user.username): return
    try:
        parts = message.text.split(maxsplit=2)
        code_text = parts[2] if len(parts) >= 3 and "السيرفر" in parts[1] else message.text.replace("كود السيرفر", "").strip()
        if not code_text or code_text == "السيرفر": code_text = message.text.replace("كود السيرفر", "").strip()
        if not code_text:
            bot.reply_to(message, "⚠️ يرجى كتابة الكود بعد الأمر، مثال:\n`كود السيرفر XYZ123`")
            return
        
        status_msg = bot.reply_to(message, "⏳ جاري الإرسال في الخاص...")
        ws = sh.worksheet("المسجلين")
        all_rows = ws.get_all_values()
        success_count = 0
        
        for row in all_rows[1:]:
            if len(row) >= 2 and row[1].strip().isdigit():
                try:
                    bot.send_message(int(row[1].strip()), f"🎮 **أهلاً بك يا @{row[0].strip()}**\n\nإليك كود السيرفر:\n`{code_text}`\n\nبالتوفيق لأبطال نخبة العرب! ✨", parse_mode="Markdown")
                    success_count += 1
                    time.sleep(0.1)
                except: pass
        bot.edit_message_text(f"✅ تم الإرسال بنجاح إلى {success_count} لاعب.", chat_id=message.chat.id, message_id=status_msg.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

def get_and_increment_server_number():
    file_name = "server_number.txt"
    try:
        with open(file_name, "r") as f: num = int(f.read().strip())
    except: num = 111
    with open(file_name, "w") as f: f.write(str(num + 1))
    return num

@bot.message_handler(func=lambda m: m.text and m.text.startswith("اضافة نتائج"))
def add_results(message):
    if not is_moderator(message.from_user.username): return
    try:
        parts = message.text.replace("اضافة نتائج", "").strip().split()
        if not parts:
            bot.reply_to(message, "⚠️ يرجى كتابة أسماء اللاعبين.")
            return

        points_map = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
        ws, ws_backup = sh.worksheet("الأبطال"), sh.worksheet("نسخة احتياطية")
        scores = {row[0].strip().lower(): int(row[1]) for row in ws.get_all_values()[1:] if len(row) >= 2 and row[1].isdigit()}

        server_num = get_and_increment_server_number()
        log_text = f"🏆 **ترتيب الفائزين في سيرفر رقم {server_num}:**\n"
        
        for idx, name in enumerate(parts[:10]):
            user = name.replace("@", "").strip().lower()
            pts = points_map[idx]
            scores[user] = scores.get(user, 0) + pts
            log_text += f"المركز {idx+1}: @{user} (+{pts} ذهب)\n"

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        data_to_write = [["username", "points"]] + [[u, p] for u, p in sorted_scores]
        
        ws.clear(); ws.update(data_to_write)
        ws_backup.clear(); ws_backup.update(data_to_write)

        bot.send_message(CHANNEL_ID, log_text, parse_mode="Markdown")
        top_30_text = "🏅 **ترتيب أبطال نخبة العرب:**\n\n" + "\n".join([f"{i+1}. @{u} ({p} ذهب)" for i, (u, p) in enumerate(sorted_scores[:30])])
        bot.send_message(CHANNEL_ID, top_30_text, parse_mode="Markdown")
        bot.reply_to(message, f"✅ تم النشر بنجاح وحفظ نسخة احتياطية.")
    except Exception as e: bot.reply_to(message, f"❌ خطأ: {e}")

# ==========================================
# 3. أوامر الإدارة (الحماية، الإضافة، الحذف)
# ==========================================
@bot.message_handler(func=lambda m: m.text and m.text.startswith("حماية"))
def protect_player(message):
    user = message.from_user.username
    if not user: return
    try:
        ws_reg = sh.worksheet("المسجلين")
        if user.lower() not in [u.lower() for u in ws_reg.col_values(1)]:
            bot.reply_to(message, "❌ يجب أن تكون مسجلاً أولاً.")
            return
    except: return

    ksa = get_ksa_time()
    if ksa.weekday() == 4 and ksa.hour >= 22:
        bot.reply_to(message, "❌ انتهى وقت طلب الحماية (الجمعة 10 م).")
        return
    elif ksa.weekday() in [5, 6, 0, 1]: 
        bot.reply_to(message, "❌ طلب الحماية مغلق حالياً.")
        return

    country = message.text.replace("حماية", "").strip()
    if not country: return bot.reply_to(message, "⚠️ اكتب اسم الدولة بعد حماية.")

    try:
        ws = sh.worksheet("الحماية")
        users = [u.lower() for u in ws.col_values(1)]
        if user.lower() in users: ws.update_cell(users.index(user.lower()) + 1, 2, country)
        else: ws.append_row([user, country])
        bot.reply_to(message, f"🛡️ تم تسجيل الحماية لـ {country}")
    except: pass

@bot.message_handler(func=lambda m: m.text and m.text.startswith("أضف"))
def add_to_list(message):
    if not is_moderator(message.from_user.username): return bot.reply_to(message, "❌ لا تملك صلاحية.")
    try:
        parts = message.text.split()
        target, list_name = parts[1].replace("@", ""), parts[4]
        ws = sh.worksheet(list_name)
        ws.append_row([target, "0"] if list_name == "المسجلين" else [target])
        bot.reply_to(message, f"✅ تمت الإضافة إلى {list_name}.")
    except Exception as e: bot.reply_to(message, f"⚠️ خطأ: {e}")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("حذف من"))
def delete_from_list(message):
    sender = message.from_user.username
    try:
        parts = message.text.split()
        list_name, target = parts[2], parts[3].replace("@", "").lower()
        if list_name == "المشرفين" and not is_main_admin(sender): return bot.reply_to(message, "❌ للمدير العام فقط.")
        if not is_moderator(sender): return
        ws = sh.worksheet(list_name)
        users = [u.lower() for u in ws.col_values(1)]
        if target in users:
            ws.delete_rows(users.index(target) + 1)
            bot.reply_to(message, f"🗑️ تم الحذف من {list_name}.")
    except: pass

# ==========================================
# 4. 🚨 نظام العقوبات (الحظر والكتم التصاعدي)
# ==========================================
@bot.message_handler(func=lambda m: m.text in ["كتم", "حظر"] and m.reply_to_message)
def punish_user(message):
    if not is_moderator(message.from_user.username): return
    
    target = message.reply_to_message.from_user
    target_id, target_user = str(target.id), target.username or target.first_name
    action = message.text.strip()

    try: ws = sh.worksheet("العقوبات")
    except: return bot.reply_to(message, "⚠️ يرجى إنشاء ورقة باسم 'العقوبات' أولاً.")

    data = ws.get_all_values()
    ban_c, mute_c, row_idx = 0, 0, None

    for i, row in enumerate(data[1:], start=2):
        if str(row[0]) == target_id:
            row_idx = i
            ban_c = int(row[2]) if len(row) > 2 and row[2] else 0
            mute_c = int(row[3]) if len(row) > 3 and row[3] else 0
            break

    if action == "حظر":
        ban_c += 1
        duration_hours = ban_c * 24
        until_date = int(time.time()) + (duration_hours * 3600)
        bot.ban_chat_member(message.chat.id, target.id, until_date=until_date)
        
        if row_idx: ws.update_cell(row_idx, 3, ban_c)
        else: ws.append_row([target_id, target_user, ban_c, mute_c])
        
        bot.reply_to(message, f"⛔ تم حظر @{target_user} لمدة {duration_hours} ساعة. (الحظر رقم {ban_c})")
        try: bot.send_message(target.id, f"🚫 تم حظرك من المجموعة لمدة {duration_hours} ساعة بسبب مخالفتك.")
        except: pass

    elif action == "كتم":
        mute_c += 1
        duration_hours = mute_c
        until_date = int(time.time()) + (duration_hours * 3600)
        bot.restrict_chat_member(message.chat.id, target.id, until_date=until_date, can_send_messages=False)
        
        if row_idx: ws.update_cell(row_idx, 4, mute_c)
        else: ws.append_row([target_id, target_user, ban_c, mute_c])
        
        bot.reply_to(message, f"🔇 تم كتم @{target_user} لمدة {duration_hours} ساعة. (الكتم رقم {mute_c})")
        try: bot.send_message(target.id, f"🔇 تم كتمك في المجموعة لمدة {duration_hours} ساعة بسبب مخالفتك.")
        except: pass

# ==========================================
# 5. الترحيب ومعرفة عدد المشاركات
# ==========================================
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for member in message.new_chat_members:
        bot.reply_to(message, f"أهلاً بك يا @{member.username or member.first_name} في المجموعة! نورتنا 🌹")

@bot.message_handler(func=lambda m: m.text == "عدد")
def check_my_msgs(message):
    uid = str(message.from_user.id)
    try:
        ws = sh.worksheet("المشاركات")
        data = ws.get_all_values()
        sheet_total = next((int(r[2]) for r in data[1:] if str(r[0]) == uid and len(r) > 2), 0)
    except: sheet_total = 0
    
    mem_count = message_counts.get(uid, {}).get("daily", 0)
    bot.reply_to(message, f"📊 عدد مشاركاتك الكلية هو: {sheet_total + mem_count} مشاركة.")

# ==========================================
# 6. المجدل التلقائي (تحديث النتائج اليومية)
# ==========================================
def auto_post_scheduler():
    posted_today_events = ""
    posted_today_msgs = ""
    while True:
        try:
            ksa = get_ksa_time()
            weekday, hour, minute, day_str = ksa.weekday(), ksa.hour, ksa.minute, ksa.strftime("%Y-%m-%d")

            # مواعيد التسجيل والحماية
            if weekday == 3 and hour == 21 and minute == 0 and posted_today_events != f"thurs_{day_str}":
                ws = sh.worksheet("المسجلين")
                bot.send_message(CHANNEL_ID, "📢 قائمة المسجلين الحالية:\n" + "\n".join([f"- @{u}" for u in ws.col_values(1)[1:]]))
                posted_today_events = f"thurs_{day_str}"

            if weekday == 4 and hour == 22 and minute == 0 and posted_today_events != f"fri_{day_str}":
                ws = sh.worksheet("الحماية")
                bot.send_message(CHANNEL_ID, "🛡️ قائمة الحماية (الجمعة 10م):\n" + "\n".join([f"- @{r[0]} -> {r[1]}" for r in ws.get_all_values()[1:] if len(r) >= 2]))
                sh.worksheet("المسجلين").clear(); sh.worksheet("المسجلين").append_row(["username", "chat_id"])
                sh.worksheet("الحماية").clear(); sh.worksheet("الحماية").append_row(["username", "country"])
                posted_today_events = f"fri_{day_str}"

            # موعد نشر قائمة التفاعل اليومية (كل يوم الساعة 20:00)
            if hour == 20 and minute == 0 and posted_today_msgs != f"msgs_{day_str}":
                try: ws = sh.worksheet("المشاركات")
                except: continue
                
                data = ws.get_all_values()
                sheet_dict = {str(r[0]): {"username": r[1], "total": int(r[2]) if len(r)>2 else 0, "daily": int(r[3]) if len(r)>3 else 0} for r in data[1:]}

                # دمج الذاكرة مع الشيت
                for uid, mem in message_counts.items():
                    if uid in sheet_dict:
                        sheet_dict[uid]["daily"] += mem["daily"]
                        sheet_dict[uid]["total"] += mem["daily"]
                        sheet_dict[uid]["username"] = mem["username"]
                    else:
                        sheet_dict[uid] = {"username": mem["username"], "total": mem["daily"], "daily": mem["daily"]}

                user_list = [{"uid": k, **v} for k, v in sheet_dict.items()]
                daily_sorted = sorted(user_list, key=lambda x: x["daily"], reverse=True)[:50]
                total_sorted = sorted(user_list, key=lambda x: x["total"], reverse=True)[:50]

                if daily_sorted:
                    bot.send_message(CHANNEL_ID, "📊 **أعلى 50 عضو مشاركة اليوم:**\n\n" + "\n".join([f"{i+1}. @{u['username']} ({u['daily']} رسالة)" for i, u in enumerate(daily_sorted) if u["daily"] > 0]), parse_mode="Markdown")
                if total_sorted:
                    bot.send_message(CHANNEL_ID, "📈 **أعلى 50 عضو مشاركة (تراكمي):**\n\n" + "\n".join([f"{i+1}. @{u['username']} ({u['total']} رسالة)" for i, u in enumerate(total_sorted) if u["total"] > 0]), parse_mode="Markdown")

                # تصفير العداد اليومي وحفظه
                new_sheet_data = [["user_id", "username", "total_msgs", "daily_msgs"]] + [[d["uid"], d["username"], str(d["total"]), "0"] for d in user_list]
                ws.clear()
                ws.update(new_sheet_data)
                message_counts.clear()
                posted_today_msgs = f"msgs_{day_str}"

        except Exception as e: print(f"خطأ مجدل: {e}")
        time.sleep(30) 

threading.Thread(target=auto_post_scheduler, daemon=True).start()

# ==========================================
# 🛡️ 7. جدار الحماية، التحيات، وعداد الرسائل المخفي
# ==========================================
@bot.message_handler(func=lambda m: True)
def count_and_greet(message):
    if message.from_user.is_bot: return

    # 1. تحديث عداد المشاركات في الذاكرة
    uid, uname = str(message.from_user.id), message.from_user.username or message.from_user.first_name
    if uid not in message_counts: message_counts[uid] = {"username": uname, "daily": 0}
    message_counts[uid]["daily"] += 1

    # 2. الرد على التحيات الأساسية (ويظل يتجاهل أي إعلانات أخرى)
    text = message.text.strip() if message.text else ""
    if text in ["السلام عليكم", "سلام عليكم", "السلام عليكم ورحمة الله وبركاته"]:
        bot.reply_to(message, "وعليكم السلام ورحمة الله وبركاته 🌹")
    elif text in ["صباح الخير", "صباح النور"]:
        bot.reply_to(message, "صباح النور والسرور ✨")
    elif text in ["مساء الخير", "مساء النور"]:
        bot.reply_to(message, "مساء النور والسرور ✨")

# --- تشغيل البوت ---
bot.infinity_polling()
