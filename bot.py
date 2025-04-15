import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import os

# ------------------------- Настройка логирования -------------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ------------------------- Настройки -------------------------
TOKEN = "7633660729:AAEF7FnE9HO0jfBsJXHRTOznP0s3jiwntPs"
OWNER_ID = 2045410830
CHANNEL_ID = "@your_channel"  # Замените на нужный ID или @username канала
# ---------------------------------------------------------------

# Стадии диалога:
# CHOOSING_PRODUCT – выбор товара из меню;
# WAITING_PHONE_NAME – ввод телефона и имени;
# WAITING_ADDRESS – ввод адреса доставки;
# CONFIRM_ORDER – финальное подтверждение заказа.
CHOOSING_PRODUCT, WAITING_PHONE_NAME, WAITING_ADDRESS, CONFIRM_ORDER = range(4)

# Обновлённый каталог ароматов (22 товара)
# (Номера записаны обычными цифрами, а описания и изображения взяты из предоставленного HTML-кода)
products = {
    "1": {
        "name": "1. Ginger Apple Jewel 🍏🌿✨",
        "description": (
            "Свіжий аромат, де яскраве яблуко поєднується с пряним імбиром, створюючи енергійний та освіжаючий букет.\n"
            "🔹 Ноти: зелене яблуко, імбир, журавлина"
        ),
        "image": "https://i.ibb.co/9k8BmxSN/photo-2025-04-15-16-46-14.jpg"
    },
    "2": {
        "name": "2. Pure Seduction Bliss 🍑🌸💫",
        "description": (
            "Солодкий аромат, що поєднує соковитий персик з ніжними пелюстками жасмину, створюючи чарівний та привабливий шлейф.\n"
            "🔹 Ноти: персик, жасмин"
        ),
        "image": "https://i.ibb.co/sdDmQmqN/photo-2025-04-15-15-08-20-2.jpg"
    },
    "3": {
        "name": "3. Toasted Amber 🔥🌸🧡",
        "description": (
            "Теплий аромат з нотами рожевого перцю та бурштину, що огортає м’яким та чуттєвим шлейфом.\n"
            "🔹 Ноти: рожевий перець, бурштин"
        ),
        "image": "https://i.ibb.co/r2wmHsqT/photo-2025-04-15-15-08-33.jpg"
    },
    "4": {
        "name": "4. Love Spell Daydream 🍇🌸☁️",
        "description": (
            "Грайливий аромат з нотами ягід та жасмину, що створює атмосферу мрійливості та ніжності.\n"
            "🔹 Ноти: ягоди, жасмин, мускус"
        ),
        "image": "https://i.ibb.co/1Y98rzQ6/photo-2025-04-15-15-08-27.jpg"
    },
    "5": {
        "name": "5. Pomegranate Rose 🌹🍷🌿",
        "description": (
            "Елегантний аромат, де пелюстки троянди поєднуються з соковитим гранатом та деревними нотами, створюючи витончену композицію.\n"
            "🔹 Ноти: троянда, гранат, деревні акорди"
        ),
        "image": "https://i.ibb.co/p6rpLtys/photo-2025-04-15-15-08-22-2.jpg"
    },
    "6": {
        "name": "6. Citrus Lily 🍋🌸🌞",
        "description": (
            "Свіжий аромат з нотами цитрусу та лілії, що дарує відчуття чистоти та енергії.\n"
            "🔹 Ноти: цитрус, лілія, жасмин"
        ),
        "image": "https://i.ibb.co/wZKsPN71/photo-2025-04-15-15-08-22.jpg"
    },
    "7": {
        "name": "7. Bare Vanilla Bliss 🍦🌺🌬️",
        "description": (
            "Ніжний аромат з нотами ванілі та фіалки, що створює атмосферу затишку та тепла.\n"
            "🔹 Ноти: ваніль, фіалка"
        ),
        "image": "https://i.ibb.co/HL97djJX/photo-2025-04-15-15-08-21-2.jpg"
    },
    "8": {
        "name": "8. Love Spell Bliss 🌸🍑🌼",
        "description": (
            "Легкий аромат з нотами жимолості та бавовни, що дарує відчуття свіжості та ніжності.\n"
            "🔹 Ноти: жимолость, бавовна"
        ),
        "image": "https://i.ibb.co/bRdsf7wN/photo-2025-04-15-15-08-21.jpg"
    },
    "9": {
        "name": "9. Velvet Petals Bliss 🌷🍬💖",
        "description": (
            "Солодкий аромат з нотами фрезії та лілії, що створює атмосферу ніжності та романтики.\n"
            "🔹 Ноти: фрезія, лілія"
        ),
        "image": "https://i.ibb.co/KcNhVvK4/photo-2025-04-15-15-08-20.jpg"
    },
    "10": {
        "name": "10. Coconut Passion Bliss 🥥🌺🍋",
        "description": (
            "Тропічний аромат з нотами кокосу, водяної лілії та лимонного цвіту, що переносить у світ відпочинку та релаксу.\n"
            "🔹 Ноти: кокос, водяна лілія, лимонний цвіт"
        ),
        "image": "https://i.ibb.co/Mx9J3CYN/photo-2025-04-15-15-08-19.jpg"
    },
    "11": {
        "name": "11. Bare Vanilla Daydream 🍦🌳🌫️",
        "description": (
            "М'який аромат з нотами ванілі та сандалу, що створює атмосферу спокою та гармонії.\n"
            "🔹 Ноти: ваніль, сандал"
        ),
        "image": "https://i.ibb.co/r2J0CXgm/photo-2025-04-15-15-08-18-2.jpg"
    },
    "12": {
        "name": "12. Pure Seduction Daydream 🍭🌸☁️",
        "description": (
            "Солодкий аромат з нотами вершкового цукру та замші, що дарує відчуття ніжності та комфорту.\n"
            "🔹 Ноти: вершковий цукор, біла замша"
        ),
        "image": "https://i.ibb.co/cXtXDGWC/photo-2025-04-15-15-08-18.jpg"
    },
    "13": {
        "name": "13. Velvet Petals Daydream 🌸🍮☕",
        "description": (
            "Квітковий аромат з нотами крему та кави, що створює атмосферу затишку та тепла.\n"
            "🔹 Ноти: квіти, крем, кава"
        ),
        "image": "https://i.ibb.co/b4y9SHy/photo-2025-04-15-15-08-17.jpg"
    },
    "14": {
        "name": "14. Coconut Passion 🥥🔥🌴",
        "description": (
            "Солодкий аромат з нотами кокосу та ванілі, що переносить у тропічний рай.\n"
            "🔹 Ноти: кокос, ваніль, лілія"
        ),
        "image": "https://i.ibb.co/KcGGjcHs/photo-2025-04-15-15-12-19-2.jpg"
    },
    "15": {
        "name": "15. Amber Romance 🍒🍮🌳",
        "description": (
            "Теплий аромат з нотами черешні, ванілі та сандалу, що створює атмосферу романтики та затишку.\n"
            "🔹 Ноти: черешня, ваніль, сандал"
        ),
        "image": "https://i.ibb.co/4whM3CBj/photo-2025-04-15-15-12-19.jpg"
    },
    "16": {
        "name": "16. Strawberries & Champagne 🍓🥂✨",
        "description": (
            "Свіжий аромат з нотами полуниці та шампанського, що створює святковий настрій.\n"
            "🔹 Ноти: полуниця, шампанське"
        ),
        "image": "https://i.ibb.co/ccfr76k4/photo-2025-04-15-15-12-18-2.jpg"
    },
    "17": {
        "name": "17. Love Spell 🌸🍑🍒",
        "description": (
            "Справжній бестселер і символ жіночності від Victoria’s Secret!\n"
            "🔹 Ноти: вишневий цвіт, стиглий персик, солодкий нектар"
        ),
        "image": "https://i.ibb.co/0yJxwb5b/photo-2025-04-15-15-12-18.jpg"
    },
    "18": {
        "name": "18. Pear Glacé 🍐🍈💧",
        "description": (
            "Свіжий та фруктовий аромат, що дарує легкість та відчуття чистоти.\n"
            "🔹 Ноти: груша, диня, роси"
        ),
        "image": "https://i.ibb.co/qvTCHVV/photo-2025-04-15-15-12-17.jpg"
    },
    "19": {
        "name": "19. Midnight Bloom 🌌🌺💫",
        "description": (
            "Магнетичний аромат, який вабить з першого вдиху.\n"
            "🔹 Ноти: нічні квіти, пудрова ваніль, легкий мускус"
        ),
        "image": "https://i.ibb.co/nMb7BfJb/photo-2025-04-15-15-12-16-2.jpg"
    },
    "20": {
        "name": "20. Velvet Petals Bliss 💗🌷💖",
        "description": (
            "Ніжний, витончений аромат, який огортає мов м’який шарф.\n"
            "🔹 Ноти: фрезія, солодкий крем"
        ),
        "image": "https://i.ibb.co/b4y9SHy/photo-2025-04-15-15-08-17.jpg"
    },
    "21": {
        "name": "21. Aqua Kiss 🌊🌼🍃",
        "description": (
            "Фрезія та маргаритка створюють чистий, легкий аромат — дихання весни на тілі.\n"
            "🔹 Ноти: фрезія, маргаритка, прохолода листя"
        ),
        "image": "https://i.ibb.co/bMcQSsLv/photo-2025-04-15-15-12-16.jpg"
    },
    "22": {
        "name": "22. Pure Seduction Classic 💋🍑🌸",
        "description": (
            "Соковита слива та квіткова свіжість зливаються в яскравий, романтичний аромат.\n"
            "🔹 Ноти: стигла слива, пелюстки фрезії"
        ),
        "image": "https://i.ibb.co/N2rqMnHr/photo-2025-04-15-15-12-15.jpg"
    },
}

# Функция для генерации меню товаров на нужной странице с навигацией (4 товара на страницу)
def get_product_menu(page: int) -> InlineKeyboardMarkup:
    sorted_products = sorted(products.items(), key=lambda x: int(x[0]))
    per_page = 4
    total_pages = (len(sorted_products) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    current_products = sorted_products[start:end]
    keyboard = []
    for prod_id, prod in current_products:
        btn = InlineKeyboardButton(text=prod["name"], callback_data=f"PRODUCT_{prod_id}")
        keyboard.append([btn])
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"PAGE_{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Далі ▶️", callback_data=f"PAGE_{page + 1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    return InlineKeyboardMarkup(keyboard)

# ------------------------- Обработчики ConversationHandler -------------------------

def start_command(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    welcome_text = (
        "🌟 Ласкаво просимо до Victoria's Secret! 🌟\n\n"
        "Відкрийте для себе розкішний асортимент оригінальних парфумованих лосьйонів та кремів з США. "
        "Наші аромати подарують вам неймовірне відчуття краси та догляду.\n\n"
        "Оберіть свій ідеальний товар нижче:"
    )
    context.user_data["current_page"] = 1
    welcome_image = "https://i.ibb.co/cS9WCwrJ/photo-2025-04-14-01-23-29.jpg"
    context.bot.send_photo(
        chat_id=chat_id,
        photo=welcome_image,
        caption=welcome_text,
        reply_markup=get_product_menu(1)
    )
    return CHOOSING_PRODUCT

def page_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = query.data
    page = int(data.split("_")[1])
    context.user_data["current_page"] = page
    try:
        query.edit_message_reply_markup(reply_markup=get_product_menu(page))
    except Exception:
        query.message.reply_text("Оберіть товар:", reply_markup=get_product_menu(page))
    return CHOOSING_PRODUCT

def back_to_menu_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    page = context.user_data.get("current_page", 1)
    try:
        query.message.delete()
    except Exception:
        pass
    welcome_text = (
        "🌟 Ласкаво просимо до Victoria's Secret! 🌟\n\n"
        "Відкрийте для себе розкішний асортимент оригінальних парфумованих лосьйонів та кремів з США. "
        "Наші аромати подарують вам неймовірне відчуття краси та догляду.\n\n"
        "Оберіть свій ідеальний товар нижче:"
    )
    welcome_image = "https://i.ibb.co/cS9WCwrJ/photo-2025-04-14-01-23-29.jpg"
    context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=welcome_image,
        caption=welcome_text,
        reply_markup=get_product_menu(page)
    )
    return CHOOSING_PRODUCT

def select_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = query.data
    if data.startswith("PRODUCT_"):
        prod_id = data.split("_")[1]
        if prod_id not in products:
            query.edit_message_text("Сталася помилка. Спробуйте ще раз.")
            return CHOOSING_PRODUCT
        context.user_data["selected_product_id"] = prod_id
        product = products[prod_id]
        caption_text = (
            f"🛍 **{product['name']}**\n\n"
            f"{product['description']}\n\n"
            "Натисніть «Замовити 🛍», щоб оформити замовлення!"
        )
        keyboard = [[
            InlineKeyboardButton("Замовити 🛍", callback_data=f"ORDER_{prod_id}"),
            InlineKeyboardButton("⬅️ Назад", callback_data="BACK_TO_MENU")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        chat_id = query.message.chat_id
        context.bot.send_photo(
            chat_id=chat_id,
            photo=product["image"],
            caption=caption_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return CHOOSING_PRODUCT
    else:
        query.edit_message_text("Невідома дія.")
        return CHOOSING_PRODUCT

def order_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = query.data
    if data.startswith("ORDER_"):
        prod_id = data.split("_")[1]
        context.user_data["selected_product_id"] = prod_id
        try:
            query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        phone_request = (
            "📱 Будь ласка, введіть ваш **номер телефону** та **ім'я**.\n\n"
            "Наприклад: `+380 99 123 45 67, Олена`"
        )
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=phone_request,
            parse_mode="Markdown"
        )
        return WAITING_PHONE_NAME
    else:
        query.edit_message_text("Невідома дія.")
        return CHOOSING_PRODUCT

def get_phone_name(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    context.user_data["phone_name"] = user_input
    address_request = (
        "🏤 Введіть, будь ласка, населений пункт, область, номер відділення Нової Пошти або Укрпошти.\n"
        "Наприклад: Київ, Київська область, Нова Пошта, відділення №42"
    )
    update.message.reply_text(address_request, parse_mode="Markdown")
    return WAITING_ADDRESS

def get_address(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    context.user_data["address"] = user_input
    prod_id = context.user_data.get("selected_product_id")
    product = products.get(prod_id)
    if not product:
        update.message.reply_text("Сталася помилка з продуктом. Спробуйте знову.")
        return ConversationHandler.END
    phone_name = context.user_data.get("phone_name", "")
    address = context.user_data.get("address", "")
    summary_text = (
        f"🛍 **{product['name']}**\n\n"
        f"{product['description']}\n\n"
        "**Ваші дані для відправлення:**\n"
        f"• Телефон і ім'я: {phone_name}\n"
        f"• Адреса доставки: {address}\n\n"
        "Перевірте, будь ласка, всі дані. Якщо все правильно – натисніть «Підтвердити ✅». "
        "Якщо бажаєте скасувати, натисніть «Скасувати ❌»."
    )
    keyboard = [[
        InlineKeyboardButton("Підтвердити ✅", callback_data="CONFIRM_ORDER"),
        InlineKeyboardButton("Скасувати ❌", callback_data="CANCEL_ORDER")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_photo(
        photo=product["image"],
        caption=summary_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return CONFIRM_ORDER

def confirm_order(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data
    prod_id = user_data.get("selected_product_id")
    product = products.get(prod_id, {})
    phone_name = user_data.get("phone_name", "")
    address = user_data.get("address", "")
    user = update.effective_user
    full_name = user.full_name
    username = f"@{user.username}" if user.username else ""
    order_msg = (
        f"🛒 **Нове замовлення!**\n\n"
        f"**Товар:** {product.get('name', '—')}\n"
        f"**Телефон і ім'я покупця:** {phone_name}\n"
        f"**Адреса доставки:** {address}\n\n"
        f"**Покупець:** {full_name} {username}\n"
        f"ID користувача: {user.id}\n"
    )
    try:
        context.bot.send_photo(
            chat_id=OWNER_ID,
            photo=product.get("image"),
            caption=order_msg,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Не вдалося відправити повідомлення адміністратору: {e}")
    try:
        query.edit_message_caption(
            caption="✅ Дякуємо! Ваше замовлення в обробці. Очікуйте на дзвінок.",
            parse_mode="Markdown",
            reply_markup=None
        )
    except Exception:
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text="✅ Дякуємо! Ваше замовлення в обробці. Очікуйте на дзвінок."
        )
    context.user_data.clear()
    return ConversationHandler.END

def cancel_order(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    try:
        query.edit_message_caption(
            caption="❌ Ваше замовлення було скасовано.",
            reply_markup=None
        )
    except Exception:
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text="❌ Ваше замовлення було скасовано."
        )
    context.user_data.clear()
    return ConversationHandler.END

def cancel_command(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("❌ Ви скасували оформлення замовлення.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

# ------------------------- Адмін-команды -------------------------

def admin_help(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id != OWNER_ID:
        update.message.reply_text("⚠️ У вас недостатньо прав.")
        return
    text = (
        "Адмін-команди:\n"
        "/help – показати це меню.\n"
        "/send_to_channel <текст> – відправити повідомлення в канал.\n"
        "/cancel – скасувати поточний діалог (користувач).\n"
    )
    update.message.reply_text(text)

def send_to_channel(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id != OWNER_ID:
        update.message.reply_text("⚠️ У вас недостатньо прав.")
        return
    if not context.args:
        update.message.reply_text("Будь ласка, введіть текст після команди /send_to_channel")
        return
    message_text = " ".join(context.args)
    button = InlineKeyboardButton("Підписатися ➡️", url="https://t.me/YOUR_BOT_USERNAME")
    markup = InlineKeyboardMarkup([[button]])
    try:
        context.bot.send_message(chat_id=CHANNEL_ID, text=message_text, reply_markup=markup)
        update.message.reply_text("📢 Повідомлення успішно відправлене в канал!")
    except Exception as e:
        logger.error(e)
        update.message.reply_text("Виникла помилка при відправленні повідомлення в канал.")

# ------------------------- Запуск бота -------------------------

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            CHOOSING_PRODUCT: [
                CallbackQueryHandler(select_product, pattern=r"^PRODUCT_\d+$"),
                CallbackQueryHandler(order_product, pattern=r"^ORDER_\d+$"),
                CallbackQueryHandler(page_handler, pattern=r"^PAGE_\d+$"),
                CallbackQueryHandler(back_to_menu_handler, pattern="^BACK_TO_MENU$")
            ],
            WAITING_PHONE_NAME: [
                MessageHandler(Filters.text & ~Filters.command, get_phone_name)
            ],
            WAITING_ADDRESS: [
                MessageHandler(Filters.text & ~Filters.command, get_address)
            ],
            CONFIRM_ORDER: [
                CallbackQueryHandler(confirm_order, pattern="^CONFIRM_ORDER$"),
                CallbackQueryHandler(cancel_order, pattern="^CANCEL_ORDER$")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("help", admin_help))
    dp.add_handler(CommandHandler("send_to_channel", send_to_channel, pass_args=True))
    updater.start_polling()
    logger.info("Bot started successfully!")
    updater.idle()

if __name__ == "__main__":
    main()
