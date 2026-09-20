import asyncio
import html
import json
import logging
import math
import os
import random
import re
import threading
import time

import httpx
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden, RetryAfter
from telegram.ext import (
    ApplicationBuilder, ExtBot, ContextTypes,
    CommandHandler, MessageHandler, CallbackQueryHandler, filters,
)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8619392859:AAGah_Fb0upGal4sw7lw4aZVHR_6qYDqVMc"
ADMIN_IDS = [8816389907, 7564889663]
ADMIN_1_USERNAME = "tbtool88"
ADMIN_2_USERNAME = "duybmw"

REQUIRED_CHANNELS = [
    {"name": "TOP 1 EVERY DAY", "username": "@top1everyday", "url": "https://t.me/top1everyday"}
]

GAME_APIS = {
    "sunwin_taixiu": ("https://amongst-plots-called-dining.trycloudflare.com/api/tx", "Sunwin Tài Xỉu"),
    "sunwin_sicbo": ("https://ent-glenn-terrain-project.trycloudflare.com/sicbo/sunwin", "Sunwin Sicbo"),
    "xocdia_md5": ("https://undo-possession-burke-checked.trycloudflare.com/api/txmd5", "Xóc Đĩa 88 MD5"),
    "ogk_fan": ("https://writers-recommend-explicit-optimize.trycloudflare.com/api/txmd5/latest", "OGK Fan MD5"),
    "hitclub_tx": ("https://gossip-marriage-anime-variance.trycloudflare.com/api/tx", "Hitclub Tài Xỉu"),
    "hitclub_md5": ("https://gossip-marriage-anime-variance.trycloudflare.com/api/txmd5", "Hitclub MD5"),
    "hitclub_sicbo": ("https://ent-glenn-terrain-project.trycloudflare.com/sicbo/hitclub", "Hitclub Sicbo"),
    "lc79_tx": ("https://reported-prot-prefers-cattle.trycloudflare.com/api/tx", "LC79 Tài Xỉu"),
    "lc79_md5": ("https://reported-prot-prefers-cattle.trycloudflare.com/api/txmd5", "LC79 MD5"),
    "betvip_tx": ("https://paying-hon-bullet-sms.trycloudflare.com/api/tx", "Betvip Tài Xỉu"),
    "betvip_md5": ("https://paying-hon-bullet-sms.trycloudflare.com/api/md5", "Betvip MD5"),
    "club789_tx": ("https://scout-respect-metal-law.trycloudflare.com/api/tx", "789 Club Tài Xỉu"),
    "club789_sicbo": ("https://ent-glenn-terrain-project.trycloudflare.com/sicbo/789club", "789 Club Sicbo"),
    "b52_tx": ("https://volunteers-executives-granted-liz.trycloudflare.com/taixiu", "B52 Tài Xỉu"),
    "b52_md5": ("https://volunteers-executives-granted-liz.trycloudflare.com/txmd5", "B52 MD5"),
    "b52_sicbo": ("https://ent-glenn-terrain-project.trycloudflare.com/sicbo/sicbo/b52", "B52 Sicbo"),
    "iwin_tx": ("https://flu-prospect-coleman-subscriptions.trycloudflare.com/api/tx", "IWIN Tài Xỉu"),
    "iwin_md5": ("https://flu-prospect-coleman-subscriptions.trycloudflare.com/api/txmd5", "IWIN MD5"),
    "max789_tx": ("https://person-talent-mission-opening.trycloudflare.com/api/tx", "Max789 Tài Xỉu"),
    "max789_md5": ("https://person-talent-mission-opening.trycloudflare.com/api/txmd5", "Max789 MD5"),
    "luck8_txmd5": ("https://leslie-messaging-definitions-marble.trycloudflare.com/api/txmd5", "Luck8 TX MD5"),
    "luck8_sicbo": ("https://leslie-messaging-definitions-marble.trycloudflare.com/api/sicbo40", "Luck8 Sicbo"),
    "ta28_tx": ("https://inform-england-organization-sample.trycloudflare.com/api/tx", "TA28 Tài Xỉu"),
    "ta28_md5": ("https://inform-england-organization-sample.trycloudflare.com/api/txmd5", "TA28 MD5"),
    "son789_tx": ("https://pregnancy-blake-debut-hybrid.trycloudflare.com/api/tx", "Son789 Tài Xỉu"),
    "son789_md5": ("https://pregnancy-blake-debut-hybrid.trycloudflare.com/api/txmd5", "Son789 MD5"),
    "rikvip_tx": ("https://adapter-suggesting-enormous-celebration.trycloudflare.com/api/tx", "Rikvip Tài Xỉu"),
    "rikvip_md5": ("https://adapter-suggesting-enormous-celebration.trycloudflare.com/api/txmd5", "Rikvip MD5"),
    "game68_banxanh": ("https://winds-fonts-seq-jaguar.trycloudflare.com/api/68/thuong", "68 Game Bài Bàn Xanh"),
    "game68_bando": ("https://winds-fonts-seq-jaguar.trycloudflare.com/api/68/thuong", "68 Game Bài Bàn Đỏ"),
    "baccarat_kubet": ("https://amongst-plots-called-dining.trycloudflare.com/api/tx", "Baccarat Kubet"),
}

SUB_MENUS = {
    "sunwin": ("☀️ SUNWIN & XÓC ĐĨA:", [
        ("⚡️ Tài Xỉu Sunwin", "sunwin_taixiu"),
        ("🎮 Sicbo Sunwin", "sunwin_sicbo"),
        ("💵 Xóc Đĩa 88 MD5", "xocdia_md5")]),
    "hitclub": ("⚡️ HITCLUB:", [
        ("⚡️ Hitclub Tài Xỉu", "hitclub_tx"),
        ("📊 Hitclub MD5", "hitclub_md5"),
        ("🎮 Hitclub Sicbo", "hitclub_sicbo")]),
    "b52": ("💸 B52 CLUB:", [
        ("💸 B52 Tài Xỉu", "b52_tx"),
        ("📊 B52 MD5", "b52_md5"),
        ("🎮 B52 Sicbo", "b52_sicbo")]),
    "lc79": ("💵 LC79:", [("💵 LC79 Tài Xỉu", "lc79_tx"), ("📊 LC79 MD5", "lc79_md5")]),
    "betvip": ("💎 BETVIP:", [("💎 Betvip Tài Xỉu", "betvip_tx"), ("📊 Betvip MD5", "betvip_md5")]),
    "club789": ("🔥 789 CLUB:", [("🔥 789 Club Tài Xỉu", "club789_tx"), ("🎮 789 Club Sicbo", "club789_sicbo")]),
    "iwin": ("⭐️ IWIN:", [("⭐️ IWIN Tài Xỉu", "iwin_tx"), ("📊 IWIN MD5", "iwin_md5")]),
    "max789": ("🆕 MAX789:", [("🆕 Max789 Tài Xỉu", "max789_tx"), ("📊 Max789 MD5", "max789_md5")]),
    "luck8": ("✨ LUCK8:", [("✨ Luck8 TX MD5", "luck8_txmd5"), ("🎮 Luck8 Sicbo", "luck8_sicbo")]),
    "ta28": ("📌 TA28:", [("📌 TA28 Tài Xỉu", "ta28_tx"), ("📊 TA28 MD5", "ta28_md5")]),
    "son789": ("📈 SON789:", [("📈 Son789 Tài Xỉu", "son789_tx"), ("📊 Son789 MD5", "son789_md5")]),
    "rikvip": ("🎮 RIKVIP:", [("🎮 Rikvip Tài Xỉu", "rikvip_tx"), ("📊 Rikvip MD5", "rikvip_md5")]),
    "game68": ("▶️ 68 GAME BÀI:", [
        ("🟢 68 Game Bài Bàn Xanh", "game68_banxanh"),
        ("🔴 68 Game Bài Bàn Đỏ", "game68_bando")]),
    "other": ("🌐 OGK FAN & KHÁC:", [("🌐 OGK Fan MD5", "ogk_fan"), ("📊 Baccarat Kubet", "baccarat_kubet")]),
}

# ========== FLASK HEALTH ==========
_flask_app = Flask(__name__)

@_flask_app.route("/")
def _health_root():
    return "OK - BOT RUNNING", 200

@_flask_app.route("/health")
def _health():
    return {"status": "alive", "users": len(user_database), "games": len(history_store)}, 200

def _run_flask():
    port = int(os.environ.get("PORT", 10000))
    _flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

threading.Thread(target=_run_flask, daemon=True).start()
print(f"[INIT] Flask on PORT {os.environ.get('PORT', 10000)}")

# ========== EMOJI PREMIUM ==========
CE = {
    "eyes": ("5210956306952758910", "👀"), "smile": ("5461117441612462242", "🙂"),
    "zap": ("5456140674028019486", "⚡️"), "bag": ("5229064374403998351", "🛍"),
    "stop": ("5260293700088511294", "⛔️"), "block": ("5240241223632954241", "🚫"),
    "excl": ("5274099962655816924", "❗️"), "bang": ("5440660757194744323", "‼️"),
    "globe": ("5447410659077661506", "🌐"), "chat": ("5443038326535759644", "💬"),
    "think": ("5467538555158943525", "💭"), "chart": ("5231200819986047254", "📊"),
    "up": ("5449683594425410231", "🔼"), "dn": ("5447183459602669338", "🔽"),
    "graph": ("5244837092042750681", "📈"), "down": ("5246762912428603768", "📉"),
    "ok": ("5206607081334906820", "✔️"), "x": ("5210952531676504517", "❌"),
    "cool": ("5222079954421818267", "🆒"), "bell": ("5458603043203327669", "🔔"),
    "mask": ("5391112412445288650", "🥸"), "clown": ("5269531045165816230", "🤡"),
    "pin": ("5397782960512444700", "📌"), "cash": ("5409048419211682843", "💵"),
    "fly": ("5233326571099534068", "💸"), "fx": ("5402186569006210455", "💱"),
    "play": ("5264919878082509254", "▶️"), "red": ("5411225014148014586", "🔴"),
    "green": ("5416081784641168838", "🟢"), "right": ("5416117059207572332", "➡️"),
    "fire": ("5424972470023104089", "🔥"), "boom": ("5276032951342088188", "💥"),
    "mic": ("5224736245665511429", "🎤"), "mega": ("5424818078833715060", "📣"),
    "shush": ("5431609822288033666", "🤫"), "down2": ("5449875686837726134", "👎"),
    "speak": ("5460795800101594035", "🗣️"), "search": ("5231012545799666522", "🔍"),
    "shield": ("5251203410396458957", "🛡"), "link": ("5271604874419647061", "🔗"),
    "pc": ("5282843764451195532", "🖥"), "info": ("5334544901428229844", "ℹ️"),
    "like": ("5337080053119336309", "👍"), "pause": ("5359543311897998264", "⏸"),
    "100": ("5341498088408234504", "💯"), "sync": ("5375338737028841420", "🔄"),
    "top": ("5415655814079723871", "🔝"), "new": ("5382357040008021292", "🆕"),
    "soon": ("5440621591387980068", "🔜"), "loc": ("5391032818111363540", "📍"),
    "plus": ("5397916757333654639", "➕"), "gem": ("5427168083074628963", "💎"),
    "star": ("5438496463044752972", "⭐️"), "spark": ("5325547803936572038", "✨"),
    "crown": ("5217822164362739968", "👑"), "trash": ("5445267414562389170", "🗑"),
    "tag": ("5222444124698853913", "🔖"), "mail": ("5253742260054409879", "✉️"),
    "lock": ("5296369303661067030", "🔒"), "wow": ("5303479226882603449", "😮"),
    "clip": ("5305265301917549162", "📎"), "gear": ("5341715473882955310", "⚙️"),
    "game": ("5361741454685256344", "🎮"), "vol": ("5388632425314140043", "🔈"),
    "hour": ("5386367538735104399", "⌛"), "ddl": ("5406745015365943482", "⬇️"),
    "sun": ("5402477260982731644", "☀️"), "rain": ("5399913388845322366", "🌧"),
    "gold": ("5440539497383087970", "🥇"), "idea": ("5422439311196834318", "💡"),
    "cal": ("5413879192267805083", "🗓"), "free": ("5406756500108501710", "🆓"),
    "edit": ("5395444784611480792", "✏️"), "alert": ("5395695537687123235", "🚨"),
    "home": ("5416041192905265756", "🏠"), "flag": ("5460755126761312667", "🚩"),
    "party": ("5461151367559141950", "🎉"), "warn": ("5447644880824181073", "⚠️"),
    "q": ("5436113877181941026", "❓"), "note": ("5463107823946717464", "🎵"),
    "grin": ("5372954454653933911", "😀"), "joy": ("5370953476635368811", "😂"),
    "think2": ("5370724846936267183", "🤔"), "cool2": ("5373141891321699086", "😎"),
    "party2": ("5370870691140737817", "🥳"), "sob": ("5370646412243510708", "😭"),
}

_VS16 = "\ufe0f"
_BY_EMOJI = {e.replace(_VS16, ""): i for i, e in CE.values()}
_PATTERN = re.compile("(?:" + "|".join(re.escape(k) for k in sorted(_BY_EMOJI, key=len, reverse=True)) + ")" + _VS16 + "?")

def premium(text):
    if not text or "<tg-emoji" in text:
        return text
    def repl(m):
        base = m.group(0).replace(_VS16, "")
        return f'<tg-emoji emoji-id="{_BY_EMOJI[base]}">{m.group(0)}</tg-emoji>'
    return _PATTERN.sub(repl, text)

def leading_emoji(text):
    m = _PATTERN.match(text)
    if not m:
        return None, text
    base = m.group(0).replace(_VS16, "")
    return _BY_EMOJI[base], text[m.end():].lstrip()

DATA_FILE = "users.json"
HISTORY_FILE = "history.json"
STATUS_ACTIVE = "🟢 Hoạt động"
STATUS_BLOCKED = "🔴 Đã chặn bot"
PENDING = "⏳ Đang chờ"
WIN = "✔️ Thắng"
LOSE = "❌ Thua"
SKIPPED = "⏭ Bỏ lỡ"
UNKNOWN = "➖ Không xác định"
USERS_PER_PAGE = 15

http_client = httpx.AsyncClient(timeout=3.0, follow_redirects=True)

def btn(text, **kwargs):
    emoji_id, rest = leading_emoji(text)
    if emoji_id and rest:
        kwargs["api_kwargs"] = {"icon_custom_emoji_id": emoji_id}
        text = rest
    return InlineKeyboardButton(text, **kwargs)

class PremiumBot(ExtBot):
    @staticmethod
    def _fix(kwargs, field):
        if kwargs.get("parse_mode") == ParseMode.HTML and isinstance(kwargs.get(field), str):
            kwargs[field] = premium(kwargs[field])
    async def send_message(self, *args, **kwargs):
        self._fix(kwargs, "text"); return await super().send_message(*args, **kwargs)
    async def edit_message_text(self, *args, **kwargs):
        self._fix(kwargs, "text"); return await super().edit_message_text(*args, **kwargs)
    async def send_photo(self, *args, **kwargs):
        self._fix(kwargs, "caption"); return await super().send_photo(*args, **kwargs)
    async def send_document(self, *args, **kwargs):
        self._fix(kwargs, "caption"); return await super().send_document(*args, **kwargs)

# ========== STORAGE ==========
def load_users():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return {int(k): v for k, v in json.load(f).items()}
    except FileNotFoundError:
        return {}
    except Exception as e:
        logger.error(f"Lỗi đọc users: {e}"); return {}

def save_users():
    try:
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(user_database, f, ensure_ascii=False)
        os.replace(tmp, DATA_FILE)
    except Exception as e:
        logger.error(f"Lỗi lưu users: {e}")

def load_history():
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logger.error(f"Lỗi đọc history: {e}"); return {}

def save_history():
    try:
        tmp = HISTORY_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(history_store, f, ensure_ascii=False)
        os.replace(tmp, HISTORY_FILE)
    except Exception as e:
        logger.error(f"Lỗi lưu history: {e}")

user_database = load_users()
history_store = load_history()
active_auto_predictions = {}
user_game_history = {}
# =========================================================
# ENGINE — 33 MODEL ENSEMBLE V9 (port từ JavaScript)
# =========================================================

def clamp(v, lo, hi): return max(lo, min(hi, v))
def safe_div(a, b, d=0.5): return d if b == 0 else a / b
def round4(x): return round(x * 10000) / 10000
def log2(x): return math.log2(x) if x > 0 else 0

def get_results(history, n):
    return [h["result"] for h in history[:min(n, len(history))]]

def count_tai(results): return sum(1 for r in results if r == "TÀI")

def current_streak(results):
    if not results: return {"type": None, "len": 0}
    t = results[0]; ln = 1
    for i in range(1, len(results)):
        if results[i] == t: ln += 1
        else: break
    return {"type": t, "len": ln}

def transition_counts(results):
    TT = TX = XT = XX = 0
    for i in range(len(results) - 1):
        older, newer = results[i + 1], results[i]
        if older == "TÀI" and newer == "TÀI": TT += 1
        elif older == "TÀI" and newer == "XỈU": TX += 1
        elif older == "XỈU" and newer == "TÀI": XT += 1
        elif older == "XỈU" and newer == "XỈU": XX += 1
    return {"TT": TT, "TX": TX, "XT": XT, "XX": XX}

def shannon_entropy(results):
    if len(results) < 2: return 1
    p = count_tai(results) / len(results)
    if p <= 0 or p >= 1: return 0
    return -(p * log2(p) + (1 - p) * log2(1 - p))

def bayesian_tai_prob(results, alpha=1, beta=1):
    t = count_tai(results); n = len(results)
    return (t + alpha) / (n + alpha + beta)

def analyze_rhythm(res):
    if not res: return []
    ordered = list(reversed(res))
    rhythm = []
    cur = ordered[0]; ln = 1
    for i in range(1, len(ordered)):
        if ordered[i] == cur: ln += 1
        else:
            rhythm.append({"type": cur, "len": ln})
            cur = ordered[i]; ln = 1
    rhythm.append({"type": cur, "len": ln})
    return rhythm

def analyze_cau(history):
    res = get_results(history, 30)
    if len(res) < 3:
        return {"type": "UNKNOWN", "strength": 0, "pTai": 0.5, "label": "Chưa đủ cầu"}
    st = current_streak(res)
    trans = transition_counts(res)
    switches = trans["TX"] + trans["XT"]
    ratio = count_tai(res) / len(res)
    ent = shannon_entropy(res)

    if st["len"] >= 3:
        cont = 0; total = 0
        for i in range(len(res) - st["len"]):
            ok = True
            for k in range(st["len"]):
                if res[i + k] != st["type"]: ok = False; break
            if ok and i + st["len"] < len(res):
                total += 1
                if res[i + st["len"]] == st["type"]: cont += 1
        p_cont = cont / total if total >= 2 else (0.4 if st["len"] >= 5 else 0.52)
        p_cont = clamp(p_cont, 0.22, 0.78)
        p_tai = p_cont if st["type"] == "TÀI" else (1 - p_cont)
        return {"type": "CAU_BET_T" if st["type"] == "TÀI" else "CAU_BET_X",
                "strength": clamp(st["len"] / 8, 0.3, 1), "pTai": p_tai,
                "label": f"Cầu bệt {st['type']} x{st['len']}", "streak": st}

    if switches >= max(2, len(res) - 2) * 0.85 and len(res) >= 4:
        next_opp = 0 if res[0] == "TÀI" else 1
        soft = 0.5 + (next_opp - 0.5) * 0.7
        return {"type": "CAU_1_1", "strength": 0.65, "pTai": soft, "label": "Cầu 1-1"}

    if len(res) >= 6:
        pairs = []
        for i in range(0, min(6, len(res) - 1), 2):
            if res[i] == res[i + 1]: pairs.append(res[i])
        if len(pairs) >= 2 and pairs[0] != pairs[1]:
            last_pair = res[0] if res[0] == res[1] else None
            if last_pair:
                p_tai = (0.62 if st["len"] == 1 else 0.38) if last_pair == "TÀI" else (0.38 if st["len"] == 1 else 0.62)
                return {"type": "CAU_2_2", "strength": 0.55, "pTai": p_tai, "label": "Cầu 2-2"}

    if ratio >= 0.68:
        return {"type": "CAU_NGHIENG_T", "strength": clamp((ratio - 0.5) * 2, 0.3, 0.9),
                "pTai": clamp(0.5 + (ratio - 0.5) * 0.8, 0.55, 0.78), "label": "Cầu nghiêng Tài"}
    if ratio <= 0.32:
        return {"type": "CAU_NGHIENG_X", "strength": clamp((0.5 - ratio) * 2, 0.3, 0.9),
                "pTai": clamp(0.5 - (0.5 - ratio) * 0.8, 0.22, 0.45), "label": "Cầu nghiêng Xỉu"}
    if ent > 0.95:
        return {"type": "CAU_HON_HOP", "strength": 0.2, "pTai": 0.5, "label": "Cầu hỗn hợp"}
    return {"type": "CAU_THUONG", "strength": 0.35,
            "pTai": clamp(0.5 + (ratio - 0.5) * 0.6, 0.35, 0.65), "label": "Cầu thường"}

def analyze_previous_results(history):
    res = get_results(history, 20)
    if not res: return {"pTai": 0.5, "conf": 0.2, "signals": [], "sample": 0}
    signals = []; score = 0; weight_sum = 0
    for w in (3, 5, 8, 12, 20):
        if len(res) >= min(w, 3):
            sl = res[:min(w, len(res))]
            p = bayesian_tai_prob(sl, 1, 1)
            wgt = math.sqrt(len(sl)) * (1.3 if w <= 5 else 1)
            score += (p - 0.5) * wgt; weight_sum += wgt
            signals.append({"name": f"freq_{w}", "pTai": p})
    if len(res) >= 3:
        last3 = "".join(res[:3])
        t = 0; n = 0
        for i in range(len(res) - 3):
            if "".join(res[i + 1:i + 4]) == last3:
                n += 1
                if res[i] == "TÀI": t += 1
        if n >= 2:
            p = (t + 1) / (n + 2)
            score += (p - 0.5) * (2 + n * 0.3); weight_sum += 2 + n * 0.3
            signals.append({"name": "last3_match", "pTai": p, "n": n})
    with_total = [h for h in history if h.get("total") is not None][:15]
    if len(with_total) >= 5:
        recent_avg = sum(h["total"] for h in with_total[:5]) / min(5, len(with_total))
        total_bias = (recent_avg - 10.5) / 10
        score += total_bias * 0.8; weight_sum += 0.8
        signals.append({"name": "dice_total", "recentAvg": round4(recent_avg)})
    p_tai = clamp(0.5 + score / weight_sum, 0.18, 0.82) if weight_sum > 0 else 0.5
    conf = clamp(0.3 + min(len(res) / 20, 1) * 0.4 + abs(p_tai - 0.5), 0.25, 0.85)
    return {"pTai": p_tai, "conf": conf, "signals": signals, "sample": len(res)}

def detect_regime(history):
    res = get_results(history, 20)
    if len(res) < 5: return "COLD_START"
    st = current_streak(res)
    ent = shannon_entropy(res)
    trans = transition_counts(res)
    switches = trans["TX"] + trans["XT"]
    ratio = count_tai(res) / len(res)
    if st["len"] >= 5: return "STREAK_T" if st["type"] == "TÀI" else "STREAK_X"
    if switches >= len(res) * 0.7: return "ALTERNATING"
    if ent < 0.6 and ratio > 0.65: return "STABLE_T"
    if ent < 0.6 and ratio < 0.35: return "STABLE_X"
    if ent > 0.95: return "HIGH_ENTROPY"
    if abs(ratio - 0.5) < 0.12: return "BALANCED"
    return "TRENDING"

# ==================== 18 MODEL CŨ ====================
def model_frequency(history, window):
    res = get_results(history, window)
    if not res: return None
    p = bayesian_tai_prob(res, 1, 1)
    shrink = min(1, len(res) / 8)
    return {"id": f"freq_{window}", "pTai": 0.5 + (p - 0.5) * shrink,
            "sample": len(res), "conf": clamp(0.35 + len(res) * 0.03, 0.35, 0.82)}

def model_exp_freq(history):
    res = get_results(history, 30)
    if not res: return None
    w_tai = 0; w_total = 0; w = 1
    for r in res:
        if r == "TÀI": w_tai += w
        w_total += w; w *= 0.9
    return {"id": "exp_freq", "pTai": safe_div(w_tai, w_total),
            "sample": len(res), "conf": clamp(0.4 + len(res) * 0.025, 0.4, 0.85)}

def model_streak(history):
    res = get_results(history, 40)
    if len(res) < 2: return None
    st = current_streak(res)
    cont = 0; total = 0
    for i in range(len(res) - st["len"]):
        same = True
        for k in range(st["len"]):
            if res[i + k] != st["type"]: same = False; break
        if same and i + st["len"] < len(res):
            total += 1
            if res[i + st["len"]] == st["type"]: cont += 1
    p_cont = cont / total if total > 0 else (0.42 if st["len"] >= 4 else 0.55)
    p_cont = clamp(p_cont, 0.25, 0.75)
    p_tai = p_cont if st["type"] == "TÀI" else (1 - p_cont)
    return {"id": "streak", "pTai": p_tai, "sample": total or len(res),
            "conf": clamp(0.4 + min(st["len"], 6) * 0.05, 0.4, 0.8)}

def model_markov1(history):
    res = get_results(history, 60)
    if len(res) < 3: return None
    c = transition_counts(res)
    from_t = c["TT"] + c["TX"]; from_x = c["XT"] + c["XX"]
    last = res[0]
    p_tai = safe_div(c["TT"], from_t) if last == "TÀI" else safe_div(c["XT"], from_x)
    return {"id": "markov1", "pTai": clamp(p_tai, 0.15, 0.85),
            "sample": from_t if last == "TÀI" else from_x,
            "conf": clamp(0.45 + (from_t if last == "TÀI" else from_x) * 0.02, 0.45, 0.88)}

def model_markov2(history):
    res = get_results(history, 60)
    if len(res) < 5: return None
    counts = {}
    for i in range(len(res) - 2):
        key = res[i + 2] + "|" + res[i + 1]
        if key not in counts: counts[key] = {"T": 0, "X": 0}
        if res[i] == "TÀI": counts[key]["T"] += 1
        else: counts[key]["X"] += 1
    key = res[1] + "|" + res[0]
    c = counts.get(key, {"T": 1, "X": 1})
    return {"id": "markov2", "pTai": safe_div(c["T"] + 1, c["T"] + c["X"] + 2),
            "sample": c["T"] + c["X"], "conf": clamp(0.4 + (c["T"] + c["X"]) * 0.03, 0.4, 0.85)}

def model_ngram(history):
    res = get_results(history, 50)
    if len(res) < 4: return None
    last2 = res[1] + res[0]
    last3 = (res[2] if len(res) > 2 else "") + res[1] + res[0]
    t2 = n2 = t3 = n3 = 0
    for i in range(len(res) - 2):
        if res[i + 2] + res[i + 1] == last2:
            n2 += 1
            if res[i] == "TÀI": t2 += 1
    for i in range(len(res) - 3):
        if res[i + 3] + res[i + 2] + res[i + 1] == last3:
            n3 += 1
            if res[i] == "TÀI": t3 += 1
    if n3 >= 2: p_tai = (t3 + 1) / (n3 + 2); sample = n3
    elif n2 >= 2: p_tai = (t2 + 1) / (n2 + 2); sample = n2
    else: return None
    return {"id": "ngram", "pTai": p_tai, "sample": sample, "conf": clamp(0.38 + sample * 0.04, 0.38, 0.8)}

def model_momentum(history):
    res = get_results(history, 15)
    if len(res) < 3: return None
    score = 0; w = 1; sum_w = 0
    for r in res:
        score += (1 if r == "TÀI" else -1) * w
        sum_w += w; w *= 0.75
    ent = shannon_entropy(res)
    damp = 1 - min(ent, 1) * 0.3
    return {"id": "momentum", "pTai": clamp(0.5 + (score / sum_w) * 0.28 * damp, 0.25, 0.75),
            "sample": len(res), "conf": clamp(0.4 + len(res) * 0.02, 0.4, 0.6)}

def model_pattern10(history):
    res = get_results(history, 10)
    if len(res) < 4: return None
    t_count = count_tai(res); ratio = t_count / len(res)
    st = current_streak(res); ent = shannon_entropy(res)
    trans = transition_counts(res); switches = trans["TX"] + trans["XT"]
    bias = (ratio - 0.5) * 0.9
    if st["len"] >= 4: bias += (-0.12 if st["type"] == "TÀI" else 0.12)
    if switches >= len(res) - 2: bias *= 0.6
    damp = 1 - min(ent, 1) * 0.35
    return {"id": "pattern10", "pTai": clamp(0.5 + bias * damp, 0.2, 0.8), "sample": len(res),
            "conf": clamp(0.5 + (10 - abs(t_count - 5)) * 0.03 - ent * 0.15, 0.35, 0.78),
            "meta": {"tCount": t_count, "ratio": round4(ratio), "streak": st,
                     "entropy": round4(ent), "switches": switches}}

def model_cau(history):
    cau = analyze_cau(history)
    return {"id": "cau_engine", "pTai": cau["pTai"], "sample": len(get_results(history, 30)),
            "conf": clamp(0.4 + cau["strength"] * 0.4, 0.35, 0.85), "meta": cau}

def model_prev_analysis(history):
    a = analyze_previous_results(history)
    return {"id": "prev_analysis", "pTai": a["pTai"], "sample": a.get("sample", 0),
            "conf": a["conf"], "meta": a}

def model_bayesian_global(history):
    res = get_results(history, 100)
    if not res: return None
    return {"id": "bayes_global", "pTai": bayesian_tai_prob(res, 2, 2), "sample": len(res),
            "conf": clamp(0.4 + log2(1 + len(res)) * 0.08, 0.4, 0.75)}

def model_similarity(history):
    res = get_results(history, 80)
    if len(res) < 15: return None
    pat_len = min(7, len(res) // 5)
    target = "".join(res[:pat_len])
    t_next = n_next = 0
    for i in range(pat_len, len(res) - 1):
        if "".join(res[i:i + pat_len]) == target:
            n_next += 1
            if res[i - 1] == "TÀI": t_next += 1
    if n_next < 3: return None
    return {"id": "similarity", "pTai": (t_next + 1) / (n_next + 2), "sample": n_next,
            "conf": clamp(0.45 + n_next * 0.04, 0.45, 0.8)}

def model_streak_reversal(history):
    res = get_results(history, 40)
    if len(res) < 6: return None
    st = current_streak(res)
    if st["len"] < 5: return None
    rev_bias = min((st["len"] - 4) * 0.08, 0.35)
    p_tai = (0.5 - rev_bias) if st["type"] == "TÀI" else (0.5 + rev_bias)
    return {"id": "streak_reversal", "pTai": clamp(p_tai, 0.2, 0.8),
            "sample": st["len"], "conf": clamp(0.35 + st["len"] * 0.04, 0.35, 0.7)}

def model_contrarian(history):
    res = get_results(history, 5)
    if len(res) < 5: return None
    t_count = count_tai(res)
    if t_count >= 4: return {"id": "contrarian", "pTai": 0.35, "sample": 5, "conf": 0.35}
    if t_count <= 1: return {"id": "contrarian", "pTai": 0.65, "sample": 5, "conf": 0.35}
    return None

# ==================== 6 MODEL NÂNG CAO ====================
def model_long_trend(history):
    res = get_results(history, 50)
    if len(res) < 30: return None
    first = res[25:50]; second = res[0:25]
    r1 = count_tai(first) / len(first); r2 = count_tai(second) / len(second)
    shift = r2 - r1
    return {"id": "long_trend", "pTai": clamp(0.5 + shift * 0.5, 0.3, 0.7), "sample": len(res),
            "conf": clamp(0.4 + abs(shift) * 2, 0.4, 0.65),
            "meta": {"ratio1": round4(r1), "ratio2": round4(r2), "shift": round4(shift)}}

def model_anti_streak(history):
    res = get_results(history, 20)
    if len(res) < 5: return None
    st = current_streak(res)
    if st["len"] < 3: return None
    strength = min((st["len"] - 2) * 0.08, 0.3)
    p_tai = (0.5 - strength) if st["type"] == "TÀI" else (0.5 + strength)
    return {"id": "anti_streak", "pTai": clamp(p_tai, 0.25, 0.75), "sample": st["len"],
            "conf": clamp(0.35 + st["len"] * 0.04, 0.35, 0.65), "meta": {"streak": st}}

def model_entropy_break(history):
    res = get_results(history, 20)
    if len(res) < 10: return None
    ent5 = shannon_entropy(get_results(history, 5))
    ent15 = shannon_entropy(get_results(history, 15))
    if ent15 - ent5 > 0.4:
        st = current_streak(res)
        p_tai = 0.6 if st["type"] == "TÀI" else 0.4
        return {"id": "entropy_break", "pTai": p_tai, "sample": 10,
                "conf": clamp(0.4 + (ent15 - ent5) * 0.3, 0.4, 0.7),
                "meta": {"ent5": round4(ent5), "ent15": round4(ent15), "gap": round4(ent15 - ent5)}}
    return None

def model_alternation_length(history):
    res = get_results(history, 30)
    if len(res) < 10: return None
    trans = transition_counts(res); switches = trans["TX"] + trans["XT"]
    ratio = switches / (len(res) - 1)
    if ratio > 0.8:
        last = res[0]
        p_tai = 0.35 if last == "TÀI" else 0.65
        return {"id": "alternation", "pTai": clamp(p_tai, 0.3, 0.7), "sample": len(res),
                "conf": clamp(0.4 + ratio * 0.3, 0.4, 0.7), "meta": {"switchRatio": round4(ratio)}}
    return None

def model_dice_sum_trend(history):
    with_total = [h for h in history if h.get("total") is not None][:20]
    if len(with_total) < 8: return None
    totals = [h["total"] for h in with_total]
    n = len(totals)
    sx = sum(range(n)); sy = sum(totals)
    sxy = sum(i * totals[i] for i in range(n)); sx2 = sum(i * i for i in range(n))
    denom = n * sx2 - sx * sx
    if denom == 0: return None
    slope = (n * sxy - sx * sy) / denom
    return {"id": "dice_trend", "pTai": clamp(0.5 + slope * 0.15, 0.3, 0.7),
            "sample": len(with_total), "conf": clamp(0.4 + len(with_total) * 0.02, 0.4, 0.65),
            "meta": {"slope": round4(slope), "recentAvg": round4(sum(totals[:5]) / 5)}}

def model_volatility(history):
    res = get_results(history, 30)
    if len(res) < 15: return None
    trans = transition_counts(res); switches = trans["TX"] + trans["XT"]
    vol = switches / (len(res) - 1)
    if vol > 0.75 or vol < 0.25: return None
    ratio = count_tai(res) / len(res)
    return {"id": "volatility", "pTai": clamp(0.5 + (ratio - 0.5) * 0.7, 0.35, 0.65),
            "sample": len(res), "conf": clamp(0.4 + (0.5 - abs(vol - 0.5)) * 0.4, 0.4, 0.65),
            "meta": {"volatility": round4(vol)}}

# ==================== 6 MODEL GHIM CẦU ====================
def model_ghim_11(history):
    res = get_results(history, 40)
    if len(res) < 8: return None
    rhythm = analyze_rhythm(res)
    if len(rhythm) < 4: return None
    recent = rhythm[-8:]
    if not all(r["len"] == 1 for r in recent) or len(recent) < 4: return None
    cur = recent[-1]
    p_tai = 0.35 if cur["type"] == "TÀI" else 0.65
    return {"id": "ghim_1_1", "pTai": clamp(p_tai, 0.3, 0.7), "sample": len(recent),
            "conf": clamp(0.45 + len(recent) * 0.03, 0.45, 0.72),
            "meta": {"rhythm": "".join(r["type"] + str(r["len"]) for r in recent)}}

def model_ghim_22(history):
    res = get_results(history, 40)
    if len(res) < 12: return None
    rhythm = analyze_rhythm(res)
    if len(rhythm) < 4: return None
    recent = rhythm[-6:]
    if not all(recent[i]["len"] == 2 for i in range(min(6, len(recent)))) or len(recent) < 3: return None
    cur = recent[-1]
    if cur["type"] == "TÀI": p_tai = 0.38 if cur["len"] >= 2 else 0.6
    else: p_tai = 0.62 if cur["len"] >= 2 else 0.4
    return {"id": "ghim_2_2", "pTai": clamp(p_tai, 0.3, 0.7), "sample": len(recent) * 2,
            "conf": clamp(0.4 + len(recent) * 0.03, 0.4, 0.68),
            "meta": {"rhythm": "".join(r["type"] + str(r["len"]) for r in recent)}}

def model_ghim_31(history):
    res = get_results(history, 40)
    if len(res) < 16: return None
    rhythm = analyze_rhythm(res)
    if len(rhythm) < 4: return None
    recent = rhythm[-6:]
    def is_p31(arr):
        return len(arr) >= 4 and all(arr[i]["len"] == (3 if i % 2 == 0 else 1) for i in range(len(arr)))
    def is_p13(arr):
        return len(arr) >= 4 and all(arr[i]["len"] == (1 if i % 2 == 0 else 3) for i in range(len(arr)))
    if is_p31(recent):
        cur = recent[-1]
        p_tai = (0.65 if cur["len"] < 3 else 0.35) if cur["type"] == "TÀI" else (0.35 if cur["len"] < 3 else 0.65)
        return {"id": "ghim_3_1", "pTai": clamp(p_tai, 0.3, 0.7), "sample": len(recent) * 2,
                "conf": clamp(0.42 + len(recent) * 0.03, 0.42, 0.7), "meta": {"pattern": "3-1"}}
    if is_p13(recent):
        cur = recent[-1]
        p_tai = (0.65 if cur["len"] < 1 else 0.35) if cur["type"] == "TÀI" else (0.35 if cur["len"] < 1 else 0.65)
        return {"id": "ghim_3_1", "pTai": clamp(p_tai, 0.3, 0.7), "sample": len(recent) * 2,
                "conf": clamp(0.42 + len(recent) * 0.03, 0.42, 0.7), "meta": {"pattern": "1-3"}}
    return None

def model_ghim_21(history):
    res = get_results(history, 40)
    if len(res) < 12: return None
    rhythm = analyze_rhythm(res)
    if len(rhythm) < 4: return None
    recent = rhythm[-6:]
    def is_p(arr, first):
        return len(arr) >= 4 and all(arr[i]["len"] == (first if i % 2 == 0 else (1 if first == 2 else 2)) for i in range(len(arr)))
    if is_p(recent, 2):
        cur = recent[-1]
        next_len = 2 if len(recent) % 2 == 0 else 1
        p_tai = (0.62 if cur["len"] < next_len else 0.4) if cur["type"] == "TÀI" else (0.38 if cur["len"] < next_len else 0.6)
        return {"id": "ghim_2_1", "pTai": clamp(p_tai, 0.32, 0.68), "sample": len(recent) * 2,
                "conf": clamp(0.4 + len(recent) * 0.03, 0.4, 0.68), "meta": {"pattern": "2-1"}}
    if is_p(recent, 1):
        cur = recent[-1]
        next_len = 1 if len(recent) % 2 == 0 else 2
        p_tai = (0.6 if cur["len"] < next_len else 0.4) if cur["type"] == "TÀI" else (0.4 if cur["len"] < next_len else 0.6)
        return {"id": "ghim_2_1", "pTai": clamp(p_tai, 0.32, 0.68), "sample": len(recent) * 2,
                "conf": clamp(0.4 + len(recent) * 0.03, 0.4, 0.68), "meta": {"pattern": "1-2"}}
    return None

def model_ghim_33(history):
    res = get_results(history, 40)
    if len(res) < 18: return None
    rhythm = analyze_rhythm(res)
    if len(rhythm) < 3: return None
    recent = rhythm[-4:]
    if not all(recent[i]["len"] == 3 for i in range(min(4, len(recent)))) or len(recent) < 2: return None
    cur = recent[-1]
    p_tai = (0.62 if cur["len"] < 3 else 0.38) if cur["type"] == "TÀI" else (0.38 if cur["len"] < 3 else 0.62)
    return {"id": "ghim_3_3", "pTai": clamp(p_tai, 0.32, 0.68), "sample": len(recent) * 3,
            "conf": clamp(0.42 + len(recent) * 0.04, 0.42, 0.7),
            "meta": {"rhythm": "".join(r["type"] + str(r["len"]) for r in recent)}}

def model_ghim_tong_hop(history):
    res = get_results(history, 50)
    if len(res) < 10: return None
    rhythm = analyze_rhythm(res)
    if len(rhythm) < 4: return None
    recent = rhythm[-8:]
    freq = {}
    for r in recent:
        freq[r["len"]] = freq.get(r["len"], 0) + 1
    dom_len = 0; dom_count = 0
    for k, v in freq.items():
        if v > dom_count: dom_count = v; dom_len = int(k)
    if dom_count < 4: return None
    cur = recent[-1]
    p_tai = (0.6 if cur["len"] < dom_len else 0.4) if cur["type"] == "TÀI" else (0.4 if cur["len"] < dom_len else 0.6)
    return {"id": "ghim_tong_hop", "pTai": clamp(p_tai, 0.32, 0.68), "sample": len(recent),
            "conf": clamp(0.42 + dom_count * 0.03, 0.42, 0.7),
            "meta": {"dominantLen": dom_len, "dominantCount": dom_count, "curLen": cur["len"], "curType": cur["type"]}}

# ==================== 3 MODEL PORT TỪ LC79 ====================
def detect_pattern_type_v2(runs):
    if len(runs) < 3: return None
    last = runs[-6:]
    lens = [r["len"] for r in last]
    vals = [r["val"] for r in last]
    last_run = last[-1]
    if all(l == 1 for l in lens) and all(i == 0 or vals[i] != vals[i - 1] for i in range(len(vals))): return "1_1"
    if all(l == 2 for l in lens) and all(i == 0 or vals[i] != vals[i - 1] for i in range(len(vals))): return "2_2"
    if all(l == 3 for l in lens) and all(i == 0 or vals[i] != vals[i - 1] for i in range(len(vals))): return "3_3"
    if len(lens) >= 5 and ",".join(map(str, lens[-5:])) == "2,1,2,1,2": return "2_1_2"
    if len(lens) >= 5 and ",".join(map(str, lens[-5:])) == "1,2,1,2,1": return "1_2_1"
    if len(lens) >= 5 and ",".join(map(str, lens[-5:])) == "3,2,3,2,3": return "3_2_3"
    if len(lens) >= 5 and ",".join(map(str, lens[-5:])) == "4,2,4,2,4": return "4_2_4"
    if len(lens) >= 5 and ",".join(map(str, lens[-5:])) == "2,2,1,2,2": return "2_2_1"
    if len(lens) >= 5 and ",".join(map(str, lens[-5:])) == "1,3,1,3,1": return "1_3_1"
    if len(lens) >= 5 and ",".join(map(str, lens[-5:])) == "3,1,3,1,3": return "3_1_3"
    if last_run and last_run["len"] >= 5: return "long_run"
    return "random"

def model_pattern_type_v2(history):
    res = get_results(history, 40)
    if len(res) < 15: return None
    rhythm = analyze_rhythm(res)
    if len(rhythm) < 3: return None
    rhythm_vals = [{"val": "T" if r["type"] == "TÀI" else "X", "len": r["len"]} for r in rhythm]
    ptype = detect_pattern_type_v2(rhythm_vals)
    if ptype == "random": return None
    last_run = rhythm[-1]; cur_type = last_run["type"]
    p_tai = 0.5
    if ptype == "1_1": p_tai = 0.35 if cur_type == "TÀI" else 0.65
    elif ptype == "2_2": p_tai = (0.38 if last_run["len"] >= 2 else 0.6) if cur_type == "TÀI" else (0.62 if last_run["len"] >= 2 else 0.4)
    elif ptype == "3_3": p_tai = (0.38 if last_run["len"] >= 3 else 0.62) if cur_type == "TÀI" else (0.62 if last_run["len"] >= 3 else 0.38)
    elif ptype == "2_1_2": p_tai = (0.4 if last_run["len"] == 2 else 0.6) if cur_type == "TÀI" else (0.6 if last_run["len"] == 2 else 0.4)
    elif ptype == "1_2_1": p_tai = (0.35 if last_run["len"] == 1 else 0.6) if cur_type == "TÀI" else (0.65 if last_run["len"] == 1 else 0.4)
    elif ptype == "3_2_3": p_tai = (0.38 if last_run["len"] == 3 else 0.6) if cur_type == "TÀI" else (0.62 if last_run["len"] == 3 else 0.4)
    elif ptype == "4_2_4": p_tai = (0.38 if last_run["len"] == 4 else 0.6) if cur_type == "TÀI" else (0.62 if last_run["len"] == 4 else 0.4)
    elif ptype == "2_2_1": p_tai = 0.42 if cur_type == "TÀI" else 0.58
    elif ptype == "1_3_1": p_tai = 0.4 if cur_type == "TÀI" else 0.6
    elif ptype == "3_1_3": p_tai = 0.42 if cur_type == "TÀI" else 0.58
    elif ptype == "long_run":
        if last_run["len"] >= 8: p_tai = 0.3 if cur_type == "TÀI" else 0.7
        elif last_run["len"] >= 5: p_tai = 0.45 if cur_type == "TÀI" else 0.55
    return {"id": "pattern_type_v2", "pTai": clamp(p_tai, 0.25, 0.75), "sample": len(rhythm),
            "conf": clamp(0.42 + len(rhythm) * 0.02, 0.42, 0.7),
            "meta": {"type": ptype, "rhythm": "".join(r["type"] + str(r["len"]) for r in rhythm[-6:])}}

def model_bridge_breaker(history):
    res = get_results(history, 40)
    if len(res) < 30: return None
    rhythm = analyze_rhythm(res)
    if len(rhythm) < 5: return None
    last_run = rhythm[-1]
    if last_run["len"] < 4: return None
    same = [r for r in rhythm if r["type"] == last_run["type"]]
    if len(same) < 5: return None
    lens = [r["len"] for r in same]
    mean = sum(lens) / len(lens)
    var = sum((l - mean) ** 2 for l in lens) / len(lens)
    std = math.sqrt(var)
    if last_run["len"] > mean + std * 1.8:
        p_tai = 0.3 if last_run["type"] == "TÀI" else 0.7
        return {"id": "bridge_breaker", "pTai": clamp(p_tai, 0.25, 0.75), "sample": last_run["len"],
                "conf": clamp(0.45 + last_run["len"] * 0.03, 0.45, 0.75),
                "meta": {"lastLen": last_run["len"], "mean": round4(mean), "std": round4(std)}}
    return None

def model_dice_chaos(history):
    with_dice = [h for h in history if h.get("dice") and len(h["dice"]) == 3 and h.get("total") is not None]
    if len(with_dice) < 15: return None
    last = with_dice[0]
    t_count = x_count = 0
    for i in range(1, len(with_dice)):
        if with_dice[i]["total"] == last["total"]:
            if i - 1 >= 0 and with_dice[i - 1]["result"] == "TÀI": t_count += 1
            elif i - 1 >= 0 and with_dice[i - 1]["result"] == "XỈU": x_count += 1
    for i in range(1, len(with_dice)):
        h = with_dice[i]
        matches = sum(1 for d in last["dice"] if d in h["dice"])
        if matches >= 2 and i - 1 >= 0:
            if with_dice[i - 1]["result"] == "TÀI": t_count += 0.5
            elif with_dice[i - 1]["result"] == "XỈU": x_count += 0.5
    if t_count + x_count < 3: return None
    p_tai = t_count / (t_count + x_count)
    return {"id": "dice_chaos", "pTai": clamp(p_tai, 0.3, 0.7), "sample": t_count + x_count,
            "conf": clamp(0.42 + min(t_count + x_count, 10) * 0.03, 0.42, 0.7),
            "meta": {"tCount": round4(t_count), "xCount": round4(x_count), "lastTotal": last["total"]}}

# ==================== WEIGHT v9 ====================
def get_model_weight(state, model_id, base_conf, sample):
    perf = state["modelPerf"].get(model_id)
    recent_acc = 0.5
    if perf and len(perf.get("recent", [])) >= 3:
        recent_acc = sum(1 for x in perf["recent"] if x) / len(perf["recent"])
    stream_bonus = 1.0
    if perf and perf.get("recent"):
        s = 0
        for i in range(len(perf["recent"]) - 1, -1, -1):
            if perf["recent"][i]: s += 1
            else: break
        stream_bonus = 1 + min(s, 8) * 0.05
    long_acc = 0.5
    if perf and perf.get("total", 0) >= 5:
        long_acc = perf["hits"] / perf["total"]
    boost = state.get("learningBoost", 1)
    sample_factor = clamp(sample / 12, 0.35, 1.3)
    w = base_conf * (0.35 + recent_acc * 1.15 + long_acc * 0.35) * sample_factor * stream_bonus * boost

    if state.get("caustats") and state.get("lastPrediction") and state["lastPrediction"].get("cauType"):
        key = state["lastPrediction"]["cauType"]
        p = state["caustats"]["patterns"].get(key, 0)
        h = state["caustats"]["hits"].get(key, 0)
        if p >= 5:
            cau_acc = h / p
            w *= (0.85 + cau_acc * 0.3)

    regime = state.get("prediction", {}).get("regime", "BALANCED")

    short_term = ["markov1", "markov2", "ngram", "momentum", "streak", "freq_5"]
    if model_id in short_term: w *= 0.5

    if model_id == "cau_engine":
        if regime in ("STREAK_T", "STREAK_X"): w *= 1.4
        elif regime == "ALTERNATING": w *= 1.3
        else: w *= 1.1
    if model_id == "pattern10":
        if regime in ("STABLE_T", "STABLE_X"): w *= 1.35
        elif regime == "HIGH_ENTROPY": w *= 0.6
        else: w *= 1.15
    if model_id == "alternation":
        w *= 1.8 if regime == "ALTERNATING" else 0.5
    if model_id == "anti_streak":
        w *= 1.5 if regime in ("STREAK_T", "STREAK_X") else 0.7
    if model_id == "entropy_break":
        w *= 1.4 if regime in ("STABLE_T", "STABLE_X") else 0.8
    if model_id == "volatility":
        w *= 1.3 if regime == "BALANCED" else 0.9

    if model_id == "bayes_global": w *= 1.5
    if model_id == "long_trend": w *= 1.3
    if model_id == "prev_analysis": w *= 1.2
    if model_id == "freq_20": w *= 1.15
    if model_id == "dice_trend": w *= 1.1
    if model_id == "contrarian": w *= 1.3

    if model_id == "ghim_1_1":
        w *= 1.8 if regime == "ALTERNATING" else 0.6
    if model_id == "ghim_2_2": w *= 1.4
    if model_id in ("ghim_3_1", "ghim_2_1"): w *= 1.3
    if model_id == "ghim_3_3":
        w *= 1.5 if regime in ("STREAK_T", "STREAK_X") else 0.9
    if model_id == "ghim_tong_hop":
        w *= 1.5 if regime in ("STREAK_T", "STREAK_X", "ALTERNATING") else 1.1

    if model_id == "pattern_type_v2": w *= 1.4
    if model_id == "bridge_breaker": w *= 1.5
    if model_id == "dice_chaos": w *= 1.3

    return max(0.03, w)

# ==================== ENSEMBLE v9 ====================
def run_ensemble(state, history):
    n = len(history)
    candidates = [
        lambda: model_frequency(history, 5),
        lambda: model_frequency(history, 10),
        lambda: model_frequency(history, 20) if n >= 15 else None,
        lambda: model_exp_freq(history),
        lambda: model_streak(history),
        lambda: model_markov1(history),
        lambda: model_markov2(history) if n >= 12 else None,
        lambda: model_ngram(history),
        lambda: model_momentum(history),
        lambda: model_pattern10(history),
        lambda: model_cau(history),
        lambda: model_prev_analysis(history),
        lambda: model_bayesian_global(history),
        lambda: model_similarity(history),
        lambda: model_streak_reversal(history),
        lambda: model_contrarian(history),
        lambda: model_long_trend(history),
        lambda: model_anti_streak(history),
        lambda: model_entropy_break(history),
        lambda: model_alternation_length(history),
        lambda: model_dice_sum_trend(history),
        lambda: model_volatility(history),
        lambda: model_ghim_11(history),
        lambda: model_ghim_22(history),
        lambda: model_ghim_31(history),
        lambda: model_ghim_21(history),
        lambda: model_ghim_33(history),
        lambda: model_ghim_tong_hop(history),
        lambda: model_pattern_type_v2(history),
        lambda: model_bridge_breaker(history),
        lambda: model_dice_chaos(history),
    ]

    models = []
    for fn in candidates:
        try:
            m = fn()
            if m and isinstance(m.get("pTai"), (int, float)) and not math.isnan(m["pTai"]):
                m["pTai"] = clamp(m["pTai"], 0.12, 0.88)
                models.append(m)
        except Exception as e:
            logger.debug(f"Model err: {e}")

    if not models:
        return {"prediction": "TÀI", "tai_probability": 0.5, "xiu_probability": 0.5,
                "confidence": 0.2, "risk": "VERY_HIGH", "sample_size": n,
                "regime": "COLD_START", "model_count": 0, "models_agree": 0,
                "top_models": [], "cau": {}, "analysis": {}, "models": []}

    sum_w = 0; sum_p = 0
    weighted = []
    for m in models:
        w = get_model_weight(state, m["id"], m.get("conf", 0.5), m.get("sample", 1))
        sum_w += w; sum_p += m["pTai"] * w
        m2 = dict(m); m2["weight"] = w
        weighted.append(m2)

    p_tai = clamp(sum_p / sum_w, 0.18, 0.82) if sum_w > 0 else 0.5
    pred_t = sum(1 for m in weighted if m["pTai"] >= 0.5)
    agree = max(pred_t, len(models) - pred_t)
    agree_ratio = agree / len(models)
    regime = detect_regime(history)
    ent = shannon_entropy(get_results(history, 15))
    cau = analyze_cau(history)

    gap = abs(p_tai - 0.5) * 2
    conf = 0.25 + gap * 0.35 + agree_ratio * 0.25 + min(n / 40, 1) * 0.15 - ent * 0.12
    conf *= (0.92 + (state.get("learningBoost", 1) - 1) * 0.25)
    if regime in ("HIGH_ENTROPY", "COLD_START"): conf *= 0.7
    if n < 5: conf *= 0.55
    elif n < 10: conf *= 0.75
    conf = clamp(conf, 0.15, 0.88)

    if conf < 0.35 or n < 4: risk = "VERY_HIGH"
    elif conf < 0.48: risk = "HIGH"
    elif conf > 0.68 and gap > 0.22: risk = "LOW"
    else: risk = "MEDIUM"

    prediction = "TÀI" if p_tai >= 0.5 else "XỈU"
    top = sorted(weighted, key=lambda m: -m["weight"])[:5]
    top = [{"id": m["id"], "pTai": round4(m["pTai"]), "w": round4(m["weight"])} for m in top]

    return {
        "prediction": prediction,
        "tai_probability": round4(p_tai),
        "xiu_probability": round4(1 - p_tai),
        "confidence": round4(conf),
        "risk": risk,
        "sample_size": n,
        "regime": regime,
        "model_count": len(models),
        "models_agree": agree,
        "top_models": top,
        "cau": cau,
        "analysis": {
            "entropy": round4(ent),
            "streak": current_streak(get_results(history, 30)),
            "freq10": round4(count_tai(get_results(history, 10)) / min(10, n)) if n >= 5 else None,
            "learningBoost": round4(state.get("learningBoost", 1)),
            "cauLabel": cau.get("label", ""),
            "regime": regime,
        },
        "models": weighted,
    }
# =========================================================
# UTILS — STATE, FETCH, MERGE HISTORY
# =========================================================

def create_state():
    return {
        "modelPerf": {},
        "learningBoost": 1.0,
        "caustats": {"patterns": {}, "hits": {}},
        "lastPrediction": None,
        "prediction": None,
    }

engine_state = {}   # engine_state[api_key] = create_state()


def norm_phien(value) -> str:
    return str(value or "").strip().lstrip("#")


def to_int(value):
    try:
        return int(norm_phien(value))
    except (ValueError, TypeError):
        return None


def derive_result(api_data):
    kq = str(api_data.get("ket_qua", "")).upper()
    if "TÀI" in kq or "TAI" in kq: return "TÀI"
    if "XỈU" in kq or "XIU" in kq: return "XỈU"
    try:
        tong = int(api_data.get("tong"))
    except (TypeError, ValueError):
        return None
    if 11 <= tong <= 18: return "TÀI"
    if 3 <= tong <= 10: return "XỈU"
    return None


async def fetch_api(url):
    try:
        r = await http_client.get(url)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and data:
                data = data[0]
            if isinstance(data, dict):
                return data
    except Exception as e:
        logger.warning(f"Lỗi gọi API {url}: {e}")
    return None


def merge_history(api_key, api_data):
    """Ghi phiên mới từ API vào history_store. Chống trùng session."""
    session = norm_phien(api_data.get("phien"))
    result = derive_result(api_data)
    if not session or not result:
        return False

    lst = history_store.setdefault(api_key, [])
    if any(norm_phien(h.get("session")) == session for h in lst):
        return False

    total = None
    try:
        total = int(api_data.get("tong"))
    except (TypeError, ValueError):
        pass

    dice = None
    d1, d2, d3 = api_data.get("d1"), api_data.get("d2"), api_data.get("d3")
    if d1 is not None and d2 is not None and d3 is not None:
        try:
            dice = [int(d1), int(d2), int(d3)]
        except (TypeError, ValueError):
            dice = None

    lst.append({
        "session": session,
        "result": result,
        "total": total,
        "dice": dice,
    })
    # Chỉ giữ 200 phiên gần nhất
    if len(lst) > 200:
        del lst[:-200]
    save_history()
    return True


def get_history_reversed(api_key):
    """Engine dùng newest-first. Đảo ngược list đã lưu (oldest-first)."""
    lst = history_store.get(api_key, [])
    return list(reversed(lst))


def predict(api_key):
    history = get_history_reversed(api_key)
    state = engine_state.setdefault(api_key, create_state())
    result = run_ensemble(state, history)
    state["prediction"] = result
    state["lastPrediction"] = {
        "session": None,
        "prediction": result["prediction"],
        "cauType": result["cau"].get("type") if isinstance(result["cau"], dict) else None,
    }
    return result


def update_model_perf(api_key, actual_result):
    """Sau khi biết kết quả phiên, cập nhật perf từng model."""
    state = engine_state.get(api_key)
    if not state or not state.get("prediction"):
        return
    models = state["prediction"].get("models", [])
    for m in models:
        mid = m.get("id")
        if not mid: continue
        perf = state["modelPerf"].setdefault(mid, {"hits": 0, "total": 0, "recent": [], "streak": 0})
        pred = "TÀI" if m["pTai"] >= 0.5 else "XỈU"
        hit = (pred == actual_result)
        perf["total"] += 1
        if hit:
            perf["hits"] += 1
            perf["streak"] = perf.get("streak", 0) + 1
        else:
            perf["streak"] = 0
        perf["recent"].append(hit)
        if len(perf["recent"]) > 30:
            perf["recent"] = perf["recent"][-30:]

    # Cập nhật caustats
    cau_type = state["lastPrediction"].get("cauType") if state.get("lastPrediction") else None
    if cau_type:
        state["caustats"]["patterns"][cau_type] = state["caustats"]["patterns"].get(cau_type, 0) + 1
        if state["lastPrediction"]["prediction"] == actual_result:
            state["caustats"]["hits"][cau_type] = state["caustats"]["hits"].get(cau_type, 0) + 1

    # learningBoost đơn giản dựa trên 12 dự đoán gần nhất
    hist = history_store.get(api_key, [])
    if len(hist) >= 3:
        recent = hist[-12:]
        hits = 0
        for h in recent:
            # Không có lưu pred history chính xác → bỏ qua
            pass


# =========================================================
# SUBSCRIPTION CHECK
# =========================================================

_sub_cache = {}
SUB_TTL = 300

async def _is_member(channel, user_id, context):
    try:
        m = await context.bot.get_chat_member(chat_id=channel["username"], user_id=user_id)
        if m.status in ("member", "administrator", "creator"):
            return True
        return m.status == "restricted" and bool(getattr(m, "is_member", False))
    except Exception as e:
        logger.error(f"Lỗi kiểm tra kênh {channel['username']}: {e}")
        return False

async def check_user_subscriptions(user_id, context):
    if _sub_cache.get(user_id, 0) > time.time():
        return []
    results = await asyncio.gather(*(_is_member(ch, user_id, context) for ch in REQUIRED_CHANNELS))
    unjoined = [ch for ch, ok in zip(REQUIRED_CHANNELS, results) if not ok]
    if not unjoined:
        _sub_cache[user_id] = time.time() + SUB_TTL
    return unjoined


# =========================================================
# REGISTER USER
# =========================================================

async def register_user(update: Update):
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat: return
    chat_id = chat.id
    info = user_database.get(chat_id)
    if info is None:
        user_database[chat_id] = {
            "id": chat_id,
            "name": user.full_name or "Không rõ",
            "username": f"@{user.username}" if user.username else "Không có",
            "status": STATUS_ACTIVE,
        }
        save_users()
    elif info.get("status") != STATUS_ACTIVE:
        info["status"] = STATUS_ACTIVE
        save_users()


async def safe_edit(query, text, reply_markup=None, **kwargs):
    try:
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML, **kwargs)
    except BadRequest as e:
        if "not modified" not in str(e).lower():
            logger.error(f"Lỗi edit_text: {e}")


# =========================================================
# MENU
# =========================================================

def home_content(user_id, chat_id):
    info = user_database.get(chat_id, {"id": chat_id, "status": STATUS_ACTIVE})
    text = (
        f"<b>✨ TRANG CHỦ HỆ THỐNG DỰ ĐOÁN ✨</b>\n\n"
        f"<b>📊 THÔNG TIN NGƯỜI DÙNG</b>\n"
        f"• <b>ID:</b> <code>{info['id']}</code>\n"
        f"• <b>TRẠNG THÁI:</b> {info['status']}\n\n"
        f"<b>🔽 Vui lòng lựa chọn các chức năng bên dưới:</b>"
    )
    kb = [
        [btn("🎮 TOOL GAME & LỊCH SỬ TỶ LỆ", callback_data="menu_chon_game")],
        [btn("📜 LỊCH SỬ ĐÚNG/SAI", callback_data="menu_lich_su")],
        [btn("🛠 ADMIN HỖ TRỢ", callback_data="menu_admin_ho_tro")],
        [btn("🎁 LỘC ADMIN", callback_data="menu_loc_admin")],
    ]
    if user_id in ADMIN_IDS:
        kb.append([btn("👑 BẢNG ĐIỀU KHIỂN ADMIN", callback_data="menu_admin_panel")])
    return text, InlineKeyboardMarkup(kb)


def panel_content():
    text = (
        f"<b>👑 BẢNG ĐIỀU KHIỂN ADMIN 👑</b>\n\n"
        f"👥 Tổng số user hiện tại: <b>{len(user_database)}</b>\n"
        f"<i>Chọn các tùy chọn quản trị bên dưới:</i>"
    )
    kb = [
        [btn("👥 Xem Danh Sách User", callback_data="admin_users_0")],
        [btn("📢 Hướng Dẫn Broadcast", callback_data="admin_guide_broadcast")],
        [btn("🏠 Về Trang Chủ", callback_data="menu_trang_chu")],
    ]
    return text, InlineKeyboardMarkup(kb)


async def show_users_page(query, page):
    items = list(user_database.values())
    total_pages = max(1, (len(items) + USERS_PER_PAGE - 1) // USERS_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    chunk = items[page * USERS_PER_PAGE:(page + 1) * USERS_PER_PAGE]
    body = ""
    for idx, info in enumerate(chunk, page * USERS_PER_PAGE + 1):
        body += (f"--- User {idx} ---\n"
                 f"👤 {html.escape(str(info.get('name','')))} ({html.escape(str(info.get('username','')))})\n"
                 f"🆔 <code>{info['id']}</code> | {info.get('status','')}\n\n")
    if not body: body = "Chưa có user nào.\n"
    nav = []
    if page > 0: nav.append(btn("⬅️ Trước", callback_data=f"admin_users_{page-1}"))
    if page < total_pages - 1: nav.append(btn("Sau ➡️", callback_data=f"admin_users_{page+1}"))
    kb = []
    if nav: kb.append(nav)
    kb.append([btn("🔙 Quay Lại Bảng Điều Khiển", callback_data="menu_admin_panel")])
    await safe_edit(query, f"<b>📋 DANH SÁCH USER (Trang {page+1}/{total_pages}):</b>\n\n{body}",
                    InlineKeyboardMarkup(kb))


# =========================================================
# COMMANDS
# =========================================================

async def start(update, context):
    await register_user(update)
    text, markup = home_content(update.effective_user.id, update.effective_chat.id)
    await update.message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)


async def admin_panel(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("<b>⛔️ Bạn không có quyền sử dụng tính năng này.</b>",
                                        parse_mode=ParseMode.HTML)
        return
    if context.args:
        broadcast_text = update.message.text.split(None, 1)[1].strip()
        await do_broadcast(context, update.message, broadcast_text)
        return
    text, markup = panel_content()
    await update.message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)


async def handle_admin_media_broadcast(update, context):
    if update.effective_user.id not in ADMIN_IDS: return
    message = update.message
    parts = (message.caption or "").split(None, 1)
    broadcast_text = parts[1].strip() if len(parts) > 1 else ""
    await do_broadcast(context, message, broadcast_text)


async def do_broadcast(context, message, broadcast_text):
    has_media = bool(message.photo or message.document)
    if not broadcast_text and not has_media:
        await message.reply_text("<b>⚠️ Vui lòng nhập nội dung sau lệnh!</b>", parse_mode=ParseMode.HTML)
        return
    if len(broadcast_text) > (1000 if has_media else 3900):
        await message.reply_text("<b>⚠️ Nội dung quá dài.</b>", parse_mode=ParseMode.HTML)
        return
    targets = [cid for cid, info in user_database.items() if info.get("status") != STATUS_BLOCKED]
    if not targets:
        await message.reply_text("<b>⚠️ Chưa có người dùng.</b>", parse_mode=ParseMode.HTML)
        return
    await message.reply_text(f"<b>⚡️ Đang gửi tới {len(targets)} người dùng...</b>", parse_mode=ParseMode.HTML)
    safe_text = html.escape(broadcast_text)
    success = fail = 0
    changed = False
    for chat_id in targets:
        for attempt in range(2):
            try:
                if message.photo:
                    await context.bot.send_photo(chat_id=chat_id, photo=message.photo[-1].file_id,
                                                 caption=safe_text, parse_mode=ParseMode.HTML)
                elif message.document:
                    await context.bot.send_document(chat_id=chat_id, document=message.document.file_id,
                                                    caption=safe_text, parse_mode=ParseMode.HTML)
                else:
                    await context.bot.send_message(chat_id=chat_id,
                                                   text=f"<b>📣 THÔNG BÁO TỪ ADMIN</b>\n\n{safe_text}",
                                                   parse_mode=ParseMode.HTML)
                success += 1
                break
            except RetryAfter as e:
                await asyncio.sleep(e.retry_after + 1); continue
            except Forbidden:
                user_database[chat_id]["status"] = STATUS_BLOCKED
                active_auto_predictions.pop(chat_id, None)
                changed = True; fail += 1; break
            except Exception as e:
                logger.error(f"Lỗi gửi tới {chat_id}: {e}")
                fail += 1; break
        else:
            fail += 1
        await asyncio.sleep(0.05)
    if changed: save_users()
    await message.reply_text(f"<b>✔️ Gửi xong!</b>\n- Thành công: {success}\n- Thất bại: {fail}",
                             parse_mode=ParseMode.HTML)


# =========================================================
# USER PREDICTION HISTORY
# =========================================================

def resolve_pending(game_history, phien_now, api_data):
    for item in game_history:
        if item["trang_thai"] != PENDING or norm_phien(item["phien"]) != norm_phien(phien_now):
            continue
        result = derive_result(api_data)
        if result is None:
            item["ket_qua_thuc_te"] = html.escape(str(api_data.get("ket_qua", "?")))
            item["trang_thai"] = UNKNOWN
        else:
            item["ket_qua_thuc_te"] = result
            item["trang_thai"] = WIN if item["du_doan"].startswith(result) else LOSE


def history_stats(hist):
    played = sum(1 for i in hist if i["trang_thai"] in (WIN, LOSE))
    wins = sum(1 for i in hist if i["trang_thai"] == WIN)
    rate = round(wins / played * 100, 1) if played else 0
    return wins, played, rate


# =========================================================
# SEND PREDICTION (dùng engine)
# =========================================================

async def send_prediction(context, chat_id, api_key, game_title, phien_du_doan):
    try:
        result = predict(api_key)
    except Exception as e:
        logger.error(f"Predict err: {e}")
        return

    du_doan_raw = result["prediction"]
    du_doan_icon = "TÀI 🔴" if du_doan_raw == "TÀI" else "XỈU 🔵"
    conf = int(round(result["confidence"] * 100))
    sample = result["sample_size"]
    model_count = result["model_count"]
    agree = result["models_agree"]
    cau = result.get("cau") or {}
    cau_label = cau.get("label", "—")

    if phien_du_doan:
        game_history = user_game_history.setdefault(chat_id, {}).setdefault(api_key, [])
        game_history.append({
            "phien": phien_du_doan,
            "du_doan": du_doan_icon,
            "ket_qua_thuc_te": "Đang cập nhật...",
            "trang_thai": PENDING,
        })
        if len(game_history) > 20: game_history.pop(0)

    kb = [
        [btn("📜 Lịch Sử Đúng/Sai", callback_data=f"history_{api_key}")],
        [btn("🛑 Dừng Tự Động Dự Đoán", callback_data="stop_auto")],
        [btn("🏠 Về Trang Chủ", callback_data="menu_trang_chu")],
    ]
    lines = [f"<b>DỰ ĐOÁN {html.escape(game_title)}</b>"]
    if phien_du_doan:
        lines.append(f"<b>PHIÊN</b> <code>{html.escape(phien_du_doan)}</code>")
    lines.append(f"<b>DỰ ĐOÁN:</b> <b>{du_doan_icon}</b>")
    lines.append(f"💯 Độ tin cậy: <b>{conf}%</b> | Sample: {sample}")
    lines.append(f"🧠 Model: {model_count} | Đồng thuận: {agree}/{model_count}")
    lines.append(f"📊 Cầu: <i>{html.escape(cau_label)}</i>")

    await context.bot.send_message(chat_id=chat_id, text="\n".join(lines),
                                   reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)


async def process_user(context, chat_id, data, api_data):
    api_key = data["api_key"]
    game_name = GAME_APIS[api_key][1]
    phien_now = norm_phien(api_data.get("phien"))
    if not phien_now: return

    # 1. Ghi phiên vào history (để engine có data)
    merged = merge_history(api_key, api_data)

    # 2. Nếu phiên mới: cập nhật kết quả model perf cho phiên trước
    if merged:
        result_now = derive_result(api_data)
        if result_now:
            update_model_perf(api_key, result_now)

    # 3. Cập nhật lịch sử user
    game_history = user_game_history.setdefault(chat_id, {}).setdefault(api_key, [])
    resolve_pending(game_history, phien_now, api_data)

    # 4. Chỉ gửi dự đoán mới khi có phiên mới
    if phien_now == data.get("last_phien"):
        return
    data["last_phien"] = phien_now

    for item in game_history:
        if item["trang_thai"] == PENDING:
            item["trang_thai"] = SKIPPED
            item["ket_qua_thuc_te"] = "Bỏ lỡ"

    n = to_int(phien_now)
    phien_du_doan = str(n + 1) if n is not None else f"{phien_now}+1"
    game_title = str(api_data.get("game") or game_name).upper()
    await send_prediction(context, chat_id, api_key, game_title, phien_du_doan)


# =========================================================
# HISTORY VIEW
# =========================================================

async def show_history(query, chat_id, api_key):
    name = GAME_APIS[api_key][1]
    hist = user_game_history.get(chat_id, {}).get(api_key, [])
    wins, played, rate = history_stats(hist)
    if hist:
        body = ""
        for h in reversed(hist[-10:]):
            body += (f"• Phiên {html.escape(h['phien'])} | {h['du_doan']} | "
                     f"KQ: {h['ket_qua_thuc_te']} → <b>{h['trang_thai']}</b>\n")
        head = f"Tỷ lệ đúng: <b>{rate}%</b> ({wins}/{played} phiên đã có kết quả)\n\n"
    else:
        head, body = "", "<i>Chưa có dữ liệu. Hãy bấm dự đoán vài phiên trước nhé.</i>\n"
    kb = [
        [btn("🔄 Làm Mới", callback_data=f"history_{api_key}")],
        [btn("📜 Tất Cả Lịch Sử", callback_data="menu_lich_su")],
        [btn("🏠 Về Trang Chủ", callback_data="menu_trang_chu")],
    ]
    text = f"<b>📜 LỊCH SỬ DỰ ĐOÁN {html.escape(name)}</b>\n\n{head}{body}"
    if (query.message.text or "").startswith("📜"):
        await safe_edit(query, text, InlineKeyboardMarkup(kb))
    else:
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)


async def show_history_menu(query, chat_id):
    games = user_game_history.get(chat_id, {})
    kb = []
    for key, hist in games.items():
        if hist and key in GAME_APIS:
            _, played, rate = history_stats(hist)
            kb.append([btn(f"📜 {GAME_APIS[key][1]} ({rate}% / {played})", callback_data=f"history_{key}")])
    kb.append([btn("🏠 Về Trang Chủ", callback_data="menu_trang_chu")])
    text = ("<b>📜 LỊCH SỬ DỰ ĐOÁN</b>\n\nChọn game để xem đúng/sai:"
            if len(kb) > 1 else
            "<b>📜 LỊCH SỬ DỰ ĐOÁN</b>\n\n<i>Chưa có lịch sử.</i>")
    await safe_edit(query, text, InlineKeyboardMarkup(kb))


# =========================================================
# AUTO PREDICT JOB
# =========================================================

async def auto_predict_job(context):
    if not active_auto_predictions:
        return
    keys = sorted({d["api_key"] for d in active_auto_predictions.values() if d["api_key"] in GAME_APIS})
    responses = await asyncio.gather(*(fetch_api(GAME_APIS[k][0]) for k in keys))
    api_cache = dict(zip(keys, responses))
    sem = asyncio.Semaphore(15)

    async def handle(chat_id, data):
        api_data = api_cache.get(data["api_key"])
        if not api_data: return
        async with sem:
            try:
                await process_user(context, chat_id, data, api_data)
            except Forbidden:
                active_auto_predictions.pop(chat_id, None)
                if chat_id in user_database:
                    user_database[chat_id]["status"] = STATUS_BLOCKED
                    save_users()
            except RetryAfter as e:
                await asyncio.sleep(e.retry_after)
            except Exception as e:
                logger.error(f"Lỗi auto fetch cho {chat_id}: {e}")

    await asyncio.gather(*(handle(cid, d) for cid, d in list(active_auto_predictions.items())))


# =========================================================
# CALLBACK
# =========================================================

async def button_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    data = query.data

    if (data == "menu_admin_panel" or data.startswith("admin_")) and user_id not in ADMIN_IDS:
        await query.answer("Bạn không có quyền truy cập!", show_alert=True)
        return
    await query.answer()
    await register_user(update)

    if data == "stop_auto":
        active_auto_predictions.pop(chat_id, None)
        await query.message.reply_text("<b>🛑 Đã dừng tính năng tự động dự đoán.</b>",
                                       parse_mode=ParseMode.HTML)
        return

    if data == "menu_admin_ho_tro":
        kb = [
            [btn("👨‍💻 Admin 1 (@dongnetsun)", url=f"https://t.me/{ADMIN_1_USERNAME}")],
            [btn("👨‍💻 Admin 2 (@vanvinhdzvailoz)", url=f"https://t.me/{ADMIN_2_USERNAME}")],
            [btn("🏠 Về Trang Chủ", callback_data="menu_trang_chu")],
        ]
        await safe_edit(query,
                        "<b>🛠 HỆ THỐNG HỖ TRỢ TRỰC TUYẾN</b>\n\n<i>Chọn Admin để được trợ giúp:</i>",
                        InlineKeyboardMarkup(kb))
        return

    if data == "menu_admin_panel":
        text, markup = panel_content()
        await safe_edit(query, text, markup)
        return

    if data.startswith("admin_users_"):
        try: page = int(data.rsplit("_", 1)[1])
        except ValueError: page = 0
        await show_users_page(query, page)
        return

    if data == "admin_guide_broadcast":
        back_kb = [[btn("🔙 Quay Lại Bảng Điều Khiển", callback_data="menu_admin_panel")]]
        await safe_edit(query,
                        "<b>📢 HƯỚNG DẪN GỬI THÔNG BÁO:</b>\n\n"
                        "Gõ: <code>/ad &lt;Nội dung&gt;</code> hoặc <code>/admin &lt;Nội dung&gt;</code>\n"
                        "Gửi kèm ảnh/file: caption bắt đầu bằng <code>/ad</code>.",
                        InlineKeyboardMarkup(back_kb))
        return

    if data == "menu_trang_chu":
        text, markup = home_content(user_id, chat_id)
        await safe_edit(query, text, markup)
        return

    unjoined = await check_user_subscriptions(user_id, context)
    if unjoined:
        kb = [[btn(f"➡️ Vào Nhóm: {ch['name']}", url=ch["url"])] for ch in unjoined]
        kb.append([btn("🔄 Kiểm Tra Lại", callback_data=data)])
        kb.append([btn("🏠 Quay Lại Trang Chủ", callback_data="menu_trang_chu")])
        warning_text = ("<b>⛔️ BẠN CHƯA HOÀN TẤT ĐIỀU KIỆN SỬ DỤNG TOOL FREE!</b>\n\n"
                        "Vui lòng tham gia đầy đủ các kênh sau:\n")
        for ch in REQUIRED_CHANNELS:
            icon = "❌" if ch in unjoined else "✔️"
            warning_text += f"• <a href='{ch['url']}'>{html.escape(ch['name'])}</a> {icon}\n"
        warning_text += "\n<i>Xong bấm <b>Kiểm Tra Lại</b>!</i>"
        await safe_edit(query, warning_text, InlineKeyboardMarkup(kb), disable_web_page_preview=True)
        return

    if data == "menu_lich_su":
        await show_history_menu(query, chat_id); return

    if data.startswith("history_"):
        key = data[len("history_"):]
        if key in GAME_APIS:
            await show_history(query, chat_id, key)
        return

    if data == "menu_chon_game":
        kb = [
            [btn("☀️ Sunwin", callback_data="sub_sunwin"), btn("⚡️ Hitclub", callback_data="sub_hitclub")],
            [btn("💸 B52", callback_data="sub_b52"), btn("💵 LC79", callback_data="sub_lc79")],
            [btn("💎 Betvip", callback_data="sub_betvip"), btn("🔥 789 Club", callback_data="sub_club789")],
            [btn("⭐️ IWIN", callback_data="sub_iwin"), btn("🆕 Max789", callback_data="sub_max789")],
            [btn("✨ Luck8", callback_data="sub_luck8"), btn("📌 TA28", callback_data="sub_ta28")],
            [btn("📈 Son789", callback_data="sub_son789"), btn("🎮 Rikvip", callback_data="sub_rikvip")],
            [btn("▶️ 68 Game Bài", callback_data="sub_game68"), btn("🌐 OGK Fan & Khác", callback_data="sub_other")],
            [btn("🏠 Về Trang Chủ", callback_data="menu_trang_chu")],
        ]
        await safe_edit(query, "<b>🎮 HỆ THỐNG CHỌN NỀN TẢNG GAME DỰ ĐOÁN:</b>", InlineKeyboardMarkup(kb))
        return

    if data.startswith("sub_"):
        menu = SUB_MENUS.get(data[4:])
        if not menu: return
        title, items = menu
        kb = [[btn(label, callback_data=f"api_{key}")] for label, key in items]
        kb.append([btn("🔼 Quay Lại Chọn Game", callback_data="menu_chon_game")])
        await safe_edit(query, f"<b>{title}</b>", InlineKeyboardMarkup(kb))
        return

    if data.startswith("api_"):
        api_key = data[4:]
        if api_key not in GAME_APIS:
            await query.message.reply_text("<b>⚠️ Game không tồn tại.</b>", parse_mode=ParseMode.HTML)
            return
        target_url, game_display_name = GAME_APIS[api_key]
        api_data = await fetch_api(target_url)

        # Ghi history nếu có
        if api_data:
            merge_history(api_key, api_data)

        active_auto_predictions[chat_id] = {"api_key": api_key, "last_phien": ""}
        stop_kb = [
            [btn("🛑 Dừng Tự Động Dự Đoán Game Này", callback_data="stop_auto")],
            [btn("🏠 Về Trang Chủ", callback_data="menu_trang_chu")],
        ]
        await query.message.reply_text(
            f"<b>🚀 Đã kích hoạt TỰ ĐỘNG DỰ ĐOÁN cho {html.escape(game_display_name)}!</b>\n"
            f"<i>Engine 33 model đang chạy. Cần ≥2 phiên để dự đoán chính xác.</i>",
            reply_markup=InlineKeyboardMarkup(stop_kb), parse_mode=ParseMode.HTML,
        )
        try:
            if api_data and norm_phien(api_data.get("phien")):
                await process_user(context, chat_id, active_auto_predictions[chat_id], api_data)
            else:
                await send_prediction(context, chat_id, api_key, game_display_name, None)
        except Exception as e:
            logger.error(f"Lỗi dự đoán ngay cho {chat_id}: {e}")
        return

    if data == "menu_loc_admin":
        loc_values = ["50k 💵", "100k 💵", "200k 💵", "500k 💵", "1 Triệu 💎", "Chúc bạn may mắn lần sau 🤡"]
        chosen = random.choice(loc_values)
        qr_link = "https://ibb.co/BHTvRB1t"
        await query.message.reply_text(
            f"<b>🎉 PHÁT LỘC ADMIN 🎉</b>\n\n"
            f"🎁 Kết quả: <b>{chosen}</b>\n\n"
            f"📸 <a href='{qr_link}'>Nhấn để xem QR lộc admin</a>\n\n"
            f"<i>Chụp màn hình gửi Admin để xác nhận!</i>",
            parse_mode=ParseMode.HTML,
        )
# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(update, context):
    logger.error("Lỗi không bắt được:", exc_info=context.error)


async def on_shutdown(application):
    try:
        await http_client.aclose()
    except Exception:
        pass


# =========================================================
# MAIN
# =========================================================

def main():
    application = (
        ApplicationBuilder()
        .bot(PremiumBot(token=TOKEN))
        .post_shutdown(on_shutdown)
        .build()
    )

    if application.job_queue is None:
        raise RuntimeError('Thiếu JobQueue. Cài bằng: pip install "python-telegram-bot[job-queue]"')

    # Chạy auto predict mỗi 5 giây
    application.job_queue.run_repeating(auto_predict_job, interval=5, first=2)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler(["ad", "admin"], admin_panel))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(
        (filters.PHOTO | filters.Document.ALL) & filters.CaptionRegex(r"^/(ad|admin)(@\w+)?(\s|$)"),
        handle_admin_media_broadcast,
    ))
    application.add_error_handler(error_handler)

    logger.info("Bot đang chạy (33 model ensemble)...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
