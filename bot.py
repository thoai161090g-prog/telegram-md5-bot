import telebot
import time
import json
from datetime import datetime

# ================== CẤU HÌNH ==================
BOT_TOKEN = "8082032097:AAHbrdASVDXln_UÙH88rzxbxx9SKG1O9imw"
ADMIN_ID = 8375848425 # THAY ID TELEGRAM ADMIN

bot = telebot.TeleBot(BOT_TOKEN)
DATA_FILE = "data.json"

# ================== DATA ==================
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "keys": {},              # key_name : {time, used_by}
            "authorized_users": {}   # uid : {activated, expire}
        }

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ================== CLEANUP ==================
def cleanup():
    now = time.time()
    expired = []
    for uid, info in data["authorized_users"].items():
        if info["expire"] < now:
            expired.append(uid)

    for uid in expired:
        del data["authorized_users"][uid]

    save_data()

def is_authorized(uid):
    return uid in data["authorized_users"]

# ================== START ==================
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "✨ Xin chào ✨\n\n"
        "🎯 Mừng bạn đến với **BOT PHÂN TÍCH MD5 5.0**\n\n"
        "🔐 Bot sử dụng KEY để hoạt động\n"
        "📩 Liên hệ Admin để lấy key:\n"
        "👉 @nhan161019\n\n"
        "⌨️ Sau khi có key, dùng lệnh:\n"
        "`/key <MÃ_KEY>`",
        parse_mode="Markdown"
    )

# ================== TẠO KEY (ADMIN) ==================
@bot.message_handler(commands=["taokey"])
def tao_key(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "🚫 Bạn không có quyền dùng lệnh này")
        return

    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(
            message,
            "⚙️ Cú pháp:\n"
            "`/taokey <TEN_KEY> <30p|1h|1d>`\n\n"
            "Ví dụ:\n"
            "`/taokey VIPNHAN 1d`",
            parse_mode="Markdown"
        )
        return

    key_name = parts[1]
    option = parts[2]

    if option == "30p":
        t = 1800
    elif option == "1h":
        t = 3600
    elif option == "1d":
        t = 86400
    else:
        bot.reply_to(message, "❌ Thời hạn chỉ hỗ trợ: 30p | 1h | 1d")
        return

    if key_name in data["keys"]:
        bot.reply_to(message, "⚠️ Key này đã tồn tại")
        return

    data["keys"][key_name] = {
        "time": t,
        "used_by": None
    }
    save_data()

    bot.reply_to(
        message,
        f"👑 **TẠO KEY THÀNH CÔNG**\n\n"
        f"🔑 Key: `{key_name}`\n"
        f"⏳ Thời hạn: {option}",
        parse_mode="Markdown"
    )

# ================== LIST KEY (ADMIN) ==================
@bot.message_handler(commands=["listkey"])
def list_key(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "🚫 Bạn không có quyền dùng lệnh này")
        return

    if not data["keys"]:
        bot.reply_to(message, "📭 Hiện chưa có key nào")
        return

    text = "📋 **DANH SÁCH KEY**\n\n"
    for k, v in data["keys"].items():
        status = "🟢 Chưa dùng" if v["used_by"] is None else f"🔴 Đã dùng ({v['used_by']})"
        if v["time"] == 1800:
            time_str = "30 phút"
        elif v["time"] == 3600:
            time_str = "1 giờ"
        else:
            time_str = "1 ngày"

        text += f"🔑 `{k}`\n⏳ {time_str}\n📌 {status}\n\n"

    bot.reply_to(message, text, parse_mode="Markdown")

# ================== DEL KEY (ADMIN) ==================
@bot.message_handler(commands=["delkey"])
def del_key(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "🚫 Bạn không có quyền dùng lệnh này")
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(
            message,
            "⚙️ Dùng: `/delkey <TEN_KEY>`\nVí dụ: `/delkey VIPNHAN`",
            parse_mode="Markdown"
        )
        return

    key_name = parts[1]

    if key_name not in data["keys"]:
        bot.reply_to(message, "❌ Key không tồn tại")
        return

    used_uid = data["keys"][key_name]["used_by"]

    if used_uid and used_uid in data["authorized_users"]:
        del data["authorized_users"][used_uid]

    del data["keys"][key_name]
    save_data()

    bot.reply_to(
        message,
        f"🗑️ **ĐÃ XOÁ KEY**\n🔑 `{key_name}`",
        parse_mode="Markdown"
    )

# ================== NHẬP KEY ==================
@bot.message_handler(commands=["key"])
def nhap_key(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "⚙️ Dùng: `/key <MÃ_KEY>`", parse_mode="Markdown")
        return

    key = parts[1]
    uid = str(message.from_user.id)

    if key not in data["keys"]:
        bot.reply_to(message, "❌ Key không tồn tại")
        return

    info = data["keys"][key]
    if info["used_by"] is not None:
        bot.reply_to(message, "⚠️ Key đã được sử dụng")
        return

    now = time.time()
    expire = now + info["time"]

    data["authorized_users"][uid] = {
        "activated": now,
        "expire": expire
    }
    info["used_by"] = uid
    save_data()

    hsd = datetime.fromtimestamp(expire).strftime("%H:%M %d/%m/%Y")
    bot.reply_to(
        message,
        f"✅ **KÍCH HOẠT THÀNH CÔNG**\n"
        f"⏳ Hết hạn: `{hsd}`\n\n"
        f"📩 Vui lòng gửi **MD5** để phân tích",
        parse_mode="Markdown"
    )

# ================== MD5 ==================
def valid_md5(s):
    return len(s) == 32 and all(c in "0123456789abcdef" for c in s.lower())

def phan_tich(md5):
    x = int(md5, 16)
    tai = x % 100
    xiu = 100 - tai
    do_tin_cay = min(abs(tai - xiu) + 50, 99)
    return tai, xiu, do_tin_cay

# ================== HANDLE MESSAGE ==================
@bot.message_handler(func=lambda m: True)
def all_msg(message):
    uid = str(message.from_user.id)
    cleanup()

    if not is_authorized(uid):
        bot.reply_to(
            message,
            "🚫 **Bạn chưa có KEY hợp lệ**\n"
            "👉 Dùng `/key <MÃ_KEY>` để kích hoạt",
            parse_mode="Markdown"
        )
        return

    text = message.text.strip()

    if not valid_md5(text):
        bot.reply_to(
            message,
            "⚠️ **Mã MD5 không hợp lệ**\n"
            "Vui lòng nhập lại",
            parse_mode="Markdown"
        )
        return

    msg = bot.reply_to(
        message,
        "📥 **Đã nhận mã MD5**\n"
        "⏳ Đang phân tích dữ liệu...",
        parse_mode="Markdown"
    )

    # ===== ĐẾM NGƯỢC 3 GIÂY =====
    for i in range(3, 0, -1):
        bot.edit_message_text(
            f"📥 **Đã nhận mã MD5**\n"
            f"⏳ Phân tích dữ liệu... **{i}s**",
            message.chat.id,
            msg.message_id,
            parse_mode="Markdown"
        )
        time.sleep(1)

    tai, xiu, do_tin_cay = phan_tich(text)
    ket_qua = "🔴 **TÀI**" if tai > xiu else "🟢 **XỈU**"

    bot.edit_message_text(
        f"🎰 **KẾT QUẢ PHÂN TÍCH**\n\n"
        f"🔮 Dự đoán: {ket_qua}\n"
        f"📊 Độ tin cậy: **{do_tin_cay}%**",
        message.chat.id,
        msg.message_id,
        parse_mode="Markdown"
    )

# ================== RUN ==================
if __name__ == "__main__":
    print("✅ Bot đang chạy...")
    bot.infinity_polling()
