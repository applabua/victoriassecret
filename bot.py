import os
import logging
import time
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from googletrans import Translator

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Встановлені значення (задані «напряму»)
TELEGRAM_TOKEN = "7633660729:AAEF7FnE9HO0jfBsJXHRTOznP0s3jiwntPs"
HEROKU_APP_NAME = "victoriassecret"  # назва додатку Heroku (без домену)
ADMIN_ID = 2045410830

# Глобальний словник із товарами (без ціни, текст українською)
products = {
    "lotion1": {
        "name": "Лосьйон для тіла з ароматом квітів",
        "description": (
            "Цей ніжний лосьйон з натуральними екстрактами та ароматом свіжих квітів "
            "забезпечує зволоження та живлення шкіри."
        ),
        "image": "images/lotion1.jpg",
    },
    "lotion2": {
        "name": "Лосьйон для тіла з ароматом ванілі",
        "description": (
            "Розкішний лосьйон з нотками ванілі дарує відчуття комфорту та забезпечує "
            "м'якість шкіри."
        ),
        "image": "images/lotion2.jpg",
    },
    # Додайте інші товари за потреби
}

# Стан діалогу для оформлення замовлення
ORDER_DETAILS = 1

#####################################
# 1. Функція для скрейпінгу даних
#####################################
def scrape_products():
    """
    Завантажує сторінку з товарами з сайту Victoria’s Secret, парсить HTML для отримання назв, описів
    та URL зображень, перекладає інформацію на українську та зберігає зображення в папку 'images'.
    
    За потреби скорегуйте селектори відповідно до структури сторінки.
    
    **Увага:** Для роботи Selenium в headless‑режимі на Heroku потрібно додаткове налаштування.
    """
    url = "https://www.victoriassecret.com/us/vs/beauty/body-lotions-and-moisturizers?scroll=true"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(5)  # Чекаємо, поки сторінка завантажиться
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    translator = Translator()

    if not os.path.exists("images"):
        os.makedirs("images")

    scraped_products = {}
    product_elements = soup.find_all("div", class_="product-tile")
    if not product_elements:
        logger.info("Не знайдено елементів товарів. Перевірте селектори!")

    for idx, elem in enumerate(product_elements, start=1):
        try:
            name_tag = elem.find("span", class_="product-name")
            name = name_tag.get_text(strip=True) if name_tag else f"Product {idx}"
            description = "Опис не надано."

            image_tag = elem.find("img")
            image_url = image_tag["src"] if image_tag and image_tag.has_attr("src") else None

            # Переклад на українську
            translated_name = translator.translate(name, dest="uk").text
            translated_description = translator.translate(description, dest="uk").text

            image_filename = ""
            if image_url:
                response = requests.get(image_url)
                image_filename = f"images/product_{idx}.jpg"
                with open(image_filename, "wb") as f:
                    f.write(response.content)
            else:
                image_filename = "images/no_image.jpg"

            product_key = f"lotion{idx}"
            scraped_products[product_key] = {
                "name": translated_name,
                "description": translated_description,
                "image": image_filename,
            }
            logger.info(f"Оброблено товар: {translated_name}")
        except Exception as e:
            logger.error(f"Помилка при обробці товару {idx}: {e}")
    return scraped_products

###############################################
# 2. Асинхронні хендлери Telegram-бота
###############################################

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /start - виводить список товарів з кнопками для перегляду деталей.
    """
    keyboard = [
        [InlineKeyboardButton(data["name"], callback_data=f"view_{pid}")]
        for pid, data in products.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(
            "Ласкаво просимо!\nОберіть лосьйон для перегляду деталей:", reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "Ласкаво просимо!\nОберіть лосьйон для перегляду деталей:", reply_markup=reply_markup
        )

async def view_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Відправляє деталі обраного товару (зображення та опис) із кнопкою «Замовити».
    """
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("view_"):
        product_id = data.split("_", 1)[1]
        product = products.get(product_id)
        if product:
            keyboard = [[InlineKeyboardButton("Замовити", callback_data=f"order_{product_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                with open(product["image"], "rb") as photo_file:
                    await query.message.reply_photo(
                        photo=photo_file,
                        caption=f"*{product['name']}*\n\n{product['description']}",
                        parse_mode="Markdown",
                        reply_markup=reply_markup,
                    )
            except Exception as e:
                logger.error(f"Помилка відправки фото: {e}")
                await query.message.reply_text("Не вдалося завантажити зображення товару.")
        else:
            await query.message.reply_text("Товар не знайдено.")

async def order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробляє вибір кнопки «Замовити» і запитує контактну інформацію.
    """
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("order_"):
        product_id = data.split("_", 1)[1]
        product = products.get(product_id)
        if product:
            context.user_data["order_product_id"] = product_id
            await query.message.reply_text(
                f"Ви обрали товар: {product['name']}\n\n"
                "Введіть вашу контактну інформацію (номер телефону, email, адресу тощо):"
            )
            return ORDER_DETAILS
    await query.message.reply_text("Сталася помилка. Будь ласка, спробуйте ще раз.")
    return ConversationHandler.END

async def order_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отримує контактну інформацію користувача, формує повідомлення з замовленням і пересилає адміну.
    """
    user_contact = update.message.text
    product_id = context.user_data.get("order_product_id")
    product = products.get(product_id)
    user = update.effective_user
    order_info = (
        "Нове замовлення!\n\n"
        f"Продукт: {product['name']}\n"
        f"Контактна інформація: {user_contact}\n"
        f"Користувач: {user.first_name} (ID: {user.id})"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=order_info)
    await update.message.reply_text("Ваше замовлення отримано! З вами зв’яжуться найближчим часом.")
    context.user_data.pop("order_product_id", None)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /cancel для скасування замовлення.
    """
    await update.message.reply_text("Замовлення скасовано.")
    return ConversationHandler.END

#################################################
# 3. Функція запуску бота: режим webhook для Heroku
#################################################
def main():
    # Якщо бажаєте оновити продукти за допомогою скрейпінгу, розкоментуйте наступні рядки:
    # global products
    # products = scrape_products()

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Налаштовуємо ConversationHandler для оформлення замовлення
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(order_callback, pattern=r"^order_")],
        states={
            ORDER_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_details)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(view_product_callback, pattern=r"^view_"))
    application.add_handler(conv_handler)

    # Налаштування запуску
    PORT = int(os.environ.get("PORT", "8443"))
    # Якщо HEROKU_APP_NAME задана, запускаємо через webhook (Heroku), інакше – polling (локально)
    if HEROKU_APP_NAME:
        # Формуємо URL для webhook-а, наприклад: https://victoriassecret.herokuapp.com/<TELEGRAM_TOKEN>
        WEBHOOK_URL = f"https://{HEROKU_APP_NAME}.herokuapp.com/{TELEGRAM_TOKEN}"
        logger.info(f"Запуск у режимі webhook за URL: {WEBHOOK_URL}")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TELEGRAM_TOKEN,
            webhook_url=WEBHOOK_URL,
        )
    else:
        logger.info("Запуск у режимі polling")
        application.run_polling()

if __name__ == "__main__":
    main()
