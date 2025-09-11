import json
import urllib.request
import os
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
    
)
from telegram import ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackQueryHandler
)






TOKEN = "8254639256:AAFUUQyTygf-xwGFQ4AnfNc70VEHn9CgTD4"
USER_FILE = "users.json"
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbzhF7Wozco434eyec5nVLlBwx4Pyha40iRQPukUI6R4CU-qcuxjr2OgyLXTDxV8rjUu2g/exec"  # 换成你自己的

# ========== 登录处理 ==========
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.contact.phone_number
    user_id = str(update.effective_user.id)
    name = update.effective_user.first_name  # 获取用户名字

    if user_id in logged_users:
        await update.message.reply_text(
            f"👋 Welcome back, {logged_users[user_id]}!",
            reply_markup=main_menu_markup
        )
    else:
        logged_users[user_id] = phone_number
        save_users()

        # ✅ 保存到 Google Sheet
        save_to_google_sheet(user_id, phone_number, name)

        await update.message.reply_text(
            f"✅ Welcome, {phone_number}!",
            reply_markup=main_menu_markup
        )

    await update.message.reply_text(
        "📌 Main Menu:",
        reply_markup=main_menu_markup
    )



def save_to_google_sheet(user_id, phone, name):
    data = {
        "user_id": user_id,
        "phone": phone,
        "name": name
    }

    json_data = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(
        GOOGLE_SHEET_URL,
        data=json_data,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = response.read().decode("utf-8")
            print("✅ Saved to Google Sheet:", result)
    except Exception as e:
        print("❌ Error saving to Google Sheet:", e)

# 读取已登录用户
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r", encoding="utf-8") as f:
        logged_users = json.load(f)
else:
    logged_users = {}

def save_users():
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(logged_users, f, ensure_ascii=False, indent=2)

# ========== 游戏数据 ==========
game_list = {
    "Lottery": {
        "provider": "Lottery",
        "name": "Lottery",
        "image": "https://fananaheng.online/image/images.jpeg",
        "url": "https://www.crazygames.com/game/tap-tap-shots"
    },
    "Football": {
        "provider": "Slots",
        "name": "Slots",
        "image": "https://fananaheng.online/image/download.jpeg",
        "url": "https://www.crazygames.com/game/soccer-legends-2021"
    },
    "Sport": {
        "provider": "Sport",
        "name": "Sport",
        "image": "https://fananaheng.online/image/fishing1.jpeg",
        "url": "https://yourgame.com/play/fishingking"
    },
    "Casino": {
        "provider": "Casino",
        "name": "Casino",
        "image": "https://fananaheng.online/image/fishing2.jpeg",
        "url": "https://yourgame.com/play/oceanfishing"
    },
}

# ========== /start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_firstname = update.effective_user.first_name
    photo_url = "https://fananaheng.online/image/login.jpg"
    message = (
        f"Welcome, {user_firstname}, to Malaysia's first licensed Telegram Casino!\n\n"
        "💥 Simply click \"Login / Register\" and immerse yourself. 🤑\n\n"
        "🌐 Website: https://hengongbet.com/"
    )

    contact_button = KeyboardButton("📱 Login / Register", request_contact=True)
    login_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True)

    await update.message.reply_photo(
        photo=photo_url,
        caption=message,
        reply_markup=login_markup
    )
    await update.message.reply_text(
        "👇 Use the keyboard below:",
        reply_markup=login_markup
    )

# ========== 主菜单 ==========
main_menu_keyboard = [
    ["Get Bonus 38", "Customer Support"],
    ["Login to Website", "🚪 Exit"]
   
]
main_menu_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)


def save_to_google_sheet_async(user_id, phone, name):
    def task():
        save_to_google_sheet(user_id, phone, name)
    threading.Thread(target=task, daemon=True).start()


# ========== 登录处理 ==========
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.contact.phone_number
    user_id = str(update.effective_user.id)
    name = update.effective_user.first_name

    # 如果是新用户
    if user_id not in logged_users:
        logged_users[user_id] = phone_number
        save_users()

        # 保存到 Google Sheet（不影响登录流程）
        try:
            save_to_google_sheet(user_id, phone_number, name)
        except Exception as e:
            print("⚠️ 保存到 Google Sheet 出错:", e)

        await update.message.reply_text(
            f"✅ Welcome, {phone_number}!",
            reply_markup=main_menu_markup
        )
    else:
        # 老用户
        await update.message.reply_text(
            f"👋 Welcome back, {logged_users[user_id]}!",
            reply_markup=main_menu_markup
        )

    # 主菜单
    await update.message.reply_text(
        "📌 Main Menu:",
            reply_markup=main_menu_markup
    )



# ========== 菜单文本处理 ==========
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = str(update.effective_user.id)

    if user_id not in logged_users:
        await update.message.reply_text("⚠️ Please click Login / Register to login")
        return

    # if text == "User Profile":
    #     phone_number = logged_users.get(user_id, "Phone number not linked")
    #     await update.message.reply_text(
    #         f"📌 User Details\n\n"
    #         f"Username: {user_id}\n"
    #         f"Name: {update.effective_user.first_name}\n"
    #         f"Email: \n"
    #         f"Mobile: {phone_number}\n"
    #         f"DOB: \n"
    #         f"Country: Malaysia",
    #         reply_markup=main_menu_markup
    #     )



    



    elif text == "🚪 Exit":
        await update.message.reply_text(
            "👋 You have exited. Type /start to restart.",
            reply_markup=ReplyKeyboardRemove()
        )


    elif text == "Login to Website":
        
        await update.message.reply_photo(
            photo = "https://fananaheng.online/image/rebate.webp",
            caption=("Login the Official Website:\nhttps://hengongbet.com/en-my\n"),
        )      

    elif text == "Get Bonus 38":
        
        await update.message.reply_photo(
            photo = "https://fananaheng.online/image/rm38.png",
            caption=("📞 Please Contact Our Customer Services to Get The 38 Bonus:\n"
            "Telegram: @Official_HengOngBet\n"
            "WhatsApp: https://wa.link/4zx1w6"),
            reply_markup=main_menu_markup
        )

    elif text == "Get Bonus 38":
        
        await update.message.reply_photo(
            photo = "https://fananaheng.online/image/rm38.png",
            caption=("📞 Please Contact Our Customer Services:\n"
            "Telegram: @Official_HengOngBet\n"
            "WhatsApp: https://wa.link/4zx1w6"),
            reply_markup=main_menu_markup
        )
    elif text == "Customer Support": 
        await update.message.reply_text( "📞 Contact us at:\nTelegram: @Official_HengOngBet\nWhatsApp: https://wa.link/4zx1w6", reply_markup=main_menu_markup )


    else:
        await update.message.reply_text("I don’t understand your options 🤔", reply_markup=main_menu_markup)

# ========== 游戏回调 ==========
async def lottery_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    game = game_list["Lottery"]
    await query.message.reply_photo(
        photo=game["image"],
        caption=f"🎮 {game['name']}\nProvider: {game['provider']}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Play", web_app=WebAppInfo(url=game["url"]))]]
        )
    )

async def slot_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    game = game_list["Football"]
    await query.message.reply_photo(
        photo=game["image"],
        caption=f"🎮 {game['name']}\nProvider: {game['provider']}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Play", web_app=WebAppInfo(url=game["url"]))]]
        )
    )

async def sport_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    game = game_list["Sport"]
    await query.message.reply_photo(
        photo=game["image"],
        caption=f"🎮 {game['name']}\nProvider: {game['provider']}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Play", web_app=WebAppInfo(url=game["url"]))]]
        )
    )

async def casino_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    game = game_list["Casino"]
    await query.message.reply_photo(
        photo=game["image"],
        caption=f"🎮 {game['name']}\nProvider: {game['provider']}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Play", web_app=WebAppInfo(url=game["url"]))]]
        )
    )
# ========== Callback Handler ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "lottery_menu":
        await lottery_menu_callback(update, context)
    elif query.data == "slot_menu":
        await slot_menu_callback(update, context)
    elif query.data == "sport_menu":
        await sport_menu_callback(update, context)
    elif query.data == "casino_menu":
        await casino_menu_callback(update, context)

# ========== 启动 Bot ==========
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
