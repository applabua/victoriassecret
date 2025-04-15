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
OWNER_ID = 2045410830
CHANNEL_ID = "@your_channel"  # Замените на нужный ID или @username канала
# -------------------------------------------------------------

# Стадии диалога:
# CHOOSING_PRODUCT – выбор товара из меню;
# WAITING_PHONE_NAME – ввод телефона и имени;
# WAITING_ADDRESS – ввод адреса доставки;
# CONFIRM_ORDER – финальное подтверждение заказа.
CHOOSING_PRODUCT, WAITING_PHONE_NAME, WAITING_ADDRESS, CONFIRM_ORDER = range(4)

# Обновленный каталог ароматов (23 позиции)
products = {
    "1": {
        "name": "1️⃣ Ginger Apple Jewel 🍏🌿",
        "description": (
            "Свіжий аромат, що відкривається іскристим яблуком та пряними відтінками.\n"
            "Ідеально збалансований, яскравий і з характером, який хочеться носити знову і знову.\n"
            "🔹 Ноти: запашне яблуко, ледь відчутний імбир, легкий деревний акцент"
        ),
        "image": "https://i.ibb.co/9k8BmxSN/photo-2025-04-15-16-46-14.jpg"
    },
    "2": {
        "name": "2️⃣ Pure Seduction Bliss 💬🍑🌸",
        "description": (
            "Аромат для романтичних моментів. Соковита слива поєднується з пелюстками жасмину — звучить м’яко, жіночно та привабливо.\n"
            "🔹 Ноти: ніжна слива, повітряний жасмин"
        ),
        "image": "https://i.ibb.co/5X6nDCq4/photo-2025-04-15-16-46-15.jpg"
    },
    "3": {
        "name": "3️⃣ Toasted Amber 🔥🧡",
        "description": (
            "Глибокий та затишний аромат із нотками спецій та теплого бурштину.\n"
            "Ніжний шлейф залишає відчуття комфорту й загадковості.\n"
            "🔹 Ноти: ледь помітний перець, золотистий бурштин"
        ),
        "image": "https://i.ibb.co/qYHnDZrx/photo-2025-04-15-16-46-13.jpg"
    },
    "4": {
        "name": "4️⃣ Love Spell Daydream ☁️🍇💫",
        "description": (
            "Ягідно-квітковий аромат із легким шипінням іскристого шампанського.\n"
            "Ніжний, мрійливий, делікатно солодкий.\n"
            "🔹 Ноти: повітряні ягоди, білий жасмин, солодкий мускус"
        ),
        "image": "https://i.ibb.co/r2wmHsqT/photo-2025-04-15-15-08-33.jpg"
    },
    "5": {
        "name": "5️⃣ Pomegranate Rose 🌹🍷",
        "description": (
            "Витончене поєднання пелюсток троянди та граната, що огортає ароматом жіночності та гармонії.\n"
            "🔹 Ноти: оксамитова троянда, гранатовий сік, акцент деревної свіжості"
        ),
        "image": "https://i.ibb.co/1Y98rzQ6/photo-2025-04-15-15-08-27.jpg"
    },
    "6": {
        "name": "6️⃣ Citrus Lily 🍋🌼",
        "description": (
            "Світлий і позитивний аромат. Поєднує цитрусову іскру з м’якістю білих квітів.\n"
            "Піднімає настрій і створює відчуття чистоти.\n"
            "🔹 Ноти: соковитий цитрус, ніжна лілія, краплі жасмину"
        ),
        "image": "https://i.ibb.co/p6rpLtys/photo-2025-04-15-15-08-22-2.jpg"
    },
    "7": {
        "name": "7️⃣ Bare Vanilla Bliss 🍦🌺",
        "description": (
            "Теплий і м’який, як обійми. Ванільна солодкість поєднується з пелюстками фіалки та орхідеї.\n"
            "🔹 Ноти: ванільний крем, фіалкові пелюстки, квітка орхідеї"
        ),
        "image": "https://i.ibb.co/wZKsPN71/photo-2025-04-15-15-08-22.jpg"
    },
    "8": {
        "name": "8️⃣ Love Spell Bliss 🌸🍑",
        "description": (
            "Легкий та грайливий аромат із квітами, що пахнуть сонцем, та м’якою бавовною.\n"
            "Ніжний, природний, привабливий.\n"
            "🔹 Ноти: жимолость, бавовняна пелюстка"
        ),
        "image": "https://i.ibb.co/HL97djJX/photo-2025-04-15-15-08-21-2.jpg"
    },
    "9": {
        "name": "9️⃣ Velvet Petals Bliss 💗🌷",
        "description": (
            "М’які квіти, огорнуті кремовою ніжністю. Аромат делікатний, як пудровий поцілунок.\n"
            "🔹 Ноти: шовкова фрезія, ніжна лілія"
        ),
        "image": "https://i.ibb.co/bRdsf7wN/photo-2025-04-15-15-08-21.jpg"
    },
    "10": {
        "name": "🔟 Coconut Passion Bliss 🥥🌴",
        "description": (
            "Мрія про тропіки — аромат, що переносить вас на узбережжя сонячних пляжів.\n"
            "🔹 Ноти: кокос, морський бриз, легкий акорд ванілі"
        ),
        "image": "https://i.ibb.co/sdDmQmqN/photo-2025-04-15-15-08-20-2.jpg"
    },
    "11": {
        "name": "1️⃣1️⃣ Bare Vanilla Daydream 🍦🌳🌫️",
        "description": (
            "М'який аромат з нотами ванілі та сандалу, що створює атмосферу спокою та гармонії.\n"
            "🔹 Ноти: ваніль, сандал, легка прохолода"
        ),
        "image": "https://i.ibb.co/KcNhVvK4/photo-2025-04-15-15-08-20.jpg"
    },
    "12": {
        "name": "1️⃣2️⃣ Pure Seduction Daydream 🍭🌸☁️",
        "description": (
            "Солодкий аромат з нотами вершкового цукру та замші, що дарує відчуття ніжності та комфорту.\n"
            "🔹 Ноти: вершковий цукор, біла замша"
        ),
        "image": "https://i.ibb.co/Mx9J3CYN/photo-2025-04-15-15-08-19.jpg"
    },
    "13": {
        "name": "1️⃣3️⃣ Velvet Petals Daydream 🌸🍮☕",
        "description": (
            "Квітковий аромат з нотами крему та кави, що створює атмосферу затишку та тепла.\n"
            "🔹 Ноти: квіти, крем, кава"
        ),
        "image": "https://i.ibb.co/r2J0CXgm/photo-2025-04-15-15-08-18-2.jpg"
    },
    "14": {
        "name": "1️⃣4️⃣ Coconut Passion 🥥🔥🌴",
        "description": (
            "Солодкий аромат з нотами кокосу та ванілі, що переносить у тропічний рай.\n"
            "🔹 Ноти: кокос, ваніль, лілія"
        ),
        "image": "https://i.ibb.co/cXtXDGWC/photo-2025-04-15-15-08-18.jpg"
    },
    "15": {
        "name": "1️⃣5️⃣ Amber Romance 🍒🍮🌳",
        "description": (
            "Теплий аромат з нотами черешні, ванілі та сандалу, що створює атмосферу романтики та затишку.\n"
            "🔹 Ноти: черешня, ваніль, сандал"
        ),
        "image": "https://i.ibb.co/1Y98rzQ6/photo-2025-04-15-15-08-27.jpg"
    },
    "16": {
        "name": "1️⃣6️⃣ Strawberries & Champagne 🍓🥂✨",
        "description": (
            "Свіжий аромат з нотами полуниці та шампанського, що створює святковий настрій.\n"
            "🔹 Ноти: полуниця, шампанське"
        ),
        "image": "https://i.ibb.co/HL97djJX/photo-2025-04-15-15-08-21-2.jpg"
    },
    "17": {
        "name": "1️⃣7️⃣ Love Spell 🌸🍑🍒",
        "description": (
            "Аромат, що поєднує вишневий цвіт і соковитий персик, створюючи коктейль чарівності та флірту.\n"
            "🔹 Ноти: вишневий цвіт, стиглий персик, солодкий нектар"
        ),
        "image": "https://i.ibb.co/r2J0CXgm/photo-2025-04-15-15-08-18-2.jpg"
    },
    "18": {
        "name": "1️⃣8️⃣ Pear Glacé 🍐🍈💧",
        "description": (
            "Свіжий та фруктовий аромат, що дарує легкість та відчуття чистоти.\n"
            "🔹 Ноти: груша, диня, роса"
        ),
        "image": "https://i.ibb.co/4whM3CBj/photo-2025-04-15-15-12-19.jpg"
    },
    "19": {
        "name": "1️⃣9️⃣ Midnight Bloom 🌌🌺💫",
        "description": (
            "Магнетичний аромат з глибокими квітковими нотами, що створює чуттєвий шлейф краси.\n"
            "🔹 Ноти: нічні квіти, пудрова ваніль, легкий мускус"
        ),
        "image": "https://i.ibb.co/0yJxwb5b/photo-2025-04-15-15-12-18.jpg"
    },
    "20": {
        "name": "2️⃣0️⃣ Velvet Petals Bliss 💗🌷💖",
        "description": (
            "Ніжний аромат з квітковими нотами та солодким кремом, що створює атмосферу ніжності та романтики.\n"
            "🔹 Ноти: фрезія, солодкий крем"
        ),
        "image": "https://i.ibb.co/bRdsf7wN/photo-2025-04-15-15-08-21.jpg"
    },
    "21": {
        "name": "2️⃣1️⃣ Aqua Kiss 🌊🌸🍃",
        "description": (
            "Свіжий квітковий аромат з нотами фрезії та маргаритки, що дарує відчуття прохолоди та легкості.\n"
            "🔹 Ноти: фрезія, маргаритка, прохолода листя"
        ),
        "image": "https://i.ibb.co/KcNhVvK4/photo-2025-04-15-15-08-20.jpg"
    },
    "22": {
        "name": "2️⃣2️⃣ Pure Seduction Classic 💋🍑🌸",
        "description": (
            "Класичний аромат, що поєднує соковиту сливу та квіткові ноти для вражаючої спокуси.\n"
            "🔹 Ноти: стигла слива, пелюстки фрезії"
        ),
        "image": "https://i.ibb.co/Mx9J3CYN/photo-2025-04-15-15-08-19.jpg"
    },
    "23": {
        "name": "2️⃣3️⃣ Bare Vanilla Classic 🍦🌰🧶",
        "description": (
            "Легендарний аромат тепла та ніжності, з м’якою ваніллю та делікатним відтінком кашеміру.\n"
            "🔹 Ноти: збита ваніль, кремовий кашемір, делікатна солодкість"
        ),
        "image": "https://i.ibb.co/N2rqMnHr/photo-2025-04-15-15-12-15.jpg"
    },
}

# Функция для генерации меню товаров на нужной странице с навигацией
def get_product_menu(page: int) -> InlineKeyboardMarkup:
    # Сортируем товары по ключу (номер продукта)
    sorted_products = sorted(products.items(), key=lambda x: int(x[0]))
    per_page = 4  # 4 товара на страницу
    total_pages = (len(sorted_products) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    current_products = sorted_products[start:end]
    
    keyboard = []
    for prod_id, prod in current_products:
        btn = InlineKeyboardButton(text=prod["name"], callback_data=f"PRODUCT_{prod_id}")
        keyboard.append([btn])  # Каждая кнопка в отдельном ряду

    # Навигационные кнопки с текстом и стрелками
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
    """
    Выводит приветственное сообщение с красивым текстом и картинкой, а также меню товаров первой страницы.
    """
    chat_id = update.effective_chat.id
    welcome_text = (
        "🌟 Ласкаво просимо до Victoria's Secret! 🌟\n\n"
        "Відкрийте для себе розкішний асортимент оригінальних парфумованих лосьйонів та кремів з США. "
        "Наші продукти допоможуть вам відчути справжню красу і догляд, який ви заслуговуєте!\n\n"
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
    """
    Обрабатывает нажатия навигационных кнопок (PAGE_<номер>) и обновляет меню товаров.
    """
    query = update.callback_query
    query.answer()
    data = query.data  # Формат "PAGE_<номер>"
    page = int(data.split("_")[1])
    context.user_data["current_page"] = page
    try:
        query.edit_message_reply_markup(reply_markup=get_product_menu(page))
    except Exception:
        query.message.reply_text("Оберіть товар:", reply_markup=get_product_menu(page))
    return CHOOSING_PRODUCT

def back_to_menu_handler(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает нажатие кнопки "⬅️ Назад" в карточке товара и возвращает пользователя к приветственному сообщению с картинкой и меню товаров той же страницы.
    """
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
        "Наші продукти допоможуть вам відчути справжню красу і догляд!\n\n"
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
    """
    Обрабатывает выбор товара (callback data "PRODUCT_<id>") и выводит подробное описание с кнопками "Замовити 🛍" и "⬅️ Назад".
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
    """
    При выборе товара "Замовити 🛍" запрашивает у пользователя телефон и имя.
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
    Сохраняет телефон і ім'я, затем запрашивает адрес доставки.
    """
    user_input = update.message.text.strip()
    context.user_data["phone_name"] = user_input

    address_request = (
        "🏤 Введіть, будь ласка, населений пункт, область, номер відділення Нової Пошти або Укрпошти.\n"
        "Наприклад: Київ, Київська область, Нова Пошта, відділення №42"
    )
    update.message.reply_text(address_request, parse_mode="Markdown")
    return WAITING_ADDRESS

def get_address(update: Update, context: CallbackContext) -> int:
    """
    Получает адрес доставки от пользователя и формирует итоговое сообщение с данными заказа.
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
    """
    При підтвердженні замовлення відправляет деталі замовлення адміну (с фото)
    і повідомляє користувача.
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
    Команда /cancel для завершення діалогу.
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
