import logging
from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
)
import os

# Логирование для отладки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ------------------------- Настройки -------------------------
# Токен бота (замените на свой токен)
TOKEN = "7633660729:AAEF7FnE9HO0jfBsJXHRTOznP0s3jiwntPs"

# ID администратора (для уведомления о заказах и проверки прав на команды)
OWNER_ID = 204541083

# ID канала для отправки сообщений (замените на фактический ID или @username канала)
CHANNEL_ID = "@your_channel"  # <--- Замените на свой ID канала
# ----------------------------------------------------------------

# Словарь с продуктами. Ключ – номер продукта (от "1" до "24").
# Для каждого продукта указывается: имя, описание (на украинском с емодзи) и ссылка на изображение.
products = {
    "1": {
        "name": "Крем №1 💖",
        "description": "🌺 Пропозиція №1:\nЦей унікальний крем від Victoria’s Secret забезпечує неймовірне зволоження, ніжну текстуру та розкішний аромат. Насолоджуйтесь доглядом за собою! ✨",
        "image": "https://i.ibb.co/9k8BmxSN/photo-2025-04-15-16-46-14.jpg"
    },
    "2": {
        "name": "Крем №2 🌸",
        "description": "🌷 Пропозиція №2:\nЕксклюзивний лосьйон з натуральними компонентами для сяючої та м’якої шкіри. Відчуйте свіжість та комфорт! 💖",
        "image": "https://i.ibb.co/5X6nDCq4/photo-2025-04-15-16-46-15.jpg"
    },
    "3": {
        "name": "Крем №3 ✨",
        "description": "🌹 Пропозиція №3:\nЦей крем дарує витонченість та неповторний аромат. Ідеальний вибір для вашого догляду! 💫",
        "image": "https://i.ibb.co/qYHnDZrx/photo-2025-04-15-16-46-13.jpg"
    },
    "4": {
        "name": "Крем №4 💎",
        "description": "💐 Пропозиція №4:\nРозкішна текстура та насичений аромат створять атмосферу розкоші у кожному вашому русі. Насолоджуйтесь! 🌟",
        "image": "https://i.ibb.co/r2wmHsqT/photo-2025-04-15-15-08-33.jpg"
    },
    "5": {
        "name": "Крем №5 🌟",
        "description": "🌼 Пропозиція №5:\nІдеальний баланс між свіжістю та зволоженням. Забезпечте своїй шкірі неповторну м’якість! 💕",
        "image": "https://i.ibb.co/1Y98rzQ6/photo-2025-04-15-15-08-27.jpg"
    },
    "6": {
        "name": "Крем №6 💐",
        "description": "🌸 Пропозиція №6:\nРозкішний догляд і аромат, які надихають на красу. Відчуйте ніжність у кожному доторку! ✨",
        "image": "https://i.ibb.co/p6rpLtys/photo-2025-04-15-15-08-22-2.jpg"
    },
    "7": {
        "name": "Крем №7 🌹",
        "description": "💖 Пропозиція №7:\nНатуральна формула для інтенсивного зволоження та догляду. Розкрийте свою природну красу! 🌟",
        "image": "https://i.ibb.co/wZKsPN71/photo-2025-04-15-15-08-22.jpg"
    },
    "8": {
        "name": "Крем №8 🌼",
        "description": "🌷 Пропозиція №8:\nЛегкий крем для сяючої та доглянутої шкіри. Оригінальний аромат для впевненості в собі! 💫",
        "image": "https://i.ibb.co/HL97djJX/photo-2025-04-15-15-08-21-2.jpg"
    },
    "9": {
        "name": "Крем №9 ✨",
        "description": "💐 Пропозиція №9:\nЕлегантність і дотик розкоші. Зволоження та живлення, які надовго залишаться з вами! 🌟",
        "image": "https://i.ibb.co/bRdsf7wN/photo-2025-04-15-15-08-21.jpg"
    },
    "10": {
        "name": "Крем №10 💎",
        "description": "🌺 Пропозиція №10:\nІнноваційна формула та розкішний аромат – все для вашої неповторності! 💖",
        "image": "https://i.ibb.co/sdDmQmqN/photo-2025-04-15-15-08-20-2.jpg"
    },
    "11": {
        "name": "Крем №11 🌸",
        "description": "🌹 Пропозиція №11:\nСтворений для тих, хто цінує якісний догляд. Зволоження, живлення та неповторний аромат! ✨",
        "image": "https://i.ibb.co/KcNhVvK4/photo-2025-04-15-15-08-20.jpg"
    },
    "12": {
        "name": "Крем №12 💖",
        "description": "💐 Пропозиція №12:\nНіжність і ефективність, втілені в одному продукті. Розкішний догляд для вашої шкіри! 🌟",
        "image": "https://i.ibb.co/Mx9J3CYN/photo-2025-04-15-15-08-19.jpg"
    },
    "13": {
        "name": "Крем №13 ✨",
        "description": "🌺 Пропозиція №13:\nУнікальна формула для інтенсивного зволоження та відновлення. Подаруйте своїй шкірі турботу! 💖",
        "image": "https://i.ibb.co/r2J0CXgm/photo-2025-04-15-15-08-18-2.jpg"
    },
    "14": {
        "name": "Крем №14 🌟",
        "description": "🌷 Пропозиція №14:\nЕксклюзивний догляд і натуральні компоненти забезпечують незрівнянний ефект. Насолоджуйтесь красою! ✨",
        "image": "https://i.ibb.co/cXtXDGWC/photo-2025-04-15-15-08-18.jpg"
    },
    "15": {
        "name": "Крем №15 💐",
        "description": "🌹 Пропозиція №15:\nФормула, розроблена з думкою про вас – для сяючої, доглянутої та здорової шкіри! 💖",
        "image": "https://i.ibb.co/b4y9SHy/photo-2025-04-15-15-08-17.jpg"
    },
    "16": {
        "name": "Крем №16 ✨",
        "description": "🌸 Пропозиція №16:\nІдеальний вибір для ніжного догляду – інтенсивне зволоження та розкішний аромат у кожній краплі! 🌟",
        "image": "https://i.ibb.co/KcGGjcHs/photo-2025-04-15-15-12-19-2.jpg"
    },
    "17": {
        "name": "Крем №17 💎",
        "description": "💐 Пропозиція №17:\nВисокоякісний продукт для витонченої шкіри. Дбайливо підібрані інгредієнти для вашого комфорту! ✨",
        "image": "https://i.ibb.co/4whM3CBj/photo-2025-04-15-15-12-19.jpg"
    },
    "18": {
        "name": "Крем №18 🌺",
        "description": "🌷 Пропозиція №18:\nЛегкість текстури та насиченість аромату створюють справжнє відчуття розкоші. Спробуйте вже сьогодні! 💖",
        "image": "https://i.ibb.co/ccfr76k4/photo-2025-04-15-15-12-18-2.jpg"
    },
    "19": {
        "name": "Крем №19 🌟",
        "description": "🌹 Пропозиція №19:\nНатуральний догляд, що дарує свіжість та енергію. Ваш секрет неповторної краси! ✨",
        "image": "https://i.ibb.co/0yJxwb5b/photo-2025-04-15-15-12-18.jpg"
    },
    "20": {
        "name": "Крем №20 💖",
        "description": "💐 Пропозиція №20:\nСтворений для тих, хто цінує натуральну красу. Інтенсивне зволоження та догляд, якого ви заслуговуєте! 🌟",
        "image": "https://i.ibb.co/qvTCHVV/photo-2025-04-15-15-12-17.jpg"
    },
    "21": {
        "name": "Крем №21 ✨",
        "description": "🌸 Пропозиція №21:\nІдеальна текстура та багатий аромат для справжнього релаксу. Подаруйте своїй шкірі краще! 💖",
        "image": "https://i.ibb.co/nMb7BfJb/photo-2025-04-15-15-12-16-2.jpg"
    },
    "22": {
        "name": "Крем №22 🌺",
        "description": "🌷 Пропозиція №22:\nДбайливо створений продукт для глибокого зволоження та живлення. Насолоджуйтесь кожним моментом! ✨",
        "image": "https://i.ibb.co/bMcQSsLv/photo-2025-04-15-15-12-16.jpg"
    },
    "23": {
        "name": "Крем №23 💎",
        "description": "💐 Пропозиція №23:\nРозкішний догляд, що дарує свіжість і сяйво. Випробуйте магію Victoria’s Secret! 🌟",
        "image": "https://i.ibb.co/N2rqMnHr/photo-2025-04-15-15-12-15.jpg"
    },
    "24": {
        "name": "Крем №24 🌟",
        "description": "🌹 Пропозиція №24:\nФінальний акорд вашого догляду – цей крем подарує шкірі неймовірну м’якість та розкішний аромат. 💖",
        "image": "https://i.ibb.co/YFFmL2WZ/photo-2025-04-15-15-12-14.jpg"
    },
}

# Функція, що формує головне привітальне повідомлення та клавіатуру з переліком продуктів
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    welcome_text = (
        "🌟 Вітаємо у світі розкоші та краси Victoria's Secret! 🌟\n\n"
        "Тут ви знайдете оригінальні парфумовані лосьйони та креми з США, які дарують неймовірні відчуття та догляд за шкірою. \n"
        "Обирайте ваш улюблений продукт нижче та зробіть свій день неповторним! 💖✨"
    )
    # Клавіатура з кнопками для кожного продукту – 3 кнопки в рядку
    buttons = []
    row = []
    for idx, prod in enumerate(products.values(), start=1):
        button = InlineKeyboardButton(prod["name"], callback_data=f"PRODUCT_{idx}")
        row.append(button)
        # создаём ряд по 3 кнопки
        if idx % 3 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    reply_markup = InlineKeyboardMarkup(buttons)

    # Відправка привітальної картинки з підписом
    welcome_image = "https://i.ibb.co/cS9WCwrJ/photo-2025-04-14-01-23-29.jpg"
    context.bot.send_photo(chat_id=chat_id, photo=welcome_image, caption=welcome_text, reply_markup=reply_markup)

# Обробка callback – вибір продукту та подальші дії
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data

    # Якщо вибір продукту (PRODUCT_{id})
    if data.startswith("PRODUCT_"):
        prod_id = data.split("_")[1]
        prod = products.get(prod_id)
        if not prod:
            query.edit_message_text("Виникла помилка, спробуйте ще раз.")
            return

        # Формуємо клавіатуру підтвердження замовлення
        keyboard = [
            [
                InlineKeyboardButton("Замовити ✅", callback_data=f"ORDER_{prod_id}"),
                InlineKeyboardButton("Скасувати ❌", callback_data="CANCEL"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = f"🛍 {prod['name']}\n\n{prod['description']}\n\nОбирайте опцію нижче:"
        # Відправка фото та опису обраного продукту
        context.bot.send_photo(chat_id=query.message.chat_id, photo=prod["image"], caption=text, reply_markup=reply_markup)

    # Якщо підтвердження замовлення (ORDER_{id})
    elif data.startswith("ORDER_"):
        prod_id = data.split("_")[1]
        prod = products.get(prod_id)
        if not prod:
            query.edit_message_text("Виникла помилка, спробуйте ще раз.")
            return
        user = update.effective_user
        # Формуємо повідомлення з даними замовлення для адміністратора
        order_msg = (
            f"🛒 **Нове замовлення!**\n\n"
            f"Продукт: {prod['name']}\n"
            f"Замовник: {user.full_name}"
        )
        if user.username:
            order_msg += f" (@{user.username})"
        order_msg += f"\nID користувача: {user.id}\n"
        # Відправка повідомлення адміністратору (без збереження даних)
        context.bot.send_message(chat_id=OWNER_ID, text=order_msg, parse_mode="Markdown")
        query.edit_message_caption(caption=f"✅ Ваше замовлення прийняте! Ми зв'яжемося з вами найближчим часом.")
    
    # Якщо користувач скасовує дію
    elif data == "CANCEL":
        query.edit_message_caption(caption="❌ Замовлення скасовано.")
    else:
        query.edit_message_text("Невідома дія.")

# Обробник команди для розсилки повідомлення в канал
def send_to_channel(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id != OWNER_ID:
        update.message.reply_text("⚠️ Ви не маєте прав доступу до цієї команди.")
        return

    # Очікуємо текст повідомлення як аргументи команди
    if not context.args:
        update.message.reply_text("Будь ласка, введіть текст повідомлення після команди /send_to_channel")
        return

    message_text = " ".join(context.args)
    # Створюємо inline кнопку з посиланням (змініть URL на потрібний)
    button = InlineKeyboardButton("Перейти ➡️", url="https://t.me/YOUR_BOT_USERNAME")
    markup = InlineKeyboardMarkup([[button]])
    try:
        context.bot.send_message(chat_id=CHANNEL_ID, text=message_text, reply_markup=markup)
        update.message.reply_text("📢 Повідомлення відправлене в канал!")
    except Exception as e:
        logger.error(e)
        update.message.reply_text("Виникла помилка при відправці повідомлення в канал.")

def main():
    # Створення апдейтера і диспетчера
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    # Обробники команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("send_to_channel", send_to_channel, pass_args=True))

    # Обробник callback для inline кнопок
    dp.add_handler(CallbackQueryHandler(button_handler))

    # Запуск бота
    updater.start_polling()
    logger.info("Бот запущений!")
    updater.idle()

if __name__ == '__main__':
    main()
