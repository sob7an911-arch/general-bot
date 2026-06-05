import telebot
import gspread
import time
import threading
import os
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# --- خادم ويب وهمي لخداع Render (لتجنب توقف البوت) ---
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

# الروابط المخصصة لنشر البيانات
LINK_RESULTS_ID = 1462648
LINK_INTERACTION_ID = 1
LINK_PROTECTION_CHAMPIONS_ID = 1462652

# الذاكرة المؤقتة لعداد الرسائل
message_counts = {}

# --- تصنيف الدول والقارات ---
CONTINENTS_MAP = {
    "آسيا": ["السعودية", "اليمن", "عمان", "الامارات", "الإمارات", "قطر", "البحرين", "الكويت", "العراق", "سوريا", "لبنان", "الاردن", "الأردن", "فلسطين", "ايران", "إيران", "تركيا", "الهند", "الصين", "اليابان", "كوريا", "باكستان", "افغانستان", "أفغانستان", "منغوليا", "كازاخستان", "اندونيسيا", "إندونيسيا", "الفلبين", "ماليزيا", "تايلاند", "فيتنام", "ميانمار", "نيبال", "بنجلاديش", "تايوان"],
    "أوروبا": ["بريطانيا", "فرنسا", "المانيا", "ألمانيا", "ايطاليا", "إيطاليا", "اسبانيا", "إسبانيا", "روسيا", "اوكرانيا", "أوكرانيا", "بولندا", "السويد", "النرويج", "فنلندا", "اليونان", "رومانيا", "صربيا", "النمسا", "سويسرا", "هولندا", "بلجيكا", "البرتغال", "التشيك", "المجر", "ايرلندا", "إيرلندا", "الدنمارك", "كرواتيا", "بلغاريا", "البلقان", "القوقاز"],
    "أفريقيا": ["مصر", "السودان", "ليبيا", "تونس", "الجزائر", "المغرب", "موريتانيا", "جنوب افريقيا", "جنوب أفريقيا", "نيجيريا", "اثيوبيا", "إثيوبيا", "الصومال", "جيبوتي", "كينيا", "السنغال", "مالي", "النيجر", "تشاد", "الكاميرون", "انغولا", "أنغولا", "مدغشقر", "غانا", "الكونغو", "زيمبابوي", "اوغندا", "أوغندا"],
    "الأمريكتين": ["امريكا", "أمريكا", "الولايات المتحدة", "كندا", "المكسيك", "البرازيل", "الارجنتين", "الأرجنتين", "كولومبيا", "فنزويلا", "تشيلي", "بيرو", "كوبا", "بوليفيا", "الاكوادور", "الإكوادور", "أوروغواي", "باراغواي"],
    "أوقيانوسيا": ["استراليا", "أستراليا", "نيوزيلندا"]
}

# --- قوانين السيرفر ---
SERVER_RULES = """⚖️ **قوانين سيرفر نخبة العرب الرسمي**

🛡️ **1. الحماية المطلقة**
يُمنع منعاً باتاً مهاجمة أو احتلال أي دولة مدرجة ضمن قائمة الحماية قبل انتهاء مدة الحماية الرسمية.
⏰ تنتهي الحماية يوم السبت بعد اسبوع عند الساعة السادسة مساء بتوقيت مكة المكرمة.

🏆 **2. شرف المنافسة**
🚫 أ: يُمنع استخدام الذهب بأي شكل من الأشكال.
🚫 ب: يُمنع استخدام جميع الوحدات العسكرية القابلة للشراء أو المعروضة للبيع، بما في ذلك الوحدات الموسمية والضباط المميزين.
🚫 ج: يُمنع استخدام الحسابات المتعددة تحت أي ظرف.

🛡️ **3. حق الدفاع**
في حال تعرضك لهجوم من دولة في قائمة الحماية:
📸 قم بتصوير الهجوم والإشعارات كاملة.
⚖️ ارفع الأدلة إلى المحكمة المختصة.
🛡️ يحق لك الدفاع عن نفسك وطرد المعتدي من أراضيك فقط.
🚫 لا يحق لك شن هجوم مضاد أو احتلال أراضيه حتى صدور قرار المحكمة.

🤝 **4. التحالفات الرسمية**
يُمنع التحالف مع أي دولة خارج قائمة الحماية الرسمية.
📋 وفي الحالات الاستثنائية يجب:
- إبلاغ مدير الفعاليات.
- الحصول على موافقة مسبقة.

👥 **5. الالتزام الجماعي**
🔒 يمنع الخروج من التحالف بشكل فردي.
🔒 كما يمنع استبعاد أي عضو من التحالف دون موافقة الإدارة.

⚠️ **6. الحذر واجب**
يُمنع احتلال أي دولة قبل الإعلان الرسمي عن قائمة الحماية.

⚖️ **7. الالتزام والانضباط**
أي لاعب يرفض تنفيذ أحكام المحكمة أو يثبت قيامه بالتخريب:
🚫 يتم حظر معرف حسابه (ID).
🚫 يمنع من المشاركة في جميع السيرفرات المستقبلية.
🚫 العقوبة نهائية وتطبق بشكل تلقائي.

🔄 **8. المرونة التنظيمية**
تخضع هذه القوانين للمراجعة والتحديث عند الحاجة.
📢 ويشترط إشعار جميع اللاعبين بأي تعديل أو إضافة جديدة فور اعتمادها.

🏅 **9. الجوائز والمكافآت**
المركز | الجائزة
🥇 الأول | 100 ذهب
🥈 الثاني | 90 ذهب
🥉 الثالث | 80 ذهب
الرابع | 70 ذهب
الخامس | 60 ذهب
السادس | 50 ذهب
السابع | 40 ذهب
الثامن | 30 ذهب
التاسع | 20 ذهب
🔟 العاشر | 10 ذهب

👨‍⚖️ **10. القضاء الإداري**
تحدد المحكمة العقوبات المناسبة وفقاً لما يلي:
📌 نوع المخالفة.
📌 توقيت وقوع المخالفة.
📌 عدد مرات التكرار.
📌 حجم الضرر الناتج عنها.
ويكون قرار المحكمة ملزماً لجميع المشاركين.

━━━━━━━━━━━━━━━━━━
⚔️ الهدف من هذه القوانين هو ضمان المنافسة العادلة وتوفير بيئة احترافية لجميع المشاركين.
نتمنى للجميع منافسة قوية وممتعة."""

# ==========================================
# --- الدوال المساعدة ---
# ==========================================
def safe_update(ws, data):
    ws.clear()
    try:
        ws.update(values=data, range_name="A1")
    except TypeError:
        try:
            ws.update("A1", data)
        except Exception:
            ws.update(data)

def get_ksa_time():
    return datetime.now(timezone(timedelta(hours=3)))

def is_registration_open():
    now = get_ksa_time()
    if now.weekday() == 2 and now.hour >= 21: return True
    if now.weekday() == 3: return True
    if now.weekday() == 4 and now.hour < 21: return True
    return False

def is_main_admin(username):
    return username and username.lower().replace("@", "") == MAIN_ADMIN.lower()

def is_moderator(username):
    if is_main_admin(username): return True
    if not username: return False
    try:
        ws = sh.worksheet("المشرفين")
        mods = [u.lower().strip().replace("@", "") for u in ws.col_values(1)]
        return username.lower().replace("@", "").strip() in mods
    except: return False

def check_user_in_list(user_val, list_name, col_index=1):
    try:
        ws = sh.worksheet(list_name)
        users = [u.lower().strip().replace("@", "") for u in ws.col_values(col_index)]
        return str(user_val).lower().replace("@", "").strip() in users
    except: return False

def is_protection_open():
    try:
        with open("protection_status.txt", "r") as f:
            return f.read().strip() == "True"
    except: return False

def set_protection_status(status):
    with open("protection_status.txt", "w") as f:
        f.write("True" if status else "False")

def get_current_server_number():
    file_name = "server_number.txt"
    try:
        with open(file_name, "r") as f: return int(f.read().strip())
    except:
        with open(file_name, "w") as f: f.write("111")
        return 111

def increment_server_number():
    file_name = "server_number.txt"
    num = get_current_server_number()
    with open(file_name, "w") as f: f.write(str(num + 1))
    return num + 1

def publish_to_link(message_id, text):
    try:
        bot.edit_message_text(text, chat_id=CHANNEL_ID, message_id=message_id, parse_mode="Markdown")
    except:
        try: bot.send_message(CHANNEL_ID, f"📌 **تحديث تلقائي:**\n\n{text}", parse_mode="Markdown")
        except: pass

def get_continent(country_name):
    for continent, countries in CONTINENTS_MAP.items():
        for c in countries:
            if c in country_name or country_name in c:
                return continent
    return "دول أخرى"

def update_protection_and_champions_link():
    try:
        ws_prot = sh.worksheet("الحماية")
        prot_rows = ws_prot.get_all_values()
        
        # تصنيف دول الحماية
        categorized_protection = {
            "آسيا": [], "أوروبا": [], "أفريقيا": [], "الأمريكتين": [], "أوقيانوسيا": [], "دول أخرى": []
        }
        
        for r in prot_rows[1:]:
            if len(r) >= 2 and r[0].strip():
                user = r[0].strip()
                country = r[1].strip()
                continent = get_continent(country)
                categorized_protection[continent].append(f"👤 {user} ➔ 🏳️ {country}")
        
        status_str = "🔓 (مفتوحة حالياً)" if is_protection_open() else "🔒 (مغلقة إلكترونياً)"
        prot_text = f"🛡️ **قائمة الحماية النهائية {status_str}:**\n\n"
        
        has_protection_data = False
        for continent, lines in categorized_protection.items():
            if lines:
                has_protection_data = True
                prot_text += f"🌍 **دول {continent}:**\n" + "\n".join(lines) + "\n\n"
                
        if not has_protection_data:
            prot_text += "📋 لا توجد طلبات حماية مسجلة حالياً.\n"

        ws_champ = sh.worksheet("الأبطال")
        champ_rows = ws_champ.get_all_values()[1:]
        scores = [(r[0].strip(), int(r[1])) for r in champ_rows if len(r) >= 2 and r[1].isdigit()]
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        
        champ_text = "🏅 **ترتيب أبطال نخبة العرب (الذهب التراكمي):**\n\n"
        if sorted_scores:
            champ_text += "\n".join([f"{i+1}. {u} ({p} ذهب)" for i, (u, p) in enumerate(sorted_scores[:30])])
        else:
            champ_text += "📋 القائمة فارغة حالياً."

        combined_text = f"{prot_text}====================\n\n{champ_text}"
        publish_to_link(LINK_PROTECTION_CHAMPIONS_ID, combined_text)
    except Exception as e: print(f"خطأ أثناء تحديث الرابط المشترك: {e}")

# ==========================================
# 1. أوامر التسجيل (مخصصة للخاص وتسمح بأي صيغة)
# ==========================================
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "أهلاً بك في مدير نخبة العرب الإلكتروني! 🌟\n\nلتسجيل حسابك في النظام ودخول السيرفرات، قم بإرسال كلمة:\n`تسجيل`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "تسجيل")
def register_step_one(message):
    if message.chat.type != 'private':
        bot.reply_to(message, "❌ يرجى التسجيل عبر مراسلتي في الخاص فقط.")
        return

    if not is_registration_open():
        bot.reply_to(message, "❌ عذراً، باب التسجيل مغلق حالياً.\nيفتح التسجيل يوم الأربعاء الساعة 9 مساءً ويغلق الجمعة الساعة 9 مساءً بتوقيت مكة المكرمة.")
        return

    chat_id = str(message.from_user.id)
    username = message.from_user.username
    if check_user_in_list(chat_id, "المخربين") or (username and check_user_in_list(username, "المخربين")):
        bot.reply_to(message, "❌ أنت في قائمة المخربين ولا يمكنك التسجيل.")
        return

    msg = bot.reply_to(message, "✅ ممتاز! التسجيل مفتوح.\nيرجى الآن إرسال (اسم حسابك، أو رقم هاتفك، أو الـ ID الخاص بك) ليتم تسجيلك به في السيرفر:")
    bot.register_next_step_handler(msg, process_registration_step)

def process_registration_step(message):
    user_input = message.text.strip()
    chat_id = str(message.from_user.id)
    
    try:
        ws = sh.worksheet("المسجلين")
        all_identifiers = [u.lower().strip() for u in ws.col_values(1)]
        all_chat_ids = ws.col_values(2)
        
        if chat_id in all_chat_ids or user_input.lower() in all_identifiers:
            bot.reply_to(message, "⚠️ حسابك مسجل بالفعل في النظام لهذا السيرفر.")
        else:
            ws.append_row([user_input, chat_id])
            bot.reply_to(message, f"✅ تم تسجيلك بنجاح بالمعرف: {user_input}\nسيتم إرسال كود السيرفر لك هنا في الخاص عند بدء الفعالية.")
            time.sleep(1)
            bot.send_message(chat_id, SERVER_RULES, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء التسجيل: {e}")

# ==========================================
# 2. أوامر الحماية (الخاص فقط - للمسجلين فقط)
# ==========================================
@bot.message_handler(func=lambda m: m.text and m.text.startswith("حماية"))
def protect_player(message):
    if message.chat.type != 'private':
        bot.reply_to(message, "❌ يرجى إرسال طلب الحماية عبر مراسلتي في الخاص فقط.")
        return
    
    if not is_protection_open():
        bot.reply_to(message, "❌ قائمة الحماية مغلقة حالياً؛ لا يمكن تفعيلها إلا بعد إرسال كود السيرفر للمسجلين.")
        return

    ksa = get_ksa_time()
    if ksa.weekday() == 4 and ksa.hour >= 22:
        bot.reply_to(message, "❌ انتهى وقت طلب الحماية المحدد (الجمعة 10:00 مساءً).")
        return

    country = message.text.replace("حماية", "").strip()
    if not country: 
        return bot.reply_to(message, "⚠️ يرجى كتابة اسم الدولة بعد كلمة حماية. مثال: `حماية السعودية`")

    chat_id = str(message.from_user.id)
    try:
        ws_reg = sh.worksheet("المسجلين")
        registered_records = ws_reg.get_all_values()
        user_identifier = None
        
        for row in registered_records:
            if len(row) >= 2 and str(row[1]).strip() == chat_id:
                user_identifier = str(row[0]).strip()
                break
                
        if not user_identifier:
            bot.reply_to(message, "❌ لا يمكنك طلب الحماية لأنك غير مسجل في قائمة (المسجلين) لهذا السيرفر.\nيرجى التسجيل أولاً عندما يكون التسجيل متاحاً.")
            return

        ws_prot = sh.worksheet("الحماية")
        prot_users = [u.strip() for u in ws_prot.col_values(1)]
        
        if user_identifier in prot_users: 
            ws_prot.update_cell(prot_users.index(user_identifier) + 1, 2, country)
        else: 
            ws_prot.append_row([user_identifier, country])
            
        bot.reply_to(message, f"🛡️ تم تفعيل الحماية للمعرف [{user_identifier}] لدولة: {country}")
        update_protection_and_champions_link()
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء معالجة طلب الحماية: {e}")

# ==========================================
# 3. إدارة النظام للمشرفين (شاملة)
# ==========================================
@bot.message_handler(func=lambda m: m.text and (m.text.startswith("إضافة") or m.text.startswith("حذف") or m.text.startswith("عرض")))
def admin_manage_lists(message):
    if not is_moderator(message.from_user.username): 
        return

    text = message.text.strip()
    parts = text.split()
    if len(parts) < 2: return
    
    action = parts[0] 
    
    supported_lists = ["المسجلين", "الحماية", "المخربين", "المشرفين", "الأبطال"]
    target_list = next((l for l in supported_lists if l in text), None)

    if not target_list:
        bot.reply_to(message, f"⚠️ لم يتم التعرف على اسم القائمة بشكل صحيح. القوائم المدعومة: {' - '.join(supported_lists)}")
        return

    if target_list in ["المشرفين", "الأبطال"] and not is_main_admin(message.from_user.username):
        bot.reply_to(message, "🚫 لا تملك صلاحية تعديل أو عرض هذه القائمة. التعديل متاح للمدير العام فقط.")
        return

    try:
        ws = sh.worksheet(target_list)
        
        if action == "عرض":
            records = ws.col_values(1)
            if len(records) <= 1:
                bot.reply_to(message, f"📋 قائمة {target_list} فارغة حالياً.")
            else:
                data_text = "\n".join([f"- {r}" for r in records[1:] if r.strip()])
                bot.reply_to(message, f"📋 **محتوى قائمة {target_list}:**\n\n{data_text}", parse_mode="Markdown")
                
        elif action in ["إضافة", "حذف"]:
            target_name = text.replace(action, "").replace("من", "").replace("قائمة", "").replace("إلى", "").replace(target_list, "").strip()
            
            if not target_name:
                bot.reply_to(message, "⚠️ يرجى تحديد الاسم بعد الأمر.")
                return

            if action == "إضافة":
                row_data = [target_name, "0"] if target_list == "المسجلين" else [target_name]
                ws.append_row(row_data)
                bot.reply_to(message, f"✅ تمت إضافة {target_name} إلى قائمة {target_list}.")
                if target_list in ["الحماية", "الأبطال"]: update_protection_and_champions_link()
                
            elif action == "حذف":
                users = [u.lower().strip() for u in ws.col_values(1)]
                if target_name.lower() in users:
                    ws.delete_rows(users.index(target_name.lower()) + 1)
                    bot.reply_to(message, f"🗑️ تم حذف {target_name} من قائمة {target_list}.")
                    if target_list in ["الحماية", "الأبطال"]: update_protection_and_champions_link()
                else:
                    bot.reply_to(message, f"⚠️ الاسم {target_name} غير موجود في القائمة.")
                    
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في النظام: {e}")

# ==========================================
# 4. كود السيرفر وإضافة النتائج
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
        
        status_msg = bot.reply_to(message, "⏳ جاري إرسال الكود للمسجلين وتفعيل الحماية...")
        ws = sh.worksheet("المسجلين")
        all_rows = ws.get_all_values()
        success_count = 0
        
        for row in all_rows[1:]:
            if len(row) >= 2 and row[1].strip().isdigit():
                try:
                    display_name = row[0].strip()
                    msg_text = f"""🎮 **أهلاً بك يا {display_name}**

إليك كود السيرفر المعتمد:
`{code_text}`

🛡️ **كيف تدخل قائمة الحماية؟**
لتأمين دولتك من الهجمات، أرسل الأمر التالي هنا في الخاص:
`حماية اسم دولتك` (مثال: حماية السعودية)

⚠️ **تنبيه:** تُغلق قائمة الحماية تلقائياً يوم الجمعة الساعة 10:00 مساءً.
⏰ تنتهي الحماية يوم السبت بعد اسبوع عند الساعة السادسة مساء بتوقيت مكة المكرمة."""

                    bot.send_message(int(row[1].strip()), msg_text, parse_mode="Markdown")
                    success_count += 1
                    time.sleep(0.1)
                except: pass
        
        set_protection_status(True)
        update_protection_and_champions_link()
        bot.edit_message_text(f"✅ تم إرسال الكود بنجاح إلى {success_count} لاعب.\n🔓 تم تفعيل واستقبال طلبات قائمة الحماية بنجاح!", chat_id=message.chat.id, message_id=status_msg.message_id)
    except Exception as e: bot.reply_to(message, f"❌ خطأ: {e}")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("اضافة نتائج"))
def add_results(message):
    if not is_moderator(message.from_user.username): return
    try:
        parts = message.text.replace("اضافة نتائج", "").strip().split()
        if not parts:
            bot.reply_to(message, "⚠️ يرجى كتابة أسماء الفائزين بالترتيب.")
            return

        points_map = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
        ws, ws_backup = sh.worksheet("الأبطال"), sh.worksheet("نسخة احتياطية")
        scores = {row[0].strip(): int(row[1]) for row in ws.get_all_values()[1:] if len(row) >= 2 and row[1].isdigit()}

        server_num = get_current_server_number()
        log_text = f"🏆 **ترتيب الفائزين في سيرفر رقم {server_num}:**\n\n"
        
        for idx, name in enumerate(parts[:10]):
            pts = points_map[idx]
            scores[name] = scores.get(name, 0) + pts
            log_text += f"🥇 المركز {idx+1}: {name} (+{pts} ذهب)\n"

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        data_to_write = [["username", "points"]] + [[u, p] for u, p in sorted_scores]
        
        safe_update(ws, data_to_write)
        safe_update(ws_backup, data_to_write)

        top_30_text = "\n🏅 **أعلى 30 بطل في الترتيب العام:**\n" + "\n".join([f"{i+1}. {u} ({p} ذهب)" for i, (u, p) in enumerate(sorted_scores[:30])])
        publish_to_link(LINK_RESULTS_ID, log_text + "\n" + top_30_text)
        update_protection_and_champions_link()
        bot.reply_to(message, "✅ تم النشر بنجاح وتحديث روابط السيرفر المعتمدة.")
    except Exception as e: bot.reply_to(message, f"❌ خطأ: {e}")

# ==========================================
# 5. الترحيب للأعضاء الجدد وأمر عدد المشاركات
# ==========================================
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    champ_text = ""
    try:
        ws_champ = sh.worksheet("الأبطال")
        champ_rows = ws_champ.get_all_values()[1:]
        scores = [(r[0].strip(), int(r[1])) for r in champ_rows if len(r) >= 2 and r[1].isdigit()]
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)[:10]
        champ_text = "\n🏅 **قائمة أبطال نخبة العرب (التوب 10):**\n"
        if sorted_scores: champ_text += "\n".join([f"{i+1}. {u} ({p} ذهب)" for i, (u, p) in enumerate(sorted_scores)])
        else: champ_text += "القائمة بانتظار أبطالها!"
    except: pass

    for member in message.new_chat_members:
        welcome_msg = f"""أهلاً بك يا {member.first_name} في مجموعة نخبة العرب! نورتنا 🌹

📢 **معلومات التسجيل في سيرفراتنا القادمة:**
يسعدنا انضمامك والمنافسة معنا!
- **طريقة التسجيل:** ادخل على الخاص الخاص بي وأرسل كلمة `تسجيل`.
- **فترة التسجيل:** يفتح التسجيل يوم الأربعاء الساعة 9:00 مساءً ويغلق الجمعة الساعة 9:00 مساءً بتوقيت مكة المكرمة.
{champ_text}"""
        bot.reply_to(message, welcome_msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "عدد")
def check_my_msgs(message):
    uid = str(message.from_user.id)
    sheet_total = 0
    try:
        ws = sh.worksheet("المشاركات")
        data = ws.get_all_values()
        for r in data[1:]:
            if len(r) > 2 and str(r[0]).strip() == uid:
                try: sheet_total = int(r[2])
                except: pass
                break
    except: pass
    mem_count = message_counts.get(uid, {}).get("daily", 0)
    bot.reply_to(message, f"📊 عدد مشاركاتك الكلية هو: {sheet_total + mem_count} مشاركة.")

# ==========================================
# 6. المجدل التلقائي وعداد الرسائل
# ==========================================
def auto_post_scheduler():
    posted_today_events = ""
    posted_today_msgs = ""
    posted_today_announcement = ""
    
    while True:
        try:
            ksa = get_ksa_time()
            weekday, hour, minute, day_str = ksa.weekday(), ksa.hour, ksa.minute, ksa.strftime("%Y-%m-%d")

            if weekday in [2, 3, 4] and hour == 20 and minute == 0 and posted_today_announcement != day_str:
                posted_today_announcement = day_str
                server_num = increment_server_number() if weekday == 2 else get_current_server_number()
                bot.send_message(CHANNEL_ID, f"🚨🔥 ســيــرفــر الأبــطــال يــنــطــلــق اللــيــلــة رقم {server_num} 🔥🚨\n(الإعلان التلقائي...)")

            if weekday == 3 and hour == 21 and minute == 0 and posted_today_events != f"thurs_{day_str}":
                posted_today_events = f"thurs_{day_str}"
                update_protection_and_champions_link()

            if weekday == 4 and hour == 22 and minute == 0 and posted_today_events != f"fri_{day_str}":
                posted_today_events = f"fri_{day_str}"
                set_protection_status(False)
                update_protection_and_champions_link()
                sh.worksheet("المسجلين").clear(); sh.worksheet("المسجلين").append_row(["username", "chat_id"])
                sh.worksheet("الحماية").clear(); sh.worksheet("الحماية").append_row(["username", "country"])

            if hour == 20 and minute == 0 and posted_today_msgs != f"msgs_{day_str}":
                posted_today_msgs = f"msgs_{day_str}" 
                try:
                    ws = sh.worksheet("المشاركات")
                    data = ws.get_all_values()
                    sheet_dict = {}
                    for r in data[1:]:
                        if len(r) > 2:
                            try: sheet_dict[str(r[0])] = {"username": r[1], "total": int(r[2]), "daily": int(r[3]) if len(r)>3 else 0}
                            except: continue

                    for uid, mem in message_counts.items():
                        if uid in sheet_dict:
                            sheet_dict[uid]["total"] += mem["daily"]
                            sheet_dict[uid]["daily"] = mem["daily"]
                            sheet_dict[uid]["username"] = mem["username"]
                        else:
                            sheet_dict[uid] = {"username": mem["username"], "total": mem["daily"], "daily": mem["daily"]}

                    user_list = [{"uid": k, **v} for k, v in sheet_dict.items()]
                    new_sheet_data = [["user_id", "username", "total_msgs", "daily_msgs"]] + [[d["uid"], d["username"], str(d["total"]), "0"] for d in user_list]
                    safe_update(ws, new_sheet_data)
                    message_counts.clear()
                except: pass
        except: pass
        time.sleep(30) 

threading.Thread(target=auto_post_scheduler, daemon=True).start()

@bot.message_handler(func=lambda m: True)
def count_and_greet(message):
    if message.from_user.is_bot: return
    uid, uname = str(message.from_user.id), message.from_user.username or message.from_user.first_name
    if uid not in message_counts: message_counts[uid] = {"username": uname, "daily": 0}
    message_counts[uid]["daily"] += 1

bot.infinity_polling()
