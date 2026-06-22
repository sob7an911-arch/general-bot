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
# ⚠️ تم إخفاء البيانات الحساسة هنا للأمان. ضع بياناتك الأصلية قبل التشغيل.
CREDENTIALS_DICT = {
  "type": "service_account",
  "project_id": "rare-mechanic-466808-s2",
  "private_key_id": "YOUR_PRIVATE_KEY_ID",
  "private_key": "YOUR_PRIVATE_KEY", 
  "client_email": "general-bot-service@rare-mechanic-466808-s2.iam.gserviceaccount.com",
  "token_uri": "https://oauth2.googleapis.com/token"
}

# 🌟 السطر السحري لحل مشكلة توثيق مفتاح جوجل (PEM file) على سيرفر Render 🌟
if "private_key" in CREDENTIALS_DICT and CREDENTIALS_DICT["private_key"]:
    CREDENTIALS_DICT["private_key"] = CREDENTIALS_DICT["private_key"].replace('\\n', '\n')

# --- تهيئة البوت وقاعدة البيانات ---
gc = gspread.service_account_from_dict(CREDENTIALS_DICT)
sh = gc.open("General_Bot_Data")
bot = telebot.TeleBot("YOUR_BOT_TOKEN") # 8606943008:AAGOjRgICsl1nGNCy3FhIGN37v1CcgH01pw

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

SERVER_RULES = """⚖️ **قوانين سيرفر نخبة العرب الرسمي**

🛡️ **1. الحماية المطلقة**
يُمنع منعاً باتاً مهاجمة أو احتلال أي دولة مدرجة ضمن قائمة الحماية قبل انتهاء مدة الحماية الرسمية.
⏰ تنتهي الحماية يوم السبت بعد اسبوع عند الساعة السادسة مساء بتوقيت مكة المكرمة.

🏆 **2. شرف المنافسة**
🚫 أ: يُمنع استخدام الذهب بأي شكل من الأشكال.
🚫 ب: يُمنع استخدام جميع الوحدات العسكرية القابلة للشراء أو المعروضة للبيع.
🚫 ج: يُمنع استخدام الحسابات المتعددة تحت أي ظرف.

🛡️ **3. حق الدفاع**
في حال تعرضك لهجوم من دولة في قائمة الحماية:
📸 قم بتصوير الهجوم والإشعارات كاملة.
⚖️ ارفع الأدلة إلى المحكمة المختصة.
🛡️ يحق لك الدفاع عن نفسك وطرد المعتدي من أراضيك فقط.

🤝 **4. التحالفات الرسمية**
يُمنع التحالف مع أي دولة خارج قائمة الحماية الرسمية.

👥 **5. الالتزام الجماعي**
🔒 يمنع الخروج من التحالف بشكل فردي.

⚠️ **6. الحذر واجب**
يُمنع احتلال أي دولة قبل الإعلان الرسمي عن قائمة الحماية.

⚖️ **7. الالتزام والانضباط**
أي لاعب يرفض تنفيذ أحكام المحكمة يتم حظر معرفه ويمنع من السيرفرات المستقبلية.

🏅 **9. الجوائز والمكافآت**
المركز الأول | 100 ذهب
المركز الثاني | 90 ذهب
المركز الثالث | 80 ذهب
"""

# ==========================================
# --- الدوال المساعدة ---
# ==========================================
def clean_text(text):
    """تنظيف النصوص لمنع تعطل التليجرام بسبب الماركداون"""
    if not text: return ""
    return str(text).replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")

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
    # الحفظ في جوجل شيت لتجنب مسح الملف عند عمل ريستارت للسيرفر (Render)
    try:
        ws = sh.worksheet("المشرفين")
        return ws.cell(1, 3).value == "True"
    except: return False

def set_protection_status(status):
    try:
        ws = sh.worksheet("المشرفين")
        ws.update_cell(1, 3, "True" if status else "False")
    except Exception as e:
        print(f"Error saving protection status: {e}")

def get_current_server_number():
    try:
        ws = sh.worksheet("المشرفين")
        val = ws.cell(1, 2).value  
        if val and val.strip().isdigit():
            return int(val.strip())
        else:
            ws.update_cell(1, 2, "112")
            return 112
    except:
        return 112

def increment_server_number():
    try:
        ws = sh.worksheet("المشرفين")
        val = ws.cell(1, 2).value
        num = int(val.strip()) if (val and val.strip().isdigit()) else 111
        new_num = num + 1
        ws.update_cell(1, 2, str(new_num))
        return new_num
    except:
        return 112

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

def get_protection_list_text():
    try:
        ws_prot = sh.worksheet("الحماية")
        prot_rows = ws_prot.get_all_values()
        
        categorized_protection = {
            "آسيا": [], "أوروبا": [], "أفريقيا": [], "الأمريكتين": [], "أوقيانوسيا": [], "دول أخرى": []
        }
        
        for r in prot_rows[1:]:
            if len(r) >= 2 and r[0].strip():
                user = clean_text(r[0].strip())
                country = clean_text(r[1].strip())
                continent = get_continent(country)
                categorized_protection[continent].append(f"👤 {user} ➔ 🏳️ {country}")
        
        status_str = "🔓 (مفتوحة حالياً)" if is_protection_open() else "🔒 (مغلقة)"
        prot_text = f"🛡️ **قائمة الحماية النهائية {status_str}:**\n\n"
        
        has_protection_data = False
        for continent, lines in categorized_protection.items():
            if lines:
                has_protection_data = True
                prot_text += f"🌍 **دول {continent}:**\n" + "\n".join(lines) + "\n\n"
                
        if not has_protection_data:
            prot_text += "📋 لا توجد طلبات حماية مسجلة حالياً.\n"
            
        return prot_text
    except Exception as e:
        return "❌ حدث خطأ في جلب قائمة الحماية."

def update_protection_and_champions_link():
    try:
        prot_text = get_protection_list_text()

        ws_champ = sh.worksheet("الأبطال")
        champ_rows = ws_champ.get_all_values()[1:]
        scores = [(clean_text(r[0].strip()), int(r[1])) for r in champ_rows if len(r) >= 2 and r[1].strip().isdigit()]
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
# 0. أوامر المشرفين وإدارة النظام
# ==========================================
@bot.message_handler(func=lambda m: m.text and m.text.strip() == "الأوامر")
def show_admin_commands(message):
    if not is_moderator(message.from_user.username): return
    cmds = """🛠️ **قائمة أوامر المشرفين للإدارة:**

🔹 `كود السيرفر [الكود]`: لإرسال الكود لجميع المسجلين وفتح التسجيل في الحماية تلقائياً.
🔹 `اضافة نتائج [الاسم1] [الاسم2]...`: لإضافة نقاط الفوز للمراكز العشرة بالترتيب.
🔹 `افتح الحماية`: لفتح تسجيل الحماية يدوياً.
🔹 `اغلق الحماية`: لإغلاق تسجيل الحماية يدوياً.
🔹 `إضافة [الاسم] إلى قائمة [المسجلين/المخربين/المشرفين]`
🔹 `حذف [الاسم] من قائمة [المسجلين/الحماية/المخربين/المشرفين/الأبطال]`
🔹 `عرض [المخربين/المشرفين]`: لعرض القوائم الخاصة."""
    bot.reply_to(message, cmds, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and m.text.strip() in ['افتح الحماية', 'افتح الحمايه'])
def open_protection_cmd(message):
    if not is_moderator(message.from_user.username): return
    set_protection_status(True)
    update_protection_and_champions_link()
    bot.reply_to(message, "🔓 **تم فتح قائمة الحماية والتسجيل بنجاح.**\nيمكن للأعضاء الآن تسجيل دولهم.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and m.text.strip() in ['اغلق الحماية', 'أغلق الحماية', 'اغلق الحمايه', 'أغلق الحمايه'])
def close_protection_cmd(message):
    if not is_moderator(message.from_user.username): return
    set_protection_status(False)
    update_protection_and_champions_link()
    bot.reply_to(message, "🔒 **تم إغلاق قائمة الحماية والتسجيل.**\nلا يمكن تسجيل دول جديدة حالياً.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and (m.text.strip().startswith("إضافة") or m.text.strip().startswith("حذف") or (m.text.strip().startswith("عرض") and m.text.strip() not in ["عرض المسجلين", "عرض الحماية", "عرض الحمايه", "عرض الأبطال", "عرض الابطال"])))
def admin_manage_lists(message):
    if not is_moderator(message.from_user.username): return

    text = message.text.strip()
    parts = text.split()
    if len(parts) < 2: return
    
    action = parts[0] 
    supported_lists = ["المسجلين", "الحماية", "المخربين", "المشرفين", "الأبطال"]
    target_list = next((l for l in supported_lists if l in text), None)

    if not target_list: return

    if target_list in ["المشرفين", "الأبطال"] and not is_main_admin(message.from_user.username):
        bot.reply_to(message, "🚫 لا تملك صلاحية تعديل أو عرض هذه القائمة. التعديل متاح للمدير العام فقط.")
        return

    try:
        ws = sh.worksheet(target_list)
        if action == "عرض":
            records = ws.col_values(1)
            if len(records) <= 1: bot.reply_to(message, f"📋 قائمة {target_list} فارغة حالياً.")
            else:
                data_text = "\n".join([f"- {clean_text(r)}" for r in records[1:] if r.strip()])
                bot.reply_to(message, f"📋 محتوى قائمة {target_list}:\n\n{data_text}", parse_mode="Markdown")
                
        elif action in ["إضافة", "حذف"]:
            target_name = text.replace(action, "").replace("من", "").replace("قائمة", "").replace("إلى", "").replace(target_list, "").strip()
            if not target_name:
                bot.reply_to(message, "⚠️ يرجى تحديد الاسم بعد الأمر.")
                return

            if action == "إضافة":
                row_data = [target_name, "0"] if target_list == "المسجلين" else [target_name]
                ws.append_row(row_data)
                bot.reply_to(message, f"✅ تمت إضافة {clean_text(target_name)} إلى قائمة {target_list}.")
                if target_list in ["الحماية", "الأبطال"]: update_protection_and_champions_link()
                
            elif action == "حذف":
                users = [u.lower().strip() for u in ws.col_values(1)]
                if target_name.lower() in users:
                    ws.delete_rows(users.index(target_name.lower()) + 1)
                    bot.reply_to(message, f"🗑️ تم حذف {clean_text(target_name)} من قائمة {target_list}.")
                    if target_list in ["الحماية", "الأبطال"]: update_protection_and_champions_link()
                else: bot.reply_to(message, f"⚠️ الاسم {clean_text(target_name)} غير موجود في القائمة.")
    except Exception as e: bot.reply_to(message, f"❌ خطأ في النظام: {e}")

# ==========================================
# 1. أوامر العرض العامة للجميع
# ==========================================
@bot.message_handler(func=lambda m: m.text and m.text.strip() in ["عرض المسجلين", "عرض الحماية", "عرض الحمايه", "عرض الأبطال", "عرض الابطال"])
def public_show_lists(message):
    cmd = message.text.strip()
    try:
        if cmd == "عرض المسجلين":
            ws = sh.worksheet("المسجلين")
            records = ws.col_values(1)[1:]
            if not records:
                bot.reply_to(message, "📋 قائمة المسجلين فارغة حالياً.")
            else:
                data_text = "\n".join([f"👤 {clean_text(r)}" for r in records if r.strip()])
                bot.reply_to(message, f"📋 **قائمة المسجلين الحالية:**\n\n{data_text}", parse_mode="Markdown")
        
        elif cmd in ["عرض الحماية", "عرض الحمايه"]:
            prot_text = get_protection_list_text()
            bot.reply_to(message, prot_text, parse_mode="Markdown")
            
        elif cmd in ["عرض الأبطال", "عرض الابطال"]:
            ws_champ = sh.worksheet("الأبطال")
            champ_rows = ws_champ.get_all_values()[1:]
            scores = [(clean_text(r[0].strip()), int(r[1])) for r in champ_rows if len(r) >= 2 and r[1].strip().isdigit()]
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
            
            champ_text = "🏅 **ترتيب أبطال نخبة العرب (الذهب التراكمي):**\n\n"
            if sorted_scores:
                champ_text += "\n".join([f"{i+1}. {u} ({p} ذهب)" for i, (u, p) in enumerate(sorted_scores)])
            else:
                champ_text += "📋 القائمة فارغة حالياً."
            bot.reply_to(message, champ_text, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في جلب البيانات: {e}")

# ==========================================
# 2. أوامر التسجيل الأساسي (مخصصة للخاص)
# ==========================================
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "أهلاً بك في مدير نخبة العرب الإلكتروني! 🌟\n\nلتسجيل حسابك في النظام ودخول السيرفرات، قم بإرسال كلمة:\n`تسجيل`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "تسجيل")
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

    if username: user_identifier = f"@{username}"
    else: user_identifier = chat_id
        
    try:
        ws = sh.worksheet("المسجلين")
        all_identifiers = [str(u).lower().strip() for u in ws.col_values(1) if u] 
        all_chat_ids = ws.col_values(2)
        
        if user_identifier.lower() in all_identifiers or chat_id in all_chat_ids:
            bot.reply_to(message, "⚠️ أنت مسجل بالفعل في النظام لهذا السيرفر.")
            return

        ws.append_row([user_identifier, chat_id])
        bot.reply_to(message, f"✅ تم تسجيلك تلقائياً بنجاح بالمعرف: {clean_text(user_identifier)}\nسيتم إرسال كود السيرفر لك هنا في الخاص عند بدء الفعالية.")
        time.sleep(1)
        bot.send_message(chat_id, SERVER_RULES, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء التسجيل: {e}")

# ==========================================
# 3. أوامر الحماية (تسجيل الدولة)
# ==========================================
@bot.message_handler(func=lambda m: m.text and (m.text.strip().startswith("حماية") or m.text.strip().startswith("حمايه")))
def protect_player(message):
    if not is_protection_open():
        bot.reply_to(message, "❌ قائمة الحماية مغلقة حالياً. لا يمكن تسجيل دولتك إلا بعد إرسال كود السيرفر للمسجلين.")
        return

    country = message.text.strip().replace("حماية", "").replace("حمايه", "").strip()
    if not country: 
        return bot.reply_to(message, "⚠️ يرجى كتابة اسم الدولة بعد الأمر. مثال: `حماية السعودية` أو `حمايه السعودية`")

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
            bot.reply_to(message, "❌ لا يمكنك طلب الحماية لأنك غير مسجل في قائمة (المسجلين) لهذا السيرفر.\nيرجى التسجيل أولاً (في الخاص) عندما يكون التسجيل متاحاً.")
            return

        ws_prot = sh.worksheet("الحماية")
        prot_users = [u.strip() for u in ws_prot.col_values(1)]
        
        if user_identifier in prot_users: 
            ws_prot.update_cell(prot_users.index(user_identifier) + 1, 2, country)
        else: 
            ws_prot.append_row([user_identifier, country])
            
        bot.reply_to(message, f"🛡️ تم تفعيل الحماية للمعرف [{clean_text(user_identifier)}] لدولة: {clean_text(country)}")
        update_protection_and_champions_link()
        
        try:
            prot_text = get_protection_list_text()
            bot.send_message(CHANNEL_ID, f"📌 **تحديث جديد في قائمة الحماية:**\n\n{prot_text}", parse_mode="Markdown")
        except: pass

    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء معالجة طلب الحماية: {e}")

# ==========================================
# 4. كود السيرفر وإضافة النتائج
# ==========================================
@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("كود السيرفر"))
def send_server_code(message):
    if not is_moderator(message.from_user.username): return
    try:
        text = message.text.strip()
        parts = text.split(maxsplit=2)
        code_text = parts[2] if len(parts) >= 3 and "السيرفر" in parts[1] else text.replace("كود السيرفر", "").strip()
        if not code_text or code_text == "السيرفر": code_text = text.replace("كود السيرفر", "").strip()
        if not code_text:
            bot.reply_to(message, "⚠️ يرجى كتابة الكود بعد الأمر، مثال:\n`كود السيرفر XYZ123`")
            return
        
        status_msg = bot.reply_to(message, "⏳ جاري إرسال الكود للمسجلين وفتح الحماية... (يرجى الانتظار لتجنب حظر تليجرام)")
        ws = sh.worksheet("المسجلين")
        all_rows = ws.get_all_values()
        success_count = 0
        failed_count = 0
        
        for row in all_rows[1:]:
            if len(row) >= 2 and row[1].strip().isdigit():
                try:
                    display_name = clean_text(row[0].strip())
                    msg_text = f"""🎮 **أهلاً بك يا {display_name}**

إليك كود السيرفر المعتمد:
`{clean_text(code_text)}`

🛡️ **كيف تدخل قائمة الحماية؟**
لتأمين دولتك من الهجمات، أرسل الأمر التالي هنا في الخاص أو في المجموعة:
`حماية اسم دولتك` أو `حمايه اسم الدولة` (مثال: حماية السعودية)

⏰ تنتهي الحماية يوم السبت بعد اسبوع عند الساعة السادسة مساء بتوقيت مكة المكرمة."""

                    bot.send_message(int(row[1].strip()), msg_text, parse_mode="Markdown")
                    success_count += 1
                except Exception: 
                    failed_count += 1
                time.sleep(0.3)
        
        set_protection_status(True)
        update_protection_and_champions_link()
        bot.edit_message_text(f"✅ تم إرسال الكود بنجاح إلى {success_count} لاعب.\n⚠️ تعذر الإرسال إلى {failed_count} لاعب.\n\n🔓 **تم فتح التسجيل في قائمة الحماية رسمياً!**", chat_id=message.chat.id, message_id=status_msg.message_id)
    except Exception as e: bot.reply_to(message, f"❌ خطأ: {e}")

@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("اضافة نتائج"))
def add_results(message):
    if not is_moderator(message.from_user.username): return
    try:
        parts = message.text.strip().replace("اضافة نتائج", "").strip().split()
        if not parts:
            bot.reply_to(message, "⚠️ يرجى كتابة أسماء الفائزين بالترتيب.")
            return

        points_map = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
        ws, ws_backup = sh.worksheet("الأبطال"), sh.worksheet("نسخة احتياطية")
        scores = {row[0].strip(): int(row[1]) for row in ws.get_all_values()[1:] if len(row) >= 2 and row[1].strip().isdigit()}

        server_num = get_current_server_number()
        log_text = f"🏆 **ترتيب الفائزين في سيرفر رقم {server_num}:**\n\n"
        
        for idx, name in enumerate(parts[:10]):
            pts = points_map[idx]
            scores[name] = scores.get(name, 0) + pts
            log_text += f"🥇 المركز {idx+1}: {clean_text(name)} (+{pts} ذهب)\n"

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        data_to_write = [["username", "points"]] + [[u, p] for u, p in sorted_scores]
        
        safe_update(ws, data_to_write)
        safe_update(ws_backup, data_to_write)

        top_30_text = "\n🏅 **أعلى 30 بطل في الترتيب العام:**\n" + "\n".join([f"{i+1}. {clean_text(u)} ({p} ذهب)" for i, (u, p) in enumerate(sorted_scores[:30])])
        publish_to_link(LINK_RESULTS_ID, log_text + "\n" + top_30_text)
        update_protection_and_champions_link()
        bot.reply_to(message, "✅ تم النشر بنجاح وتحديث روابط السيرفر المعتمدة.")
    except Exception as e: bot.reply_to(message, f"❌ خطأ: {e}")

# ==========================================
# 5. الترحيب وعدد المشاركات
# ==========================================
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    champ_text = ""
    try:
        ws_champ = sh.worksheet("الأبطال")
        champ_rows = ws_champ.get_all_values()[1:]
        scores = [(clean_text(r[0].strip()), int(r[1])) for r in champ_rows if len(r) >= 2 and r[1].strip().isdigit()]
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)[:10]
        champ_text = "\n🏅 **قائمة أبطال نخبة العرب (التوب 10):**\n"
        if sorted_scores: champ_text += "\n".join([f"{i+1}. {u} ({p} ذهب)" for i, (u, p) in enumerate(sorted_scores)])
        else: champ_text += "القائمة بانتظار أبطالها!"
    except: pass

    for member in message.new_chat_members:
        welcome_msg = f"""أهلاً بك يا {clean_text(member.first_name)} في مجموعة نخبة العرب! نورتنا 🌹

📢 **معلومات التسجيل في سيرفراتنا القادمة:**
يسعدنا انضمامك والمنافسة معنا!
- **طريقة التسجيل:** ادخل على الخاص الخاص بي وأرسل كلمة `تسجيل`.
- **فترة التسجيل:** يفتح التسجيل يوم الأربعاء الساعة 9:00 مساءً ويغلق الجمعة الساعة 9:00 مساءً بتوقيت مكة المكرمة.
{champ_text}"""
        bot.reply_to(message, welcome_msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "عدد")
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
# 6. المجدل التلقائي
# ==========================================
def auto_post_scheduler():
    posted_events_tracker = set()
    
    while True:
        try:
            ksa = get_ksa_time()
            weekday, hour, minute, day_str = ksa.weekday(), ksa.hour, ksa.minute, ksa.strftime("%Y-%m-%d")

            event_fri_reminder_20_50 = f"fri_remind_{day_str}"
            if weekday == 4 and hour == 20 and minute == 50 and event_fri_reminder_20_50 not in posted_events_tracker:
                posted_events_tracker.add(event_fri_reminder_20_50)
                reminder_text = "@all\n⏳ **تذكير هام جداً!**\n\nاقترب موعد انطلاق سيرفر الأبطال! 🚀\n\n" \
                                "🔹 **لغير المسجلين:** سارعوا فوراً بالدخول إلى خاص البوت وإرسال كلمة `تسجيل` قبل إغلاق باب التسجيل.\n" \
                                "🔹 **للمسجلين مسبقاً:** استعدوا وجهزوا أنفسكم، سيتم إرسال كود السيرفر لكم في الخاص قريباً جداً.\n\n" \
                                "🎯 بالتوفيق لجميع الأبطال!"
                try:
                    bot.send_message(CHANNEL_ID, reminder_text)
                    ws_reg = sh.worksheet("المسجلين")
                    for r in ws_reg.get_all_values()[1:]:
                        if len(r) >= 2 and r[1].strip().isdigit():
                            try:
                                bot.send_message(int(r[1].strip()), reminder_text.replace("@all\n", ""))
                                time.sleep(0.3)
                            except: pass
                except: pass

            event_fri_final_lists_22 = f"fri_final_{day_str}"
            if weekday == 4 and hour == 22 and minute == 0 and event_fri_final_lists_22 not in posted_events_tracker:
                posted_events_tracker.add(event_fri_final_lists_22)
                try:
                    ws_reg = sh.worksheet("المسجلين")
                    reg_records = ws_reg.col_values(1)[1:]
                    reg_text = "📋 **القائمة النهائية للمسجلين:**\n" + "\n".join([f"👤 {clean_text(r)}" for r in reg_records if r.strip()]) if reg_records else "📋 لا يوجد مسجلين."
                    
                    prot_text = get_protection_list_text()

                    final_msg = f"🔔 **إعلان القوائم النهائية לסيرفر الأبطال!** 🔔\n\n{reg_text}\n\n{'-'*20}\n\n{prot_text}"
                    
                    bot.send_message(CHANNEL_ID, final_msg, message_thread_id=1, parse_mode="Markdown")
                    time.sleep(1)
                    bot.send_message(CHANNEL_ID, final_msg, message_thread_id=1462652, parse_mode="Markdown")
                except: pass

            event_wed_thu_announcement = f"announcement_{day_str}"
            if weekday in [2, 3] and hour == 20 and minute == 0 and event_wed_thu_announcement not in posted_events_tracker:
                posted_events_tracker.add(event_wed_thu_announcement)
                server_num = increment_server_number() if weekday == 2 else get_current_server_number()
                
                announcement_text = f"🚨🔥 **ســيــرفــر الأبــطــال يــنــطــلــق قــريــبــاً رقم {server_num}** 🔥🚨\n\n" \
                                    f"يا أبطال **\"نخبة العرب\"**، باب التسجيل مفتوح حالياً لتجهيز الجيوش والمواجهات! ⚔️👑\n\n" \
                                    f"📝 **[طريقة المشاركة]:**\n" \
                                    f"1️⃣ ادخل إلى الخاص بالبوت.\n" \
                                    f"2️⃣ أرسل كلمة (**تسجيل**).\n\n" \
                                    f"💰 **[المكافآت]:** مكافآت ضخمة من **القطع الذهبية** بانتظار الفائزين بالصدارة! 🟡🏆"
                try:
                    bot.send_message(CHANNEL_ID, announcement_text, parse_mode="Markdown")
                except:
                    pass

            event_fri_hourly = f"fri_hourly_{day_str}_{hour}"
            if weekday == 4 and 13 <= hour <= 20 and minute == 0 and event_fri_hourly not in posted_events_tracker:
                posted_events_tracker.add(event_fri_hourly)
                server_num = get_current_server_number()
                hours_left = 21 - hour
                
                time_text = f"بعد {hours_left} ساعة من الآن" if hours_left > 1 else "بعد ساعة واحدة من الآن"
                announcement_text = f"🔥🚨 **سيرفر الأبطال رقم {server_num} ينطلق الليلة!** 🚨🔥\n\n" \
                                    f"يا أبطال **\"نخبة العرب\"**، جهزوا استراتيجياتكم وتحالفاتكم واستعدوا للمواجهة الكبرى! ⚔️👑\n\n" \
                                    f"⏱️ **[التوقيت]:** ينطلق السيرفر الليلة! (متبقي **{time_text}** فقط على الانطلاق الرسمي عند الساعة 9:00 مساءً).\n" \
                                    f"💰 **[المكافآت]:** المراكز الأولى ينتظرها تكريم خاص ومكافآت ضخمة من **القطع الذهبية** تصل إلى 100 قطعة للمركز الأول! 🟡🏆\n\n" \
                                    f"📝 **[طريقة المشاركة في السيرفر]:**\n" \
                                    f"لضمان تسجيلك وتواجدك مع الأبطال المعتمدين:\n" \
                                    f"1️⃣ ادخل إلى الخاص بالبوت الحالي.\n" \
                                    f"2️⃣ أرسل كلمة (**تسجيل**).\n" \
                                    f"3️⃣ سيقوم البوت بتسجيلك فوراً ويُرسل لك القوانين الرسمية، وعند انطلاق السيرفر سيوصلك الكود مباشرة في الخاص!\n\n" \
                                    f"🎯 لا تفوتوا الفرصة.. النصر حليف الأقوى والأذكى! 🚀"
                try:
                    bot.send_message(CHANNEL_ID, announcement_text, parse_mode="Markdown")
                except: pass

            event_thurs_links = f"thurs_links_{day_str}"
            if weekday == 3 and hour == 21 and minute == 0 and event_thurs_links not in posted_events_tracker:
                posted_events_tracker.add(event_thurs_links)
                update_protection_and_champions_link()

            event_wed_clear = f"wed_clear_{day_str}"
            if weekday == 2 and hour == 20 and minute == 55 and event_wed_clear not in posted_events_tracker:
                posted_events_tracker.add(event_wed_clear)
                try:
                    set_protection_status(False)
                    sh.worksheet("المسجلين").clear()
                    sh.worksheet("المسجلين").append_row(["username", "chat_id"])
                    sh.worksheet("الحماية").clear()
                    sh.worksheet("الحماية").append_row(["username", "country"])
                    update_protection_and_champions_link()
                except Exception as e: print("Error clearing sheets:", e)

            event_daily_msgs = f"msgs_{day_str}"
            if hour == 20 and minute == 0 and event_daily_msgs not in posted_events_tracker:
                posted_events_tracker.add(event_daily_msgs) 
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
