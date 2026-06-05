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

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

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
bot = telebot.TeleBot("8606943008:AAFx25Asp08gQVdYGc0D-qj9FVGyD_uMsjM")

MAIN_ADMIN = "ab0oturki"  
CHANNEL_ID = "@abo_turky_genaral"  

# الروابط المخصصة لنشر البيانات وتعديل الرسائل المثبتة
LINK_RESULTS_ID = 1462648
LINK_INTERACTION_ID = 1
LINK_PROTECTION_CHAMPIONS_ID = 1462652

# الذاكرة المؤقتة لعداد الرسائل
message_counts = {}

def get_ksa_time():
    return datetime.now(timezone(timedelta(hours=3)))

def is_main_admin(username):
    return username and username.lower().replace("@", "") == MAIN_ADMIN.lower()

def check_user_in_list(username_or_phone, list_name):
    try:
        ws = sh.worksheet(list_name)
        users = [u.lower().strip().replace("@", "") for u in ws.col_values(1)]
        return str(username_or_phone).lower().replace("@", "").strip() in users
    except:
        return False

def is_moderator(username):
    return is_main_admin(username) or check_user_in_list(username, "المشرفين")

# --- جلب المعرف المعتمد للمستخدم (اليوزر أو رقم الهاتف المسجل) ---
def get_user_identifier(from_user):
    if from_user.username:
        return from_user.username.lower().replace("@", "").strip()
    try:
        ws = sh.worksheet("المسجلين")
        all_rows = ws.get_all_values()
        for row in all_rows[1:]:
            if len(row) >= 2 and row[1].strip() == str(from_user.id):
                return row[0].strip().lower()
    except:
        pass
    return None

# --- إدارة حالة فتح وإغلاق قائمة الحماية ---
def is_protection_open():
    try:
        with open("protection_status.txt", "r") as f:
            return f.read().strip() == "True"
    except:
        return False

def set_protection_status(status):
    with open("protection_status.txt", "w") as f:
        f.write("True" if status else "False")

# --- دالات التحكم برقم السيرفر التراكمي ---
def get_current_server_number():
    file_name = "server_number.txt"
    try:
        with open(file_name, "r") as f:
            return int(f.read().strip())
    except:
        with open(file_name, "w") as f:
            f.write("111")
        return 111

def increment_server_number():
    file_name = "server_number.txt"
    num = get_current_server_number()
    with open(file_name, "w") as f:
        f.write(str(num + 1))
    return num + 1

# --- دالة النشر الموحد على روابط القنوات المحددة ---
def publish_to_link(message_id, text):
    try:
        bot.edit_message_text(text, chat_id=CHANNEL_ID, message_id=message_id, parse_mode="Markdown")
    except:
        try:
            bot.send_message(CHANNEL_ID, f"📌 **تحديث تلقائي للرابط ({message_id}):**\n\n{text}", parse_mode="Markdown")
        except:
            print(f"فشل النشر التلقائي للرابط {message_id}")

# --- دالة تحديث رابط الحماية والأبطال المشترك المخصص ---
def update_protection_and_champions_link():
    try:
        ws_prot = sh.worksheet("الحماية")
        prot_rows = ws_prot.get_all_values()
        protection_lines = []
        for r in prot_rows[1:]:
            if len(r) >= 2 and r[0].strip():
                name = f"@{r[0].strip()}" if not r[0].strip().isdigit() else r[0].strip()
                protection_lines.append(f"- {name} -> {r[1]}")
        
        status_str = "🔓 (مفتوحة حالياً)" if is_protection_open() else "🔒 (مغلقة إلكترونياً)"
        prot_text = f"🛡️ **قائمة الحماية النهائية {status_str}:**\n\n"
        if protection_lines:
            prot_text += "\n".join(protection_lines)
        else:
            prot_text += "📋 لا توجد طلبات حماية مسجلة حالياً."

        ws_champ = sh.worksheet("الأبطال")
        champ_rows = ws_champ.get_all_values()[1:]
        scores = []
        for r in champ_rows:
            if len(r) >= 2 and r[1].isdigit():
                scores.append((r[0].strip(), int(r[1])))
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        
        champ_text = "🏅 **ترتيب أبطال نخبة العرب (الذهب التراكمي):**\n\n"
        if sorted_scores:
            champ_text += "\n".join([f"{i+1}. " + (f"@{u}" if not u.isdigit() else u) + f" ({p} ذهب)" for i, (u, p) in enumerate(sorted_scores[:30])])
        else:
            champ_text += "📋 القائمة فارغة حالياً."

        combined_text = f"{prot_text}\n\n====================\n\n{champ_text}"
        publish_to_link(LINK_PROTECTION_CHAMPIONS_ID, combined_text)
    except Exception as e:
        print(f"خطأ أثناء تحديث الرابط المشترك: {e}")

# ==========================================
# 1. أوامر التسجيل وعرض القوائم
# ==========================================
@bot.message_handler(func=lambda m: m.text == "تسجيل")
def register_player(message):
    user = message.from_user.username
    chat_id = message.from_user.id
    
    # التحقق من الحظر في قائمة المخربين لليوزر أو الشات آيدي
    if check_user_in_list(str(chat_id), "المخربين") or (user and check_user_in_list(user, "المخربين")):
        bot.reply_to(message, "❌ أنت في قائمة المخربين ولا يمكنك التسجيل.")
        return

    if user:
        user_idf = user.lower().replace("@", "").strip()
        ws = sh.worksheet("المسجلين")
        usernames = [u.lower().strip() for u in ws.col_values(1)]
        if user_idf not in usernames:
            ws.append_row([user_idf, str(chat_id)])
            bot.reply_to(message, f"✅ تم تسجيلك بنجاح يا @{user_idf} في القائمة.")
        else:
            bot.reply_to(message, "⚠️ أنت مسجل بالفعل.")
    else:
        # إذا لم يكن لديه اسم مستخدم (حساب بدون يوزر)، نطلب رقم الهاتف عبر زر خاص
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btn = telebot.types.KeyboardButton(text="📱 مشاركة رقم الهاتف للتسجيل", request_contact=True)
        markup.add(btn)
        bot.send_message(chat_id, "⚠️ حسابك لا يحتوي على اسم مستخدم (Username).\nيرجى الضغط على الزر أدناه لمشاركة رقم هاتفك وإتمام عملية التسجيل بالسيرفر ومختلف القوائم:", reply_markup=markup)

# معالج استقبال رقم الهاتف وتخزينه كمعرف رسمي بديل لليوزر
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if not message.contact: return
    chat_id = message.from_user.id
    phone = message.contact.phone_number.strip().replace("+", "")
    
    if check_user_in_list(phone, "المخربين") or check_user_in_list(str(chat_id), "المخربين"):
        bot.reply_to(message, "❌ هذا الرقم أو الحساب موجود في قائمة المخربين ولا يمكنه التسجيل.")
        return
        
    ws = sh.worksheet("المسجلين")
    all_identifiers = [u.lower().strip() for u in ws.col_values(1)]
    chat_ids = [c.strip() for c in ws.col_values(2)]
    
    if phone in all_identifiers or str(chat_id) in chat_ids:
        bot.reply_to(message, "⚠️ أنت مسجل بالفعل مسبقاً في النظام.", reply_markup=telebot.types.ReplyKeyboardRemove())
        return
        
    ws.append_row([phone, str(chat_id)])
    bot.send_message(chat_id, f"✅ تم تسجيلك بنجاح برقم الهاتف المعتمد: {phone}\nيمكنك الآن استخدام كافة ميزات البوت كالمعتاد.", reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: m.text == "عرض قائمة المسجلين")
def view_registered(message):
    if not is_moderator(message.from_user.username):
        bot.reply_to(message, "❌ عذراً، لا يمكن عرض القوائم علناً.")
        return
    try:
        ws = sh.worksheet("المسجلين")
        usernames = ws.col_values(1)
        if len(usernames) <= 1:
            bot.reply_to(message, "📋 القائمة فارغة حالياً.")
            return
        text = "📋 **قائمة المسجلين:**\n\n"
        for u in usernames[1:]:
            if u.strip(): 
                name = f"- @{u}\n" if not u.isdigit() else f"- {u}\n"
                text += name
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
        
        status_msg = bot.reply_to(message, "⏳ جاري إرسال الكود للمسجلين باليوزر ورقم الهاتف وتفعيل الحماية...")
        ws = sh.worksheet("المسجلين")
        all_rows = ws.get_all_values()
        success_count = 0
        
        for row in all_rows[1:]:
            if len(row) >= 2 and row[1].strip().isdigit():
                try:
                    display_name = f"@{row[0].strip()}" if not row[0].strip().isdigit() else row[0].strip()
                    bot.send_message(int(row[1].strip()), f"🎮 **أهلاً بك يا {display_name}**\n\nإليك كود السيرفر المعتمد:\n`{code_text}`\n\n🛡️ يمكنك الآن تفعيل الحماية عن طريق إرسال الأمر بالصيغة التالية:\nحماية اسم دولتك", parse_mode="Markdown")
                    success_count += 1
                    time.sleep(0.1)
                except: pass
        
        set_protection_status(True)
        update_protection_and_champions_link()
        
        bot.edit_message_text(f"✅ تم إرسال الكود بنجاح إلى {success_count} لاعب.\n🔓 تم تفعيل واستقبل طلبات قائمة الحماية بنجاح!", chat_id=message.chat.id, message_id=status_msg.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("اضافة نتائج"))
def add_results(message):
    if not is_moderator(message.from_user.username): return
    try:
        parts = message.text.replace("اضافة نتائج", "").strip().split()
        if not parts:
            bot.reply_to(message, "⚠️ يرجى كتابة أسماء أو أرقام اللاعبين.")
            return

        points_map = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
        ws, ws_backup = sh.worksheet("الأبطال"), sh.worksheet("نسخة احتياطية")
        scores = {row[0].strip().lower(): int(row[1]) for row in ws.get_all_values()[1:] if len(row) >= 2 and row[1].isdigit()}

        server_num = get_current_server_number()
        log_text = f"🏆 **ترتيب الفائزين في سيرفر رقم {server_num}:**\n\n"
        
        for idx, name in enumerate(parts[:10]):
            user = name.replace("@", "").strip().lower()
            pts = points_map[idx]
            scores[user] = scores.get(user, 0) + pts
            display_name = f"@{user}" if not user.isdigit() else user
            log_text += f"🥇 المركز {idx+1}: {display_name} (+{pts} ذهب)\n"

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        data_to_write = [["username", "points"]] + [[u, p] for u, p in sorted_scores]
        
        ws.clear(); ws.update(data_to_write)
        ws_backup.clear(); ws_backup.update(data_to_write)

        top_30_text = "\n🏅 **أعلى 30 بطل في الترتيب العام:**\n" + "\n".join([f"{i+1}. " + (f"@{u}" if not u.isdigit() else u) + f" ({p} ذهب)" for i, (u, p) in enumerate(sorted_scores[:30])])
        publish_to_link(LINK_RESULTS_ID, log_text + "\n" + top_30_text)
        
        update_protection_and_champions_link()
        bot.reply_to(message, "✅ تم النشر بنجاح وتحديث روابط السيرفر المعتمدة.")
    except Exception as e: bot.reply_to(message, f"❌ خطأ: {e}")

# ==========================================
# 3. نظام الإدارة والأوامر الذكية للحذف والإضافة
# ==========================================
@bot.message_handler(func=lambda m: m.text and m.text.startswith("حماية"))
def protect_player(message):
    user_idf = get_user_identifier(message.from_user)
    if not user_idf:
        bot.reply_to(message, "❌ يجب أن تكون مسجلاً أولاً عبر إرسال أمر 'تسجيل'.")
        return
    
    if not is_protection_open():
        bot.reply_to(message, "❌ قائمة الحماية مغلقة حالياً؛ لا يمكن تفعيلها إلا بعد إرسال كود السيرفر للمسجلين.")
        return

    ksa = get_ksa_time()
    if ksa.weekday() == 4 and ksa.hour >= 22:
        bot.reply_to(message, "❌ انتهى وقت طلب الحماية المحدد (الجمعة 10:00 مساءً).")
        return

    country = message.text.replace("حماية", "").strip()
    if not country: return bot.reply_to(message, "⚠️ يرجى كتابة اسم الدولة بعد كلمة حماية. مثال: `حماية السعودية`")

    try:
        ws = sh.worksheet("الحماية")
        users = [u.lower().strip() for u in ws.col_values(1)]
        if user_idf in users: 
            ws.update_cell(users.index(user_idf) + 1, 2, country)
        else: 
            ws.append_row([user_idf, country])
            
        display_name = f"@{user_idf}" if not user_idf.isdigit() else user_idf
        bot.reply_to(message, f"🛡️ تم تسجيل وتفعيل الحماية لـ {display_name} لدولة: {country}")
        update_protection_and_champions_link()
    except: pass

@bot.message_handler(func=lambda m: m.text and m.text.startswith("أضف"))
def add_to_list(message):
    if not is_moderator(message.from_user.username): return bot.reply_to(message, "❌ لا تملك صلاحية.")
    try:
        parts = message.text.split()
        target = parts[1].replace("@", "").strip().lower()
        list_name = parts[4].strip()
        
        if list_name not in ["المسجلين", "الحماية", "المخربين"] and not is_main_admin(message.from_user.username):
            bot.reply_to(message, "❌ لا تملك صلاحية تعديل هذه القائمة، التعديل متاح للمدير العام فقط.")
            return

        ws = sh.worksheet(list_name)
        ws.append_row([target, "0"] if list_name == "المسجلين" else [target])
        bot.reply_to(message, f"✅ تمت إضافة {target} إلى قائمة {list_name}.")
        if list_name in ["الحماية", "الأبطال"]: update_protection_and_champions_link()
    except Exception as e: bot.reply_to(message, f"⚠️ خطأ: {e}")

# أمر الحذف الشامل والذكي ليدعم الحذف باليوزر أو برقم الهاتف في جميع القوائم المحددة
@bot.message_handler(func=lambda m: m.text and m.text.startswith("حذف"))
def delete_player_from_any_list(message):
    sender = message.from_user.username
    if not is_moderator(sender):
        bot.reply_to(message, "❌ لا تملك صلاحية الإشراف لتنفيذ هذا الأمر.")
        return
    
    text = message.text.strip()
    supported_lists = ["المسجلين", "الحماية", "المخربين", "المشرفين", "الأبطال", "المشاركات"]
    target_list = None
    
    for l in supported_lists:
        if l in text:
            target_list = l
            break
            
    if not target_list:
        bot.reply_to(message, "⚠️ لم يتم التعرف على اسم القائمة بشكل صحيح. مثال: `حذف اسم اللاعب @username من قائمة المسجلين` أو بالرقم `حذف اللاعب 05xxxxxxxx من قائمة المسجلين`")
        return

    if target_list not in ["المسجلين", "الحماية", "المخربين"]:
        if not is_main_admin(sender):
            bot.reply_to(message, "❌ عذراً، لا يمكن تعديل أو حذف الأسماء من هذه القائمة إلا للمدير العام فقط.")
            return

    words = text.split()
    target_user = None
    
    # محاولة استخراج اليوزر المقترن بـ @ أولاً
    for w in words:
        if w.startswith("@"):
            target_user = w.replace("@", "").strip().lower()
            break
            
    # إذا لم يوجد يوزر مقترن بـ @، نبحث عن رقم الهاتف (سلسلة أرقام)
    if not target_user:
        for w in words:
            clean_w = w.replace("@", "").strip().lower()
            if clean_w.isdigit() and len(clean_w) >= 7:
                target_user = clean_w
                break

    # تصفية النص الاحتياطية
    if not target_user:
        clean_text = text.replace("حذف", "").replace("اسم", "").replace("اللاعب", "").replace("من", "").replace("قائمة", "").replace(target_list, "").strip()
        if clean_text:
            target_user = clean_text.split()[0].replace("@", "").strip().lower()

    if not target_user:
        bot.reply_to(message, "⚠️ يرجى تحديد معرف اللاعب أو رقم هاتفه المراد حذفه في نص الأمر.")
        return

    try:
        ws = sh.worksheet(target_list)
        users = [u.lower().strip() for u in ws.col_values(1)]
        if target_user in users:
            idx = users.index(target_user) + 1
            ws.delete_rows(idx)
            display_name = f"@{target_user}" if not target_user.isdigit() else target_user
            bot.reply_to(message, f"🗑️ تم حذف {display_name} من قائمة {target_list} بنجاح.")
            if target_list in ["الحماية", "الأبطال"]:
                update_protection_and_champions_link()
        else:
            display_name = f"@{target_user}" if not target_user.isdigit() else target_user
            bot.reply_to(message, f"⚠️ المستهدف {display_name} غير موجود في قائمة {target_list}.")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء الحذف: {e}")

# ==========================================
# 4. نظام العقوبات (الحظر والكتم التصاعدي)
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
    elif action == "كتم":
        mute_c += 1
        duration_hours = mute_c
        until_date = int(time.time()) + (duration_hours * 3600)
        bot.restrict_chat_member(message.chat.id, target.id, until_date=until_date, can_send_messages=False)
        
        if row_idx: ws.update_cell(row_idx, 4, mute_c)
        else: ws.append_row([target_id, target_user, ban_c, mute_c])
        
        bot.reply_to(message, f"🔇 تم كتم @{target_user} لمدة {duration_hours} ساعة. (الكتم رقم {mute_c})")

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
# 6. المجدل التلقائي للأوامر والرسائل الدورية والروابط
# ==========================================
def auto_post_scheduler():
    posted_today_events = ""
    posted_today_msgs = ""
    posted_today_announcement = ""
    
    while True:
        try:
            ksa = get_ksa_time()
            weekday, hour, minute, day_str = ksa.weekday(), ksa.hour, ksa.minute, ksa.strftime("%Y-%m-%d")

            # --- 1. إعلان انطلاق السيرفر التلقائي (الأربعاء، الخميس، الجمعة الساعة 8:00 مساءً) ---
            if weekday in [2, 3, 4] and hour == 20 and minute == 0 and posted_today_announcement != day_str:
                if weekday == 2:
                    server_num = increment_server_number()
                else:
                    server_num = get_current_server_number()

                announcement_text = f"""🚨🔥 ســيــرفــر الأبــطــال يــنــطــلــق اللــيــلــة رقم {server_num} 🔥🚨

🏆 هل أنت مستعد لخوض التحدي؟
⚔️ هل تمتلك المهارة والقدرة على الوصول إلى القمة؟

يسر إدارة نخبة العرب الإعلان عن انطلاق سيرفر الأبطال الليلة عند:
🕘 الساعة 9:00 مساءً بتوقيت مكة المكرمة

📝 طريقة التسجيل:
1️⃣ الدخول إلى مدير نخبة العرب الإلكتروني: @NOKHBAT_ALARAB_bot
2️⃣ إرسال الأمر التالي في الخاص لمرة واحدة فقط: /start
3️⃣ بعد ذلك أرسل: تسجيل

✅ ستصلك رسالة تؤكد نجاح عملية التسجيل (باليوزر أو برقم الهاتف إذا لم يتوفر يوزر).

🔐 بعد التسجيل سيقوم مدير نخبة العرب الإلكتروني بإرسال كود السيرفر إليك برسالة خاصة عند الساعة التاسعة مساء الجمعة بتوقيت مكة المكرمة.

بعد استلام الكود أرسل لمدير نخبة العرب الإلكتروني لتفعيل الحماية:
🛡️ حماية + اسم دولتك (مثال: حماية السعودية)

⏰ تنبيه هام:
تُغلق قائمة الحماية عند الساعة 10:00 مساء الجمعة بشكل إلكتروني تليها النشر المباشر للقوائم المعتمدة.

نتمنى لجميع المشاركين التوفيق والنجاح! 🔥"""
                bot.send_message(CHANNEL_ID, announcement_text)
                posted_today_announcement = day_str

            # --- 2. تحديثات المسجلين يوم الخميس ---
            if weekday == 3 and hour == 21 and minute == 0 and posted_today_events != f"thurs_{day_str}":
                update_protection_and_champions_link()
                posted_today_events = f"thurs_{day_str}"

            # --- 3. نشر قائمة الحماية النهائية وإغلاقها تلقائياً (الجمعة 10:00 مساءً) ---
            if weekday == 4 and hour == 22 and minute == 0 and posted_today_events != f"fri_{day_str}":
                set_protection_status(False)
                update_protection_and_champions_link()
                
                sh.worksheet("المسجلين").clear(); sh.worksheet("المسجلين").append_row(["username", "chat_id"])
                sh.worksheet("الحماية").clear(); sh.worksheet("الحماية").append_row(["username", "country"])
                posted_today_events = f"fri_{day_str}"

            # --- 4. تحديث قائمة التفاعل والرسائل على الرابط المخصص 1 (كل يوم الساعة 8:00 مساءً) ---
            if hour == 20 and minute == 0 and posted_today_msgs != f"msgs_{day_str}":
                try: ws = sh.worksheet("المشاركات")
                except: continue
                
                data = ws.get_all_values()
                sheet_dict = {str(r[0]): {"username": r[1], "total": int(r[2]) if len(r)>2 else 0, "daily": int(r[3]) if len(r)>3 else 0} for r in data[1:]}

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

                interaction_text = ""
                if daily_sorted:
                    interaction_text += "📊 **أعلى 50 عضو مشاركة اليوم:**\n\n" + "\n".join([f"{i+1}. " + (f"@{u['username']}" if not str(u['username']).isdigit() else u['username']) + f" ({u['daily']} رسالة)" for i, u in enumerate(daily_sorted) if u["daily"] > 0])
                if total_sorted:
                    interaction_text += "\n\n📈 **أعلى 50 عضو مشاركة (تراكمي):**\n\n" + "\n".join([f"{i+1}. " + (f"@{u['username']}" if not str(u['username']).isdigit() else u['username']) + f" ({u['total']} رسالة)" for i, u in enumerate(total_sorted) if u["total"] > 0])

                if interaction_text:
                    publish_to_link(LINK_INTERACTION_ID, interaction_text)

                new_sheet_data = [["user_id", "username", "total_msgs", "daily_msgs"]] + [[d["uid"], d["username"], str(d["total"]), "0"] for d in user_list]
                ws.clear()
                ws.update(new_sheet_data)
                message_counts.clear()
                posted_today_msgs = f"msgs_{day_str}"

        except Exception as e: print(f"خطأ مجدل: {e}")
        time.sleep(30) 

threading.Thread(target=auto_post_scheduler, daemon=True).start()

# ==========================================
# 7. جدار الحماية، التحيات، وعداد الرسائل
# ==========================================
@bot.message_handler(func=lambda m: True)
def count_and_greet(message):
    if message.from_user.is_bot: return

    uid, uname = str(message.from_user.id), message.from_user.username or message.from_user.first_name
    if uid not in message_counts: message_counts[uid] = {"username": uname, "daily": 0}
    message_counts[uid]["daily"] += 1

    text = message.text.strip() if message.text else ""
    if text in ["السلام عليكم", "سلام عليكم", "السلام عليكم ورحمة الله وبركاته"]:
        bot.reply_to(message, "وعليكم السلام ورحمة الله وبركاته 🌹")
    elif text in ["صباح الخير", "صباح النور"]:
        bot.reply_to(message, "صباح النور والسرور ✨")
    elif text in ["مساء الخير", "مساء النور"]:
        bot.reply_to(message, "مساء النور والسرور ✨")

# --- تشغيل البوت ---
bot.infinity_polling()
