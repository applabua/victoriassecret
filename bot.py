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

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ------------------------- Настройки -------------------------
TOKEN = "7633660729:AAEF7FnE9HO0jfBsJXHRTOznP0s3jiwntPs"   # Например: "123456789:ABC..."
OWNER_ID = 2045410830        # Ваш Telegram ID (администратора)
CHANNEL_ID = "@ваш_канал"   # Например: "@my_channel" или числовой ID
# -------------------------------------------------------------

# Состояния для ConversationHandler
(
    CHOOSING_PRODUCT,    # Пользователь выбирает товар (через инлайн-кнопки)
    WAITING_PHONE_NAME,  # Пользователь вводит телефон и имя
    WAITING_CITY_REGION, # Пользователь вводит населённый пункт и область
    WAITING_POST_OFFICE, # Пользователь вводит номер отделения почты
    CONFIRM_ORDER        # Пользователь подтверждает или отменяет заказ
) = range(5)

# Каталог продуктов (пример: 24 позиции)
products = {
    "1": {
        "name": "Зволожуючий крем Bombshell 💖",
        "description": (
            "💧 **Bombshell** – крем, що дарує глибоке зволоження, "
            "ніжну текстуру та неповторний аромат для вашої шкіри!"
        ),
        "image": "https://i.ibb.co/9k8BmxSN/photo-2025-04-15-16-46-14.jpg"
    },
    "2": {
        "name": "Ніжний лосьйон Tease 🌸",
        "description": (
            "🌺 **Tease** – легкий лосьйон для щоденного догляду, "
            "що забезпечує свіжість та м’якість шкіри!"
        ),
        "image": "https://i.ibb.co/5X6nDCq4/photo-2025-04-15-16-46-15.jpg"
    },
    "3": {
        "name": "Шовковий крем Seduction ✨",
        "description": (
            "🌹 **Seduction** – крем із насиченою текстурою, "
            "що дарує шовкову гладкість та чаруючий аромат!"
        ),
        "image": "https://i.ibb.co/qYHnDZrx/photo-2025-04-15-16-46-13.jpg"
    },
    "4": {
        "name": "Містичний крем Dreamy Glow 💎",
        "description": (
            "🌟 **Dreamy Glow** – крем, створений для сяйва та "
            "рівномірного відтінку шкіри, підкреслюючи вашу красу!"
        ),
        "image": "https://i.ibb.co/r2wmHsqT/photo-2025-04-15-15-08-33.jpg"
    },
    # При необходимости добавьте оставшиеся товары до 24 (или сколько нужно)
    # ...
}

# -------------------------------------------------------------
#                   Шаги разговора (Conversation)
# -------------------------------------------------------------

def start(update: Update, context: CallbackContext) -> int:
    """
    Точка входа в ConversationHandler.
    Показывает приветственное сообщение и список товаров (inline-кнопки).
    """
    chat_id = update.effective_chat.id
    welcome_text = (
        "🌟 Вітаємо у світі розкоші та краси Victoria's Secret! 🌟\n\n"
        "Тут ви знайдете оригінальні парфумовані лосьйони та креми з США, "
        "які дарують неповторні відчуття та догляд за шкірою.\n"
        "Оберіть товар, який вам подобається, щоб дізнатися більше! 💖"
    )

    # Формируем кнопки для каждого продукта (3 в ряд)
    buttons = []
    row = []
    for idx, prod_id in enumerate(products.keys(), start=1):
        product_title = products[prod_id]["name"]
        btn = InlineKeyboardButton(
            text=product_title, 
            callback_data=f"PRODUCT_{prod_id}"
        )
        row.append(btn)
        if idx % 3 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    reply_markup = InlineKeyboardMarkup(buttons)

    # Отправляем превью-картинку + текст + инлайн-кнопки
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
    Обработка выбора продукта через inline-кнопку вида: PRODUCT_{id}.
    Показываем описание и кнопку «Замовити».
    """
    query = update.callback_query
    query.answer()

    data = query.data
    if data.startswith("PRODUCT_"):
        prod_id = data.split("_")[1]
        if prod_id not in products:
            query.edit_message_text("Сталася помилка. Спробуйте ще раз.")
            return CHOOSING_PRODUCT

        # Сохраняем ID выбранного продукта в user_data
        context.user_data["selected_product_id"] = prod_id

        product = products[prod_id]
        caption_text = (
            f"🛍 **{product['name']}**\n\n"
            f"{product['description']}\n\n"
            "Натисніть «Замовити 🛍», щоб оформити замовлення!"
        )

        # Оставляем только одну кнопку «Замовити»
        keyboard = [
            [
                InlineKeyboardButton("Замовити 🛍", callback_data=f"ORDER_{prod_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Редактируем текущее сообщение (либо отправляем новое) с фото
        chat_id = query.message.chat_id
        # Удобнее отправить новое сообщение, а старое можно оставить как есть
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
    Обработка нажатия «Замовити 🛍» -> переходим к запросу телефона и имени.
    """
    query = update.callback_query
    query.answer()
    
    data = query.data
    if data.startswith("ORDER_"):
        prod_id = data.split("_")[1]
        # На случай, если пользователь обновил страницу или выбрал другой товар
        context.user_data["selected_product_id"] = prod_id

        # Убираем кнопки у предыдущего сообщения (по возможности)
        try:
            query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        # Спрашиваем у пользователя номер телефона и имя
        text_request = (
            "📱 Будь ласка, введіть ваш **номер телефону** та **ім'я** у одному повідомленні.\n\n"
            "_Наприклад:_ `+380 99 123 45 67, Олена`"
        )
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=text_request,
            parse_mode="Markdown"
        )
        return WAITING_PHONE_NAME
    else:
        query.edit_message_text("Невідома дія.")
        return CHOOSING_PRODUCT


def get_phone_name(update: Update, context: CallbackContext) -> int:
    """
    Получаем от пользователя телефон и имя.
    """
    user_input = update.message.text.strip()
    context.user_data["phone_name"] = user_input  # Сохраняем в user_data

    # Теперь спрашиваем город/область
    text_request = (
        "📍 Вкажіть, будь ласка, **населений пункт** та **область**.\n\n"
        "_Наприклад:_ `Київ, Київська область`"
    )
    update.message.reply_text(text_request, parse_mode="Markdown")
    return WAITING_CITY_REGION


def get_city_region(update: Update, context: CallbackContext) -> int:
    """
    Получаем населённый пункт и область.
    """
    user_input = update.message.text.strip()
    context.user_data["city_region"] = user_input

    # Просим номер отделения НП или УкрПошты
    text_request = (
        "🏤 Будь ласка, напишіть номер відділення **Нової Пошти** або **Укрпошти**.\n\n"
        "_Наприклад:_ `Нова Пошта, відділення №42`"
    )
    update.message.reply_text(text_request, parse_mode="Markdown")
    return WAITING_POST_OFFICE


def get_post_office(update: Update, context: CallbackContext) -> int:
    """
    Получаем номер отделения почты (Новая Почта или УкрПошта).
    После этого формируем финальное подтверждение заказа.
    """
    user_input = update.message.text.strip()
    context.user_data["post_office"] = user_input

    # Формируем текст с данными заказа
    prod_id = context.user_data.get("selected_product_id")
    product = products.get(prod_id)
    if not product:
        update.message.reply_text("Сталася помилка з продуктом. Спробуйте знову.")
        return ConversationHandler.END

    phone_name = context.user_data.get("phone_name", "")
    city_region = context.user_data.get("city_region", "")
    post_off = context.user_data.get("post_office", "")

    summary_text = (
        f"🛍 **{product['name']}**\n\n"
        f"{product['description']}\n\n"
        "**Ваші дані для відправлення:**\n"
        f"• Телефон і ім'я: {phone_name}\n"
        f"• Місто, область: {city_region}\n"
        f"• Відділення: {post_off}\n\n"
        "Перевірте, будь ласка, всі дані. Якщо все правильно – натисніть «Підтвердити ✅». "
        "Якщо бажаєте скасувати, натисніть «Скасувати ❌»."
    )

    # Показываем итоговое сообщение и inline-кнопки подтверждения/отмены
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
    Пользователь нажал «Підтвердити ✅».
    Отправляем заказ администратору, выводим пользователю сообщение об успехе.
    """
    query = update.callback_query
    query.answer()

    user_data = context.user_data
    prod_id = user_data.get("selected_product_id")
    product = products.get(prod_id, {})
    phone_name = user_data.get("phone_name", "")
    city_region = user_data.get("city_region", "")
    post_office = user_data.get("post_office", "")

    user = update.effective_user
    full_name = user.full_name
    username = f"@{user.username}" if user.username else ""

    # Отправляем админу все сведения о заказе
    order_msg = (
        "🛒 **Нове замовлення!**\n\n"
        f"**Товар:** {product.get('name', '—')}\n"
        f"**Телефон і ім'я покупця:** {phone_name}\n"
        f"**Населений пункт, область:** {city_region}\n"
        f"**Відділення:** {post_office}\n\n"
        f"**Покупець:** {full_name} {username}\n"
        f"ID користувача: {user.id}\n"
    )
    try:
        context.bot.send_message(
            chat_id=OWNER_ID,
            text=order_msg,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Не вдалося відправити повідомлення адміністратору: {e}")

    # Сообщение пользователю
    try:
        query.edit_message_caption(
            caption="✅ Дякуємо! Ваше замовлення в обробці. Очікуйте на дзвінок найближчим часом.",
            parse_mode="Markdown",
            reply_markup=None
        )
    except Exception:
        # Если редактирование не прошло (например, из-за фото), отправим новое сообщение
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text="✅ Дякуємо! Ваше замовлення в обробці. Очікуйте на дзвінок найближчим часом."
        )

    # Заканчиваем разговор
    user_data.clear()
    return ConversationHandler.END


def cancel_order(update: Update, context: CallbackContext) -> int:
    """
    Пользователь нажал «Скасувати ❌» в финальном сообщении.
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
    Фолбек для /cancel – на случай, если пользователь хочет прервать процесс.
    """
    update.message.reply_text("❌ Ви скасували оформлення замовлення.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END


# -------------------------------------------------------------
#                   Команды для админа
# -------------------------------------------------------------

def admin_help(update: Update, context: CallbackContext):
    """
    Показываем краткую справку по админ-командам.
    """
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
    """
    Отправка сообщения в канал с инлайн-кнопкой.
    """
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
        context.bot.send_message(
            chat_id=CHANNEL_ID, 
            text=message_text,
            reply_markup=markup
        )
        update.message.reply_text("📢 Повідомлення успішно відправлене в канал!")
    except Exception as e:
        logger.error(e)
        update.message.reply_text("Виникла помилка при відправленні повідомлення в канал.")


# -------------------------------------------------------------
#                       Запуск бота
# -------------------------------------------------------------

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # ConversationHandler для оформления заказа
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
            WAITING_CITY_REGION: [
                MessageHandler(Filters.text & ~Filters.command, get_city_region)
            ],
            WAITING_POST_OFFICE: [
                MessageHandler(Filters.text & ~Filters.command, get_post_office)
            ],
            CONFIRM_ORDER: [
                CallbackQueryHandler(confirm_order, pattern="^CONFIRM_ORDER$"),
                CallbackQueryHandler(cancel_order, pattern="^CANCEL_ORDER$")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command)
        ],
        allow_reentry=True
    )
    dp.add_handler(conv_handler)

    # Команды для админа
    dp.add_handler(CommandHandler("help", admin_help))
    dp.add_handler(CommandHandler("send_to_channel", send_to_channel, pass_args=True))

    # Запускаем бота
    updater.start_polling()
    logger.info("Bot started successfully!")
    updater.idle()


if __name__ == "__main__":
    main()
