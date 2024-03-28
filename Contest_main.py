from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import uuid

TOKEN = '##############'
ADMIN_CHAT_ID = 971204608  

def get_base_reply_keyboard():
    keyboard = [
        ['Вернуться в магазин', 'Корзина'],
        ['Тех.поддержка'],  
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    welcome_message = (
        "Привет! Рады приветствовать тебя в нашем магазине. Здесь ты можешь не только заказать вкусные сладости, "
        "но и принять участие в нашем увлекательном конкурсе. Следуй инструкциям ниже, чтобы узнать больше:\n\n"
        "1️⃣ Нажми на кнопку \"Конкурс\", чтобы автоматически добавить участие в корзину и шанс выиграть призы.\n"
        "2️⃣ Хочешь что-то ещё? Исследуй наше меню и добавь в корзину всё, что пожелаешь.\n"
        "3️⃣ Перейди в корзину, чтобы оформить заказ и подтвердить участие в конкурсе.\n"
        "4️⃣ Следуй подсказкам бота для завершения оформления заказа.\n\n"
        "Удачи в конкурсе! Надеемся, ты найдёшь у нас много вкусного и интересного. Если возникнут вопросы, не стесняйся обращаться за помощью."
    )
    sent_message = await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

    context.user_data['message_ids'] = [sent_message.message_id]

    question_message = "Что бы ты хотел заказать?"
    keyboard = [
        [InlineKeyboardButton("🍓Клубника в шоколаде", callback_data='strawberry')],
        [InlineKeyboardButton("🍌Банан в шоколаде", callback_data='banana')],
        [InlineKeyboardButton("🛒Корзина", callback_data='cart')],
        [InlineKeyboardButton("🎁Конкурс", callback_data='competition')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=question_message, reply_markup=reply_markup)

async def handle_competition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Клавиатура для сообщения после участия в конкурсе
    keyboard = [
        [InlineKeyboardButton("🔙 Вернуться в магазин", callback_data='back_to_shop')],
        [InlineKeyboardButton("🛒 Перейти в корзину", callback_data='cart')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    
    if context.user_data.get('has_participated', False):
       
        await query.edit_message_text(
            text="Вы уже участвовали в конкурсе. Участие возможно только один раз.",
            reply_markup=reply_markup
        )
        return


    cart = context.user_data.setdefault('cart', [])
    cart.append("Участие в конкурсе")
    context.user_data['in_competition'] = True  

  
    await query.edit_message_text(
        text="Участие в конкурсе добавлено в корзину. Возвращайтесь в магазин или перейдите в корзину, чтобы оформить заказ.",
        reply_markup=reply_markup
    )


async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id  

    
    if 'message_ids' in context.user_data and len(context.user_data['message_ids']) > 1:
        for msg_id in context.user_data['message_ids'][:-1]:  
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except Exception as e:
                print(f"Ошибка при удалении сообщения: {e}")
        
        context.user_data['message_ids'] = context.user_data['message_ids'][-1:]

    keyboard = [
        [InlineKeyboardButton("🍓Клубника в шоколаде", callback_data='strawberry')],
        [InlineKeyboardButton("🍌Банан в шоколаде", callback_data='banana')],
        [InlineKeyboardButton("🛒Корзина", callback_data='cart')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await context.bot.send_message(chat_id=chat_id, text='Привет! Что бы вы хотели заказать?', reply_markup=reply_markup)

    if 'message_ids' not in context.user_data:
        context.user_data['message_ids'] = [sent_message.message_id]
    else:
        context.user_data['message_ids'].append(sent_message.message_id)


async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Корзина", callback_data='cart')],
        [InlineKeyboardButton("Назад", callback_data='back_to_shop')],
    ]
    if query.data == 'strawberry':
        keyboard[0:0] = [ 
            [InlineKeyboardButton("6 штук", callback_data='strawberry_6')],
            [InlineKeyboardButton("9 штук", callback_data='strawberry_9')],
            [InlineKeyboardButton("16 штук", callback_data='strawberry_16')],
        ]
    elif query.data == 'banana':
        keyboard[0:0] = [  
            [InlineKeyboardButton("3 штуки", callback_data='banana_3')],
            [InlineKeyboardButton("6 штук", callback_data='banana_6')],
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Выберите количество:", reply_markup=reply_markup)


product_descriptions = {
    "strawberry_6": "Клубника в шоколаде 6 штук",
    "strawberry_9": "Клубника в шоколаде 9 штук",
    "strawberry_16": "Клубника в шоколаде 16 штук",
    "banana_3": "Банан в шоколаде 3 штуки",
    "banana_6": "Банан в шоколаде 6 штук",
}

async def handle_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()


    try:
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")

    product_code = query.data
    product_description = product_descriptions.get(product_code, "Неизвестный товар")

    cart = context.user_data.setdefault('cart', [])
    cart.append(product_description)

   
    keyboard = [
        [InlineKeyboardButton("Вернуться в магазин", callback_data='back_to_shop')],
        [InlineKeyboardButton("Корзина", callback_data='cart')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

 
    sent_message = await context.bot.send_message(chat_id=query.message.chat_id, text=f"{product_description} добавлено в корзину.", reply_markup=reply_markup)


    if 'message_ids' not in context.user_data:
        context.user_data['message_ids'] = [sent_message.message_id]
    else:
        context.user_data['message_ids'].append(sent_message.message_id)


async def handle_back_to_shop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    
    try:
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")
    chat_id = query.message.chat_id
    keyboard = [
        [InlineKeyboardButton("🍓Клубника в шоколаде", callback_data='strawberry')],
        [InlineKeyboardButton("🍌Банан в шоколаде", callback_data='banana')],
        [InlineKeyboardButton("🛒Корзина", callback_data='cart')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    sent_message = await context.bot.send_message(chat_id=chat_id, text='Привет! Что бы вы хотели заказать?', reply_markup=reply_markup)
    if 'message_ids' not in context.user_data:
        context.user_data['message_ids'] = [sent_message.message_id]
    else:
        context.user_data['message_ids'].append(sent_message.message_id)


async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cart = context.user_data.get('cart', [])
    if cart:
        cart_items = "\n".join([f"- {item}" for item in cart])
        text = f"Ваша корзина:\n{cart_items}"
        keyboard = [
            [InlineKeyboardButton("Очистить корзину", callback_data='clear_cart')],
            [InlineKeyboardButton("Оформить заказ", callback_data='checkout')],
            [InlineKeyboardButton("Вернуться в магазин", callback_data='back_to_shop')],
        ]
    else:
        text = "Ваша корзина пуста."
        keyboard = [
            [InlineKeyboardButton("Вернуться в магазин", callback_data='back_to_shop')],
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=text, reply_markup=reply_markup)


async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data['cart'] = []
    await query.edit_message_text(text="Ваша корзина была очищена.")


async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data['awaiting_name'] = True
    await query.edit_message_text(text="Пожалуйста, введите ваше имя для оформления заказа:")



async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "Вернуться в магазин":
        await send_welcome_message(update, context)
    elif text == "Корзина":
        await view_cart(update, context)
    elif text == "Тех.поддержка":
        await update.message.reply_text('Если у вас возникли вопросы, обратитесь в техподдержку: @chokostrawberryadmin')
    elif 'awaiting_name' in context.user_data and context.user_data['awaiting_name']:
        context.user_data['name'] = text
        context.user_data['awaiting_name'] = False
        context.user_data['awaiting_date'] = True
        await update.message.reply_text('На какую дату делаем заказ? (пример: 24.07.2024)')
    elif 'awaiting_date' in context.user_data and context.user_data['awaiting_date']:
        context.user_data['date'] = text
        context.user_data['awaiting_date'] = False
        context.user_data['awaiting_nickname'] = True
        await update.message.reply_text('Пожалуйста, введите ваш @ник в Telegram для связи:')
    elif 'awaiting_nickname' in context.user_data and context.user_data['awaiting_nickname']:
        context.user_data['nickname'] = text
        context.user_data['awaiting_nickname'] = False
        keyboard = [[KeyboardButton("Отправить номер телефона", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text('Теперь, пожалуйста, отправьте ваш номер телефона:', reply_markup=reply_markup)


async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    contact = update.message.contact
    if contact:
        name = context.user_data.get('name', 'Не указано')
        date = context.user_data.get('date', 'Дата не указана')
        nickname = context.user_data.get('nickname', 'Ник не указан')
        unique_id = None  

        cart_items = "\n".join(context.user_data.get('cart', ['Корзина пуста']))

        if context.user_data.get('in_competition', False):
            unique_id = str(uuid.uuid4())[:8]
            message_text_admin = (f"Получен новый заказ от {name} ({nickname})!\n"
                                  f"Номер телефона: {contact.phone_number}\n"
                                  f"Дата заказа: {date}\n"
                                  f"Содержимое заказа:\n{cart_items}\n"
                                  f"Уникальный номер участника конкурса🎂: {unique_id}")
            context.user_data['has_participated'] = True
        else:
            message_text_admin = (f"Получен новый заказ от {name} ({nickname})!\n"
                                  f"Номер телефона: {contact.phone_number}\n"
                                  f"Дата заказа: {date}\n"
                                  f"Содержимое заказа:\n{cart_items}")
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message_text_admin)
        thank_you_message = 'Спасибо, ваш заказ принят в обработку! Мы подготовим его к указанной дате.'

        if unique_id:
            thank_you_message += f'\nВаш уникальный код участника конкурса: {unique_id}'

        await update.message.reply_text(thank_you_message, reply_markup=get_base_reply_keyboard())

        user_has_participated = context.user_data.pop('has_participated', False)
        context.user_data.clear()
        if user_has_participated:
            context.user_data['has_participated'] = True
        context.user_data.pop('in_competition',
                              None)  


if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(handle_choice, pattern='^(strawberry|banana)$'))
    application.add_handler(CallbackQueryHandler(handle_quantity, pattern=r'^(strawberry_|banana_)\d+$'))
    application.add_handler(CallbackQueryHandler(view_cart, pattern='^cart$'))
    application.add_handler(CallbackQueryHandler(clear_cart, pattern='^clear_cart$'))
    application.add_handler(CallbackQueryHandler(checkout, pattern='^checkout$'))
    application.add_handler(CallbackQueryHandler(handle_back_to_shop, pattern='^back_to_shop$'))
    application.add_handler(CallbackQueryHandler(handle_competition, pattern='^competition$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.CONTACT, contact_handler))

    application.run_polling()



