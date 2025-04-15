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

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ------------------------- Настройки -------------------------
TOKEN = "7633660729:AAEF7FnE9HO0jfBsJXHRTOznP0s3jiwntPs"
OWNER_ID = 204541083
CHANNEL_ID = "@your_channel"  # Замените на нужный ID или @username канала
# -------------------------------------------------------------

# Определяем стадии ConversationHandler:
# 0 - Выбор товара; 1 - Ввод телефона и имени; 2 - Ввод адресных данных (населений пункт, область и отделение почты);
# 3 - Финальное подтверждение заказа.
CHOOSING_PRODUCT, WAITING_PHONE_NAME, WAITING_ADDRESS, CONFIRM_ORDER = range(4)

# Каталог товаров – 24 продукта с именами, описаниями и ссылками на фото
products = {
    "1": {
        "name": "Зволожуючий крем Bombshell 💖",
        "description": "💧 **Bombshell** – крем, що дарує глибоке зволоження, ніжну текстуру та неповторний аромат для вашої шкіри!",
        "image": "https://i.ibb.co/9k8BmxSN/photo-2025-04-15-16-46-14.jpg"
    },
    "2": {
        "name": "Ніжний лосьйон Tease 🌸",
        "description": "🌺 **Tease** – легкий лосьйон для щоденного догляду, що забезпечує свіжість та м’якість шкіри!",
        "image": "https://i.ibb.co/5X6nDCq4/photo-2025-04-15-16-46-15.jpg"
    },
    "3": {
        "name": "Шовковий крем Seduction ✨",
        "description": "🌹 **Seduction** – крем із насиченою текстурою, що дарує шовкову гладкість та чаруючий аромат!",
        "image": "https://i.ibb.co/qYHnDZrx/photo-2025-04-15-16-46-13.jpg"
    },
    "4": {
        "name": "Містичний крем Dreamy Glow 💎",
        "description": "🌟 **Dreamy Glow** – крем, створений для сяйва та рівномірного відтінку шкіри, підкреслюючи вашу красу!",
        "image": "https://i.ibb.co/r2wmHsqT/photo-2025-04-15-15-08-33.jpg"
    },
    "5": {
        "name": "Розкішний крем Luscious Body 🌟",
        "description": "💖 **Luscious Body** – інтенсивне живлення та відновлення шкіри для відчуття справжньої розкоші!",
        "image": "https://i.ibb.co/1Y98rzQ6/photo-2025-04-15-15-08-27.jpg"
    },
    "6": {
        "name": "Лосьйон Velvet Touch 🌼",
        "description": "💐 **Velvet Touch** – ніжний лосьйон, що дарує м’якість та комфорт, залишаючи приємний аромат на шкірі!",
        "image": "https://i.ibb.co/p6rpLtys/photo-2025-04-15-15-08-22-2.jpg"
    },
    "7": {
        "name": "Крем Charm Essence 🌺",
        "description": "🌷 **Charm Essence** – утончений крем, наповнений життям та енергією завдяки своїй легкій текстурі та свіжому аромату!",
        "image": "https://i.ibb.co/wZKsPN71/photo-2025-04-15-15-08-22.jpg"
    },
    "8": {
        "name": "Лосьйон Glamour Radiance 💫",
        "description": "✨ **Glamour Radiance** – лосьйон, який дарує шкірі сяйво та розкішний вигляд, підкреслюючи вашу індивідуальність!",
        "image": "https://i.ibb.co/HL97djJX/photo-2025-04-15-15-08-21-2.jpg"
    },
    "9": {
        "name": "Крем Mystic Moisture 💧",
        "description": "🌹 **Mystic Moisture** – крем, що дарує глибоке зволоження та робить вашу шкіру неймовірно м’якою і гладкою!",
        "image": "https://i.ibb.co/bRdsf7wN/photo-2025-04-15-15-08-21.jpg"
    },
    "10": {
        "name": "Крем Delightful Dusk 🌙",
        "description": "💖 **Delightful Dusk** – крем для інтенсивного відновлення, що забезпечує ніжний догляд і ексклюзивний аромат для вечора!",
        "image": "https://i.ibb.co/sdDmQmqN/photo-2025-04-15-15-08-20-2.jpg"
    },
    "11": {
        "name": "Крем Enchanted Velvet ✨",
        "description": "💎 **Enchanted Velvet** – відчуйте магію догляду з кремом, який дарує шовковисту м’якість та сяйво вашій шкірі!",
        "image": "https://i.ibb.co/KcNhVvK4/photo-2025-04-15-15-08-20.jpg"
    },
    "12": {
        "name": "Лосьйон Pure Elegance 💫",
        "description": "🌸 **Pure Elegance** – ідеальний баланс між ніжністю та живленням, що забезпечує свіжість і неповторну елегантність!",
        "image": "https://i.ibb.co/Mx9J3CYN/photo-2025-04-15-15-08-19.jpg"
    },
    "13": {
        "name": "Крем Opulent Glow 🌟",
        "description": "💐 **Opulent Glow** – крем, що підкреслює вашу природну красу, даруючи глибоке зволоження та ефектний блиск!",
        "image": "https://i.ibb.co/r2J0CXgm/photo-2025-04-15-15-08-18-2.jpg"
    },
    "14": {
        "name": "Крем Divine Nectar 🍯",
        "description": "🌹 **Divine Nectar** – розкішний крем, натхненний природними компонентами для ексклюзивного догляду за шкірою!",
        "image": "https://i.ibb.co/cXtXDGWC/photo-2025-04-15-15-08-18.jpg"
    },
    "15": {
        "name": "Лосьйон Soft Whisper 🌬",
        "description": "💖 **Soft Whisper** – легкий лосьйон, що дарує свіжість і делікатний аромат, як тихий шепіт весни!",
        "image": "https://i.ibb.co/b4y9SHy/photo-2025-04-15-15-08-17.jpg"
    },
    "16": {
        "name": "Крем Radiant Charm ✨",
        "description": "🌟 **Radiant Charm** – крем для ефективного зволоження, який дарує вашій шкірі неймовірне сяйво та чарівність!",
        "image": "https://i.ibb.co/KcGGjcHs/photo-2025-04-15-15-12-19-2.jpg"
    },
    "17": {
        "name": "Крем Secret Allure 💎",
        "description": "🌺 **Secret Allure** – витончений крем, який підкреслює вашу індивідуальність та додає магнетизму зовнішності!",
        "image": "https://i.ibb.co/4whM3CBj/photo-2025-04-15-15-12-19.jpg"
    },
    "18": {
        "name": "Лосьйон Satin Bliss 🌼",
        "description": "🌷 **Satin Bliss** – ніжний лосьйон, що забезпечує доглянутость шкіри і дарує відчуття шовковистої розкоші!",
        "image": "https://i.ibb.co/ccfr76k4/photo-2025-04-15-15-12-18-2.jpg"
    },
    "19": {
        "name": "Небесний крем Celestial 💫",
        "description": "💐 **Celestial** – крем, що дарує неземну легкість, зволоження та сяйво, створюючи відчуття чистоти кожного дня!",
        "image": "https://i.ibb.co/0yJxwb5b/photo-2025-04-15-15-12-18.jpg"
    },
    "20": {
        "name": "Крем Orchid Dream 🌸",
        "description": "✨ **Orchid Dream** – насичений крем з делікатним ароматом орхідеї для ніжного та ефективного догляду!",
        "image": "https://i.ibb.co/qvTCHVV/photo-2025-04-15-15-12-17.jpg"
    },
    "21": {
        "name": "Лосьйон Serene Touch 🌹",
        "description": "💖 **Serene Touch** – лосьйон, що дарує спокій та свіжість, збагачуючи шкіру вітамінами та зволоженням!",
        "image": "https://i.ibb.co/nMb7BfJb/photo-2025-04-15-15-12-16-2.jpg"
    },
    "22": {
        "name": "Крем Mystical Silk ✨",
        "description": "🌟 **Mystical Silk** – крем для витонченої шкіри, що дарує розкішну гладкість та незабутній аромат!",
        "image": "https://i.ibb.co/bMcQSsLv/photo-2025-04-15-15-12-16.jpg"
    },
    "23": {
        "name": "Крем Eternal Grace 💫",
        "description": "💎 **Eternal Grace** – крем, який поєднує інтенсивне живлення з елегантністю, залишаючи шкіру неймовірно м’якою!",
        "image": "https://i.ibb.co/N2rqMnHr/photo-2025-04-15-15-12-15.jpg"
    },
    "24": {
        "name": "Крем Velvet Enigma 🌙",
        "description": "🌹 **Velvet Enigma** – розкішний крем, що окутує шкіру таємничою ніжністю, даруючи неповторне сяйво!",
        "image": "https://i.ibb.co/YFFmL2WZ/photo-2025-04-15-15-12-14.jpg"
    },
}

# ------------------------- Функции Conversation -------------------------

def start(update: Update, context: CallbackContext) -> int:
    """
    Выводит приветственное сообщение с картинкой и 24 кнопками товаров.
    """
    chat_id = update.effective_chat.id
    welcome_text = (
        "🌟 Вітаємо у світі розкоші та краси Victoria's Secret! 🌟\n\n"
        "Тут ви знайдете оригінальні парфумовані лосьйони та креми з США, які дарують неповторні відчуття та догляд за шкірою.\n"
        "Обирайте товар, який вам подобається, та дізнайтеся більше! 💖"
    )

    buttons = []
    row = []
    # Создаём 24 кнопки (3 в ряд)
    for idx, prod_id in enumerate(products.keys(), start=1):
        product_title = products[prod_id]["name"]
        btn = InlineKeyboardButton(text=product_title, callback_data=f"PRODUCT_{prod_id}")
        row.append(btn)
        if idx % 3 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    reply_markup = InlineKeyboardMarkup(buttons)
    
    welcome_image = "https://i.ibb.co/cS9WCwrJ/photo-2025-04-14-01-23-29.jpg"
    context.bot.send_photo(
        chat_id=chat_id, 
        photo=welcome_image, 
        caption=welcome_text,
        reply_markup=reply_markup
    )
    return CHOOSING_PRODUCT


def select_product(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает выбор товара по кнопке "PRODUCT_{id}" и выводит подробное описание с кнопкой "Замовити 🛍".
    """
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

        keyboard = [
            [InlineKeyboardButton("Замовити 🛍", callback_data=f"ORDER_{prod_id}")]
        ]
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
    """
    При натисканні "Замовити 🛍" запрашивает у пользователя номер телефона и имя.
    """
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
    """
    Получаем от пользователя телефон и имя, затем запрашиваем адрес доставки.
    """
    user_input = update.message.text.strip()
    context.user_data["phone_name"] = user_input

    address_request = (
        "📍 Вкажіть, будь ласка, населений пункт та область.\n"
        "Наприклад: Київ, Київська область\n\n"
        "🏤 Будь ласка, напишіть номер відділення Нової Пошти або Укрпошти.\n"
        "Наприклад: Нова Пошта, відділення №42"
    )
    update.message.reply_text(address_request, parse_mode="Markdown")
    return WAITING_ADDRESS


def get_address(update: Update, context: CallbackContext) -> int:
    """
    Получаем у пользователя адрес доставки (нас. пункт, область та відділення).
    Формируем итоговое сообщение с данными заказа.
    """
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

    keyboard = [
        [
            InlineKeyboardButton("Підтвердити ✅", callback_data="CONFIRM_ORDER"),
            InlineKeyboardButton("Скасувати ❌", callback_data="CANCEL_ORDER")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_photo(
        photo=product["image"],
        caption=summary_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return CONFIRM_ORDER


def confirm_order(update: Update, context: CallbackContext) -> int:
    """
    При підтвердженні замовлення – надсилаємо дані замовлення адміну (з фото) і повідомляємо користувача.
    """
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
        # Отправляем админу фото с данными заказа
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
    """
    Обработка нажатия кнопки "Скасувати ❌".
    """
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
    """
    Команда /cancel для прерывания диалога.
    """
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
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_PRODUCT: [
                CallbackQueryHandler(select_product, pattern=r"^PRODUCT_\d+$"),
                CallbackQueryHandler(order_product, pattern=r"^ORDER_\d+$"),
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
