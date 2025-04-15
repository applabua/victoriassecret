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

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ------------------------- Налаштування -------------------------
TOKEN = "7633660729:AAEF7FnE9HO0jfBsJXHRTOznP0s3jiwntPs"  # Токен бота
OWNER_ID = 204541083  # ID адміністратора
CHANNEL_ID = "@your_channel"  # Замініть на свій ID або @username каналу
# -----------------------------------------------------------------

# Оновлений каталог продуктів (24 позиції) із реальними назвами та описами
products = {
    "1": {
        "name": "Зволожуючий крем Bombshell 💖",
        "description": (
            "💧 **Bombshell** – крем, що дарує глибоке зволоження, ніжну текстуру та неповторний аромат, "
            "який робить вашу шкіру сяючою та привабливою!"
        ),
        "image": "https://i.ibb.co/9k8BmxSN/photo-2025-04-15-16-46-14.jpg"
    },
    "2": {
        "name": "Ніжний лосьйон Tease 🌸",
        "description": (
            "🌺 **Tease** – легкий лосьйон для щоденного догляду, який забезпечує свіжість та м’якість шкіри, "
            "додаючи впевненості у вашому стилі!"
        ),
        "image": "https://i.ibb.co/5X6nDCq4/photo-2025-04-15-16-46-15.jpg"
    },
    "3": {
        "name": "Шовковий крем Seduction ✨",
        "description": (
            "🌹 **Seduction** – крем з насиченою текстурою, що дарує шовкову гладкість та делікатний аромат, "
            "який зачаровує кожного!"
        ),
        "image": "https://i.ibb.co/qYHnDZrx/photo-2025-04-15-16-46-13.jpg"
    },
    "4": {
        "name": "Містичний крем Dreamy Glow 💎",
        "description": (
            "🌟 **Dreamy Glow** – крем, створений для сяйва та рівномірного відтінку шкіри, який підкреслює "
            "вашу природну красу!"
        ),
        "image": "https://i.ibb.co/r2wmHsqT/photo-2025-04-15-15-08-33.jpg"
    },
    "5": {
        "name": "Розкішний крем Luscious Body 🌟",
        "description": (
            "💖 **Luscious Body** – інтенсивне живлення та відновлення шкіри для відчуття справжньої розкоші!"
        ),
        "image": "https://i.ibb.co/1Y98rzQ6/photo-2025-04-15-15-08-27.jpg"
    },
    "6": {
        "name": "Лосьйон Velvet Touch 🌼",
        "description": (
            "💐 **Velvet Touch** – ніжний лосьйон, що дарує м’якість та комфорт, залишаючи приємний аромат на шкірі!"
        ),
        "image": "https://i.ibb.co/p6rpLtys/photo-2025-04-15-15-08-22-2.jpg"
    },
    "7": {
        "name": "Крем Charm Essence 🌺",
        "description": (
            "🌷 **Charm Essence** – утончений крем, наповнений життям та енергією завдяки своїй легкій текстурі "
            "та свіжому аромату!"
        ),
        "image": "https://i.ibb.co/wZKsPN71/photo-2025-04-15-15-08-22.jpg"
    },
    "8": {
        "name": "Лосьйон Glamour Radiance 💫",
        "description": (
            "✨ **Glamour Radiance** – лосьйон, який дарує шкірі сяйво та розкішний вигляд, підкреслюючи вашу індивідуальність!"
        ),
        "image": "https://i.ibb.co/HL97djJX/photo-2025-04-15-15-08-21-2.jpg"
    },
    "9": {
        "name": "Крем Mystic Moisture 💧",
        "description": (
            "🌹 **Mystic Moisture** – крем, що дарує глибоке зволоження та робить вашу шкіру неймовірно м’якою і гладкою!"
        ),
        "image": "https://i.ibb.co/bRdsf7wN/photo-2025-04-15-15-08-21.jpg"
    },
    "10": {
        "name": "Крем Delightful Dusk 🌙",
        "description": (
            "💖 **Delightful Dusk** – крем для інтенсивного відновлення, що забезпечує ніжний догляд і ексклюзивний аромат для вечора!"
        ),
        "image": "https://i.ibb.co/sdDmQmqN/photo-2025-04-15-15-08-20-2.jpg"
    },
    "11": {
        "name": "Крем Enchanted Velvet ✨",
        "description": (
            "💎 **Enchanted Velvet** – відчуйте магію догляду з кремом, який дарує шовковисту м’якість та сяйво вашій шкірі!"
        ),
        "image": "https://i.ibb.co/KcNhVvK4/photo-2025-04-15-15-08-20.jpg"
    },
    "12": {
        "name": "Лосьйон Pure Elegance 💫",
        "description": (
            "🌸 **Pure Elegance** – ідеальний баланс між ніжністю та живленням, що забезпечує свіжість і неповторну елегантність!"
        ),
        "image": "https://i.ibb.co/Mx9J3CYN/photo-2025-04-15-15-08-19.jpg"
    },
    "13": {
        "name": "Крем Opulent Glow 🌟",
        "description": (
            "💐 **Opulent Glow** – крем, що підкреслює вашу природну красу, даруючи глибоке зволоження та ефектний блиск!"
        ),
        "image": "https://i.ibb.co/r2J0CXgm/photo-2025-04-15-15-08-18-2.jpg"
    },
    "14": {
        "name": "Крем Divine Nectar 🍯",
        "description": (
            "🌹 **Divine Nectar** – розкішний крем, натхненний природними компонентами для ексклюзивного догляду за шкірою!"
        ),
        "image": "https://i.ibb.co/cXtXDGWC/photo-2025-04-15-15-08-18.jpg"
    },
    "15": {
        "name": "Лосьйон Soft Whisper 🌬",
        "description": (
            "💖 **Soft Whisper** – легкий лосьйон, що дарує свіжість і делікатний аромат, як тихий шепіт весни!"
        ),
        "image": "https://i.ibb.co/b4y9SHy/photo-2025-04-15-15-08-17.jpg"
    },
    "16": {
        "name": "Крем Radiant Charm ✨",
        "description": (
            "🌟 **Radiant Charm** – крем для ефективного зволоження, який дарує вашій шкірі неймовірне сяйво та чарівність!"
        ),
        "image": "https://i.ibb.co/KcGGjcHs/photo-2025-04-15-15-12-19-2.jpg"
    },
    "17": {
        "name": "Крем Secret Allure 💎",
        "description": (
            "🌺 **Secret Allure** – витончений крем, який підкреслює вашу індивідуальність та додає магнетизму зовнішності!"
        ),
        "image": "https://i.ibb.co/4whM3CBj/photo-2025-04-15-15-12-19.jpg"
    },
    "18": {
        "name": "Лосьйон Satin Bliss 🌼",
        "description": (
            "🌷 **Satin Bliss** – ніжний лосьйон, що забезпечує доглянутость шкіри і дарує відчуття шовковистої розкоші!"
        ),
        "image": "https://i.ibb.co/ccfr76k4/photo-2025-04-15-15-12-18-2.jpg"
    },
    "19": {
        "name": "Небесний крем Celestial 💫",
        "description": (
            "💐 **Celestial** – крем, що дарує неземну легкість, зволоження та сяйво, створюючи відчуття чистоти кожного дня!"
        ),
        "image": "https://i.ibb.co/0yJxwb5b/photo-2025-04-15-15-12-18.jpg"
    },
    "20": {
        "name": "Крем Orchid Dream 🌸",
        "description": (
            "✨ **Orchid Dream** – насичений крем з делікатним ароматом орхідеї для ніжного та ефективного догляду!"
        ),
        "image": "https://i.ibb.co/qvTCHVV/photo-2025-04-15-15-12-17.jpg"
    },
    "21": {
        "name": "Лосьйон Serene Touch 🌹",
        "description": (
            "💖 **Serene Touch** – лосьйон, що дарує спокій та свіжість, збагачуючи шкіру вітамінами та зволоженням!"
        ),
        "image": "https://i.ibb.co/nMb7BfJb/photo-2025-04-15-15-12-16-2.jpg"
    },
    "22": {
        "name": "Крем Mystical Silk ✨",
        "description": (
            "🌟 **Mystical Silk** – крем для витонченої шкіри, що дарує розкішну гладкість та незабутній аромат!"
        ),
        "image": "https://i.ibb.co/bMcQSsLv/photo-2025-04-15-15-12-16.jpg"
    },
    "23": {
        "name": "Крем Eternal Grace 💫",
        "description": (
            "💎 **Eternal Grace** – крем, який поєднує інтенсивне живлення з елегантністю, залишаючи шкіру неймовірно м’якою!"
        ),
        "image": "https://i.ibb.co/N2rqMnHr/photo-2025-04-15-15-12-15.jpg"
    },
    "24": {
        "name": "Крем Velvet Enigma 🌙",
        "description": (
            "🌹 **Velvet Enigma** – розкішний крем, що окутує шкіру таємничою ніжністю, даруючи неповторне сяйво!"
        ),
        "image": "https://i.ibb.co/YFFmL2WZ/photo-2025-04-15-15-12-14.jpg"
    },
}

# Функція для відправки привітального повідомлення зі зображенням та клавіатурою вибору товарів
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    welcome_text = (
        "🌟 Вітаємо у світі розкоші та краси Victoria's Secret! 🌟\n\n"
        "Тут ви знайдете оригінальні парфумовані лосьйони та креми з США, які дарують неповторні відчуття та догляд за шкірою. \n"
        "Обирайте свій улюблений продукт нижче та зробіть свій день особливим! 💖✨"
    )
    # Формування кнопок – по 3 в рядку
    buttons = []
    row = []
    for idx, prod in enumerate(products.values(), start=1):
        btn = InlineKeyboardButton(prod["name"], callback_data=f"PRODUCT_{idx}")
        row.append(btn)
        if idx % 3 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    reply_markup = InlineKeyboardMarkup(buttons)
    
    welcome_image = "https://i.ibb.co/cS9WCwrJ/photo-2025-04-14-01-23-29.jpg"
    context.bot.send_photo(chat_id=chat_id, photo=welcome_image, caption=welcome_text, reply_markup=reply_markup)

# Обробка callback – вибір товару, показ опису та замовлення
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data

    if data.startswith("PRODUCT_"):
        prod_id = data.split("_")[1]
        prod = products.get(prod_id)
        if not prod:
            query.edit_message_text("Виникла помилка, спробуйте ще раз.")
            return

        # Клавіатура для підтвердження замовлення
        keyboard = [
            [
                InlineKeyboardButton("Замовити ✅", callback_data=f"ORDER_{prod_id}"),
                InlineKeyboardButton("Скасувати ❌", callback_data="CANCEL"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = f"🛍 **{prod['name']}**\n\n{prod['description']}\n\nОбирайте опцію нижче:"
        context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=prod["image"],
            caption=text,
            reply_markup=reply_markup
        )

    elif data.startswith("ORDER_"):
        prod_id = data.split("_")[1]
        prod = products.get(prod_id)
        if not prod:
            query.edit_message_text("Виникла помилка, спробуйте ще раз.")
            return

        user = update.effective_user
        order_msg = (
            f"🛒 **Нове замовлення!**\n\n"
            f"Продукт: {prod['name']}\n"
            f"Замовник: {user.full_name}"
        )
        if user.username:
            order_msg += f" (@{user.username})"
        order_msg += f"\nID користувача: {user.id}\n"
        context.bot.send_message(chat_id=OWNER_ID, text=order_msg, parse_mode="Markdown")
        
        # Спроба оновити повідомлення із зображенням – видаляємо inline клавіатуру та оновлюємо підпис;
        # якщо редагування не проходить, відправляємо окреме повідомлення
        try:
            query.edit_message_caption(
                caption="✅ Ваше замовлення прийняте! Ми зв'яжемося з вами найближчим часом.",
                reply_markup=None
            )
        except Exception as e:
            logger.error(e)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="✅ Ваше замовлення прийняте! Ми зв'яжемося з вами найближчим часом.")

    elif data == "CANCEL":
        try:
            query.edit_message_caption(
                caption="❌ Замовлення скасовано.",
                reply_markup=None
            )
        except Exception as e:
            logger.error(e)
            context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Замовлення скасовано.")
    else:
        query.edit_message_text("Невідома дія.")

# Команда для розсилки повідомлення в канал (тільки для адміністратора)
def send_to_channel(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id != OWNER_ID:
        update.message.reply_text("⚠️ Ви не маєте прав доступу до цієї команди.")
        return

    if not context.args:
        update.message.reply_text("Будь ласка, введіть текст повідомлення після команди /send_to_channel")
        return

    message_text = " ".join(context.args)
    button = InlineKeyboardButton("Перейти ➡️", url="https://t.me/YOUR_BOT_USERNAME")
    markup = InlineKeyboardMarkup([[button]])
    try:
        context.bot.send_message(chat_id=CHANNEL_ID, text=message_text, reply_markup=markup)
        update.message.reply_text("📢 Повідомлення відправлене в канал!")
    except Exception as e:
        logger.error(e)
        update.message.reply_text("Виникла помилка при відправці повідомлення в канал.")

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("send_to_channel", send_to_channel, pass_args=True))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    logger.info("Бот запущений!")
    updater.idle()

if __name__ == '__main__':
    main()
