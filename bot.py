#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════
    بوت إدارة سيرفر لعبة الجنرال - نخبة العرب
    General Game Server Management Bot
    By: @ab0oTurki
═══════════════════════════════════════════════════════
"""

import sqlite3
import logging
from datetime import time
import pytz
from telegram import Update
from telegram.ext import (
    Application, MessageHandler,
    filters, ContextTypes, CommandHandler
)
from telegram.error import TelegramError

# ═══════════════════════════════════════════════
#  ⚙️  الإعدادات الأساسية  -  CONFIG
# ═══════════════════════════════════════════════

BOT_TOKEN        = "8606943008:AAGcFvCT73iHY71OOhkw2USy8bNMki72g8s"  # 🔑 توكن البوت
OWNER_USERNAME   = "ab0oTurki"                 # 👑 اسم حساب المالك (بدون @)
CHANNEL_USERNAME = "@abo_turky_genaral"        # 📢 اسم القناة
# إذا كانت القناة فيها مواضيع (Topics/Forum) ضع رقم الموضوع هنا، وإلا اجعله None
CHANNEL_THREAD_ID = None                       # مثال: 1462652  أو  None

# منطقة التوقيت
SAUDI_TZ = pytz.timezone('Asia/Riyadh')        # UTC+3

# نقاط الذهب لكل مركز
GOLD = {1:100, 2:90, 3:80, 4:70, 5:60, 6:50, 7:40, 8:30, 9:20, 10:10}


# ═══════════════════════════════════════════════
#  🗄️  قاعدة البيانات
# ═══════════════════════════════════════════════

DB = 'general_bot.db'

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS registrations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL,
            user_id     INTEGER,
            server_num  INTEGER NOT NULL,
            reg_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(username, server_num)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS protection (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL,
            user_id     INTEGER,
            country     TEXT NOT NULL,
            server_num  INTEGER NOT NULL,
            reg_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(username, server_num)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS saboteurs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            added_by    TEXT,
            added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS admins (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            added_by    TEXT,
            added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS champions (
            username        TEXT PRIMARY KEY,
            total_gold      INTEGER DEFAULT 0,
            servers_played  INTEGER DEFAULT 0,
            best_rank       INTEGER,
            last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS server_results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            server_num  INTEGER,
            rank        INTEGER,
            username    TEXT,
            gold        INTEGER,
            by_user     TEXT,
            rec_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(server_num, rank)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            val TEXT
        )''')

        c.execute("INSERT OR IGNORE INTO settings VALUES ('server_num','1')")
        conn.commit()


def gs(key):
    """get setting"""
    with sqlite3.connect(DB) as conn:
        r = conn.execute("SELECT val FROM settings WHERE key=?", (key,)).fetchone()
    return r[0] if r else None


def ss(key, val):
    """set setting"""
    with sqlite3.connect(DB) as conn:
        conn.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", (key, str(val)))


# ═══════════════════════════════════════════════
#  🕐  فحص الأوقات
# ═══════════════════════════════════════════════

def registration_open() -> bool:
    """الأربعاء 9م ← الجمعة 9:30م"""
    now = datetime_now()
    wd  = now.weekday()           # 0=Mon … 6=Sun
    h, m = now.hour, now.minute
    if wd == 2 and (h > 21 or (h == 21 and m >= 0)):   # الأربعاء >= 21:00
        return True
    if wd == 3:                                          # الخميس كاملاً
        return True
    if wd == 4 and (h < 21 or (h == 21 and m <= 30)):  # الجمعة <= 21:30
        return True
    return False


def protection_open() -> bool:
    """نفس فترة التسجيل لكن تغلق الجمعة 10م"""
    if not registration_open():
        return False
    now = datetime_now()
    if now.weekday() == 4 and now.hour >= 22:
        return False
    return True


def datetime_now():
    from datetime import datetime
    return datetime.now(SAUDI_TZ)


# ═══════════════════════════════════════════════
#  🔐  فحص الصلاحيات
# ═══════════════════════════════════════════════

def clean(u: str) -> str:
    return u.lstrip('@').lower().strip()

def is_owner(u: str) -> bool:
    return clean(u) == clean(OWNER_USERNAME)

def is_admin(u: str) -> bool:
    if is_owner(u): return True
    with sqlite3.connect(DB) as conn:
        r = conn.execute("SELECT id FROM admins WHERE username=?", (clean(u),)).fetchone()
    return r is not None

def is_saboteur(u: str) -> bool:
    with sqlite3.connect(DB) as conn:
        r = conn.execute("SELECT id FROM saboteurs WHERE username=?", (clean(u),)).fetchone()
    return r is not None

def is_registered(u: str) -> bool:
    sn = gs('server_num')
    with sqlite3.connect(DB) as conn:
        r = conn.execute(
            "SELECT id FROM registrations WHERE username=? AND server_num=?",
            (clean(u), sn)).fetchone()
    return r is not None


# ═══════════════════════════════════════════════
#  📢  نشر القوائم في القناة
# ═══════════════════════════════════════════════

async def send_to_channel(bot, text: str):
    kwargs = dict(
        chat_id    = CHANNEL_USERNAME,
        text       = text,
        parse_mode = 'HTML'
    )
    if CHANNEL_THREAD_ID:
        kwargs['message_thread_id'] = CHANNEL_THREAD_ID
    try:
        await bot.send_message(**kwargs)
    except TelegramError as e:
        logging.error(f"Channel send error: {e}")


async def publish_registration_list(bot):
    sn = gs('server_num')
    with sqlite3.connect(DB) as conn:
        rows = conn.execute(
            "SELECT username FROM registrations WHERE server_num=? ORDER BY reg_at", (sn,)
        ).fetchall()

    lines = [f"{i}. @{r[0]}" for i, r in enumerate(rows, 1)]
    body  = '\n'.join(lines) if lines else "لا يوجد مسجلون حتى الآن"

    text = (
        f"📋 <b>قائمة التسجيل — السيرفر {sn}</b>\n"
        f"👥 عدد المسجلين: {len(rows)}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{body}"
    )
    await send_to_channel(bot, text)


async def publish_protection_list(bot):
    sn = gs('server_num')
    with sqlite3.connect(DB) as conn:
        rows = conn.execute(
            "SELECT username, country FROM protection WHERE server_num=? ORDER BY reg_at", (sn,)
        ).fetchall()

    lines = [f"{i}. @{u}  🌍 {c}" for i, (u, c) in enumerate(rows, 1)]
    body  = '\n'.join(lines) if lines else "لا يوجد مسجلون حتى الآن"

    text = (
        f"🛡 <b>قائمة الحماية — السيرفر {sn}</b>\n"
        f"👥 عدد المسجلين: {len(rows)}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{body}"
    )
    await send_to_channel(bot, text)


async def publish_champions_list(bot):
    with sqlite3.connect(DB) as conn:
        rows = conn.execute(
            "SELECT username, total_gold, servers_played "
            "FROM champions ORDER BY total_gold DESC LIMIT 20"
        ).fetchall()

    medals = {1:"🥇", 2:"🥈", 3:"🥉"}
    lines  = []
    for i, (u, g, s) in enumerate(rows, 1):
        m = medals.get(i, f"<b>{i}.</b>")
        lines.append(f"{m} @{u}  💰 {g} ذهب  🎮 {s} سيرفر")

    body = '\n'.join(lines) if lines else "القائمة فارغة حتى الآن"

    text = (
        "🏆 <b>قائمة أبطال نخبة العرب</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"{body}"
    )
    await send_to_channel(bot, text)


# ═══════════════════════════════════════════════
#  📩  معالج الرسائل الرئيسي
# ═══════════════════════════════════════════════

async def handle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    msg  = update.message
    text = msg.text.strip()
    user = msg.from_user
    uname = user.username or ""

    # ─── تسجيل ───────────────────────────────
    if text == "تسجيل":
        await do_register(msg, uname, user.id)

    # ─── حماية ───────────────────────────────
    elif text.startswith("حماية"):
        country = text[5:].strip()
        await do_protection(msg, uname, user.id, country)

    # ─── مخرب ────────────────────────────────
    elif text.startswith("مخرب"):
        target = text[4:].strip()
        await do_saboteur(msg, uname, target)

    # ─── مشررف ───────────────────────────────
    elif text.startswith("مشررف"):
        target = text[5:].strip()
        await do_add_admin(msg, uname, target)

    # ─── كود السيرفر ─────────────────────────
    elif text.startswith("كود السيرفر"):
        code = text[11:].strip()
        await do_send_code(msg, ctx, uname, code)

    # ─── نتائج ───────────────────────────────
    elif text.startswith("نتائج"):
        await do_results(msg, ctx, uname, text)

    # ─── سيرفر جديد ──────────────────────────
    elif text == "سيرفر جديد":
        await do_new_server(msg, uname)

    # ─── قوائم العرض ─────────────────────────
    elif text == "قائمة التسجيل":
        await show_registration(msg)
    elif text == "قائمة الحماية":
        await show_protection(msg)
    elif text in ("قائمة الأبطال", "الأبطال", "أبطال"):
        await show_champions(msg)
    elif text == "قائمة المخربين" and is_admin(uname):
        await show_saboteurs(msg)

    # ─── مساعدة ──────────────────────────────
    elif text in ("مساعدة", "/start", "/help"):
        await do_help(msg, uname)


# ═══════════════════════════════════════════════
#  ⚡  منطق الأوامر
# ═══════════════════════════════════════════════

async def do_register(msg, uname: str, uid: int):
    if not uname:
        await msg.reply_text("❌ يجب أن يكون لحسابك اسم مستخدم (@username) لكي تتمكن من التسجيل.")
        return
    if not registration_open():
        await msg.reply_text(
            "⏰ <b>باب التسجيل مغلق حالياً</b>\n\n"
            "📅 يفتح: الأربعاء الساعة 9 مساءً\n"
            "📅 يغلق: الجمعة الساعة 9:30 مساءً",
            parse_mode='HTML'
        )
        return
    if is_saboteur(uname):
        await msg.reply_text("🚫 حسابك موجود في قائمة المخربين ولا يمكنك المشاركة.")
        return
    if is_registered(uname):
        await msg.reply_text("ℹ️ أنت مسجل مسبقاً في هذا السيرفر.")
        return

    sn = gs('server_num')
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO registrations (username, user_id, server_num) VALUES(?,?,?)",
            (clean(uname), uid, sn)
        )
        count = conn.execute(
            "SELECT COUNT(*) FROM registrations WHERE server_num=?", (sn,)
        ).fetchone()[0]

    await msg.reply_text(
        f"✅ <b>تم تسجيلك بنجاح!</b>\n\n"
        f"👤 الاسم: @{uname}\n"
        f"🎮 السيرفر: #{sn}\n"
        f"📊 رقمك في القائمة: {count}",
        parse_mode='HTML'
    )


async def do_protection(msg, uname: str, uid: int, country: str):
    if not uname:
        await msg.reply_text("❌ يجب أن يكون لحسابك اسم مستخدم (@username).")
        return
    if not country:
        await msg.reply_text(
            "⚠️ اكتب اسم دولتك بعد كلمة <b>حماية</b>\n"
            "مثال: <code>حماية المملكة العربية السعودية</code>",
            parse_mode='HTML'
        )
        return
    if not protection_open():
        await msg.reply_text(
            "⏰ <b>باب قائمة الحماية مغلق</b>\n"
            "يغلق التسجيل يوم الجمعة الساعة 10 مساءً.",
            parse_mode='HTML'
        )
        return
    if not is_registered(uname):
        await msg.reply_text(
            "❌ يجب أن تكون مسجلاً في <b>قائمة التسجيل</b> أولاً.\n"
            "أرسل: <code>تسجيل</code>",
            parse_mode='HTML'
        )
        return

    sn = gs('server_num')
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO protection (username, user_id, country, server_num) VALUES(?,?,?,?)",
            (clean(uname), uid, country, sn)
        )

    await msg.reply_text(
        f"🛡 <b>تم تسجيلك في قائمة الحماية!</b>\n\n"
        f"👤 الاسم: @{uname}\n"
        f"🌍 الدولة: {country}",
        parse_mode='HTML'
    )


async def do_saboteur(msg, uname: str, target: str):
    if not is_admin(uname):
        await msg.reply_text("🚫 ليس لديك صلاحية لهذا الأمر.")
        return
    if not target:
        await msg.reply_text(
            "⚠️ اكتب اسم الحساب بعد كلمة <b>مخرب</b>\n"
            "مثال: <code>مخرب username</code>",
            parse_mode='HTML'
        )
        return

    target = clean(target)

    if is_owner(target):
        await msg.reply_text("🚫 لا يمكن إضافة المالك لهذه القائمة.")
        return

    sn = gs('server_num')
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO saboteurs (username, added_by) VALUES(?,?)",
            (target, clean(uname))
        )
        # إزالته من السيرفر الحالي
        conn.execute("DELETE FROM registrations WHERE username=? AND server_num=?", (target, sn))
        conn.execute("DELETE FROM protection WHERE username=? AND server_num=?", (target, sn))

    await msg.reply_text(
        f"🔴 تم إضافة @{target} إلى قائمة المخربين\n"
        f"وتم إزالته من قوائم السيرفر الحالي تلقائياً."
    )


async def do_add_admin(msg, uname: str, target: str):
    if not is_owner(uname):
        await msg.reply_text("🚫 هذا الأمر للمالك @ab0oTurki فقط.")
        return
    if not target:
        await msg.reply_text(
            "⚠️ اكتب اسم الحساب بعد كلمة <b>مشررف</b>\n"
            "مثال: <code>مشررف username</code>",
            parse_mode='HTML'
        )
        return

    target = clean(target)
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO admins (username, added_by) VALUES(?,?)",
            (target, clean(uname))
        )

    await msg.reply_text(f"✅ تم منح @{target} صلاحيات المشرف.")


async def do_send_code(msg, ctx, uname: str, code: str):
    if not is_admin(uname):
        await msg.reply_text("🚫 ليس لديك صلاحية لإرسال كود السيرفر.")
        return
    if not code:
        await msg.reply_text(
            "⚠️ اكتب الكود بعد <b>كود السيرفر</b>\n"
            "مثال: <code>كود السيرفر XXXX-YYYY</code>",
            parse_mode='HTML'
        )
        return

    sn = gs('server_num')
    with sqlite3.connect(DB) as conn:
        players = conn.execute(
            "SELECT user_id, username FROM registrations WHERE server_num=? AND user_id IS NOT NULL",
            (sn,)
        ).fetchall()

    if not players:
        await msg.reply_text("⚠️ لا يوجد لاعبون مسجلون بعد.")
        return

    notice = await msg.reply_text(f"⏳ جاري الإرسال لـ {len(players)} لاعب...")
    sent = failed = 0

    for uid, un in players:
        try:
            await ctx.bot.send_message(
                chat_id = uid,
                text    = (
                    f"🎮 <b>كود السيرفر #{sn}</b>\n\n"
                    f"🔑 الكود: <code>{code}</code>\n\n"
                    f"بالتوفيق للجميع! 🏆"
                ),
                parse_mode='HTML'
            )
            sent += 1
        except TelegramError:
            failed += 1

    await notice.edit_text(
        f"✅ <b>تم الإرسال!</b>\n"
        f"📤 ناجح: {sent}\n"
        f"❌ فشل: {failed} (لم يبدأوا البوت)",
        parse_mode='HTML'
    )


async def do_results(msg, ctx, uname: str, text: str):
    """
    صيغة إدخال النتائج:
    نتائج
    1- username1
    2- username2
    ...
    10- username10
    """
    if not is_admin(uname):
        await msg.reply_text("🚫 ليس لديك صلاحية لإدخال النتائج.")
        return

    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]

    if len(lines) < 2:
        await msg.reply_text(
            "⚠️ <b>صيغة إدخال النتائج:</b>\n\n"
            "<code>نتائج\n"
            "1- اسم_المستخدم\n"
            "2- اسم_المستخدم\n"
            "...\n"
            "10- اسم_المستخدم</code>",
            parse_mode='HTML'
        )
        return

    results = []
    for line in lines[1:]:
        for sep in ('-', '.', ')'):
            if sep in line:
                parts = line.split(sep, 1)
                try:
                    rank   = int(parts[0].strip())
                    player = clean(parts[1].strip())
                    if 1 <= rank <= 10 and player:
                        results.append((rank, player))
                except ValueError:
                    pass
                break

    if not results:
        await msg.reply_text("❌ لم أتعرف على أي نتيجة. راجع الصيغة.")
        return

    sn = gs('server_num')
    confirm_lines = []

    with sqlite3.connect(DB) as conn:
        for rank, player in results:
            gold = GOLD.get(rank, 0)

            conn.execute(
                "INSERT OR REPLACE INTO server_results (server_num, rank, username, gold, by_user) VALUES(?,?,?,?,?)",
                (sn, rank, player, gold, clean(uname))
            )

            row = conn.execute(
                "SELECT total_gold, servers_played FROM champions WHERE username=?", (player,)
            ).fetchone()

            if row:
                new_gold    = row[0] + gold
                new_servers = row[1] + 1
                conn.execute(
                    "UPDATE champions SET total_gold=?, servers_played=?, best_rank=CASE WHEN best_rank IS NULL OR ? < best_rank THEN ? ELSE best_rank END, last_updated=CURRENT_TIMESTAMP WHERE username=?",
                    (new_gold, new_servers, rank, rank, player)
                )
            else:
                conn.execute(
                    "INSERT INTO champions (username, total_gold, servers_played, best_rank) VALUES(?,?,?,?)",
                    (player, gold, 1, rank)
                )

            confirm_lines.append(f"{rank}. @{player}  💰 {gold} ذهب")

    # نشر قائمة الأبطال في القناة
    await publish_champions_list(ctx.bot)

    confirm = "\n".join(confirm_lines)
    await msg.reply_text(
        f"✅ <b>تم تسجيل نتائج السيرفر #{sn}</b>\n\n{confirm}",
        parse_mode='HTML'
    )


async def do_new_server(msg, uname: str):
    if not is_owner(uname):
        await msg.reply_text("🚫 هذا الأمر للمالك فقط.")
        return

    old = int(gs('server_num'))
    new = old + 1
    ss('server_num', new)

    await msg.reply_text(
        f"🆕 <b>تم إنشاء سيرفر جديد</b>\n\n"
        f"السيرفر السابق: #{old}\n"
        f"السيرفر الحالي: <b>#{new}</b>\n\n"
        f"قوائم التسجيل والحماية جاهزة من جديد ✅",
        parse_mode='HTML'
    )


# ─── قوائم العرض ───────────────────────────────

async def show_registration(msg):
    sn = gs('server_num')
    with sqlite3.connect(DB) as conn:
        rows = conn.execute(
            "SELECT username FROM registrations WHERE server_num=? ORDER BY reg_at", (sn,)
        ).fetchall()

    if not rows:
        await msg.reply_text("📋 قائمة التسجيل فارغة حتى الآن.")
        return

    lines = "\n".join(f"{i}. @{r[0]}" for i, r in enumerate(rows, 1))
    await msg.reply_text(
        f"📋 <b>قائمة التسجيل — السيرفر #{sn}</b>\n"
        f"👥 العدد: {len(rows)}\n"
        f"━━━━━━━━━━━━━━\n{lines}",
        parse_mode='HTML'
    )


async def show_protection(msg):
    sn = gs('server_num')
    with sqlite3.connect(DB) as conn:
        rows = conn.execute(
            "SELECT username, country FROM protection WHERE server_num=? ORDER BY reg_at", (sn,)
        ).fetchall()

    if not rows:
        await msg.reply_text("🛡 قائمة الحماية فارغة حتى الآن.")
        return

    lines = "\n".join(f"{i}. @{u}  🌍 {c}" for i, (u, c) in enumerate(rows, 1))
    await msg.reply_text(
        f"🛡 <b>قائمة الحماية — السيرفر #{sn}</b>\n"
        f"👥 العدد: {len(rows)}\n"
        f"━━━━━━━━━━━━━━\n{lines}",
        parse_mode='HTML'
    )


async def show_champions(msg):
    with sqlite3.connect(DB) as conn:
        rows = conn.execute(
            "SELECT username, total_gold, servers_played FROM champions ORDER BY total_gold DESC LIMIT 20"
        ).fetchall()

    if not rows:
        await msg.reply_text("🏆 قائمة الأبطال فارغة حتى الآن.")
        return

    medals = {1:"🥇", 2:"🥈", 3:"🥉"}
    lines  = [
        f"{medals.get(i, str(i)+'.')} @{u}  💰 {g} ذهب  🎮 {s} سيرفر"
        for i, (u, g, s) in enumerate(rows, 1)
    ]
    await msg.reply_text(
        "🏆 <b>قائمة أبطال نخبة العرب</b>\n"
        "━━━━━━━━━━━━━━\n" + "\n".join(lines),
        parse_mode='HTML'
    )


async def show_saboteurs(msg):
    with sqlite3.connect(DB) as conn:
        rows = conn.execute(
            "SELECT username, added_by, added_at FROM saboteurs ORDER BY added_at"
        ).fetchall()

    if not rows:
        await msg.reply_text("✅ قائمة المخربين فارغة.")
        return

    lines = "\n".join(f"{i}. @{u} (أضافه: @{ab})" for i, (u, ab, _) in enumerate(rows, 1))
    await msg.reply_text(
        f"🔴 <b>قائمة المخربين</b>\n"
        f"العدد: {len(rows)}\n"
        f"━━━━━━━━━━━━━━\n{lines}",
        parse_mode='HTML'
    )


async def do_help(msg, uname: str):
    admin_section = ""
    if is_admin(uname):
        admin_section = (
            "\n\n🔧 <b>أوامر المشرفين:</b>\n"
            "<code>مخرب username</code>  — إضافة لقائمة المخربين\n"
            "<code>نتائج</code>  — إدخال نتائج السيرفر\n"
            "<code>كود السيرفر XXXX</code>  — إرسال الكود للمسجلين\n"
            "<code>قائمة المخربين</code>  — عرض القائمة"
        )

    owner_section = ""
    if is_owner(uname):
        owner_section = (
            "\n\n👑 <b>أوامر المالك:</b>\n"
            "<code>مشررف username</code>  — منح صلاحية مشرف\n"
            "<code>سيرفر جديد</code>  — بدء سيرفر جديد"
        )

    sn = gs('server_num')
    await msg.reply_text(
        f"🎮 <b>بوت إدارة سيرفر الجنرال</b>\n"
        f"السيرفر الحالي: <b>#{sn}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>أوامر الجميع:</b>\n"
        f"<code>تسجيل</code>  — التسجيل في السيرفر\n"
        f"<code>حماية اسم الدولة</code>  — التسجيل في قائمة الحماية\n"
        f"<code>قائمة التسجيل</code>  — عرض المسجلين\n"
        f"<code>قائمة الحماية</code>  — عرض قائمة الحماية\n"
        f"<code>قائمة الأبطال</code>  — أبطال نخبة العرب"
        f"{admin_section}{owner_section}\n\n"
        f"⏰ <b>مواعيد التسجيل:</b>\n"
        f"يفتح: الأربعاء 9 مساءً\n"
        f"يغلق: الجمعة 9:30 مساءً\n"
        f"آخر موعد للحماية: الجمعة 10 مساءً",
        parse_mode='HTML'
    )


# ═══════════════════════════════════════════════
#  ⏰  المهام المجدولة
# ═══════════════════════════════════════════════
# التوقيت بـ UTC (السعودية = UTC+3)
# الخميس 9م KSA = 18:00 UTC  → weekday index 3
# الجمعة 8م KSA = 17:00 UTC  → weekday index 4
# الجمعة 10م KSA = 19:00 UTC → weekday index 4

async def job_reg_thursday(ctx: ContextTypes.DEFAULT_TYPE):
    await publish_registration_list(ctx.bot)

async def job_reg_friday(ctx: ContextTypes.DEFAULT_TYPE):
    await publish_registration_list(ctx.bot)

async def job_prot_friday(ctx: ContextTypes.DEFAULT_TYPE):
    await publish_protection_list(ctx.bot)


# ═══════════════════════════════════════════════
#  🚀  تشغيل البوت
# ═══════════════════════════════════════════════

def main():
    logging.basicConfig(
        format  = '%(asctime)s | %(levelname)s | %(message)s',
        level   = logging.INFO
    )

    init_db()
    logging.info("✅ قاعدة البيانات جاهزة")

    app = Application.builder().token(BOT_TOKEN).build()

    # ── معالج الرسائل ──────────────────────────
    app.add_handler(CommandHandler("start", handle))
    app.add_handler(CommandHandler("help",  handle))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    # ── المهام المجدولة ────────────────────────
    jq = app.job_queue

    # الخميس 9 مساء KSA = 18:00 UTC
    jq.run_daily(job_reg_thursday,
                 time    = time(18, 0, tzinfo=pytz.utc),
                 days    = (3,))   # 3 = Thursday

    # الجمعة 8 مساء KSA = 17:00 UTC
    jq.run_daily(job_reg_friday,
                 time    = time(17, 0, tzinfo=pytz.utc),
                 days    = (4,))   # 4 = Friday

    # الجمعة 10 مساء KSA = 19:00 UTC
    jq.run_daily(job_prot_friday,
                 time    = time(19, 0, tzinfo=pytz.utc),
                 days    = (4,))   # 4 = Friday

    logging.info("🤖 البوت يعمل الآن...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
