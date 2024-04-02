import random
from os import getenv

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, filters, ConversationHandler, ContextTypes, MessageHandler, \
    CallbackQueryHandler

CITY_REGISTRATION, CITY_REGISTRATION_CALLBACKS, PLAYLIST_REGISTRATION, PLAYLIST_REGISTRATION_CALLBACKS, RESULT = map(
    chr, range(5))

CONTINUE_ADD_CITIES, STOP_ADD_CITIES, CONTINUE_ADD_PLAYLISTS, STOP_ADD_PLAYLISTS, APPLY_ADD_VARIANT, DENY_ADD_VARIANT = map(
    chr, range(5, 11))

(
    CITIES
) = map(chr, range(120, 121))

END = ConversationHandler.END


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user = update.effective_user
    context.user_data[CITIES] = []
    context.user_data['VARIANT'] = ''
    initial_message = f'Приветствую тебя {user.username} в нашем Concerts mate bot'
    if True:
        await update.message.reply_text(f'{initial_message}. '
                                        f'{"Поскольку вы здесь впервые, нужно пройти процесс регистрации."}')
        await update.message.reply_text('Введите город в котором вы желаете посещать концерты')
        return CITY_REGISTRATION
    else:
        return END


async def add_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    city_name = update.message.text
    cities_data = context.user_data[CITIES]
    if city_name in cities_data:
        await update.message.reply_text(f"Город {city_name} уже был добавлен")
    else:
        luck_factor = random.randrange(0, 2)

        if luck_factor % 2 == 1:
            keyboard = [
                [
                    InlineKeyboardButton('Добавить предложенное', callback_data=str(APPLY_ADD_VARIANT)),
                    InlineKeyboardButton('Отказаться', callback_data=str(DENY_ADD_VARIANT))
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['VARIANT'] = 'Мурманск'
            await update.message.reply_text(f'Города {city_name} не существует, может вы имели ввиду Мурманск?',
                                            reply_markup=reply_markup)
            return CITY_REGISTRATION_CALLBACKS

        cities_data.append(city_name)
        await update.message.reply_text(f"Город {city_name} добавлен успешно")

    keyboard = [
        [
            InlineKeyboardButton("Добавить еще один город", callback_data=str(CONTINUE_ADD_CITIES)),
            InlineKeyboardButton("Прекратить добавление городов", callback_data=str(STOP_ADD_CITIES)),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Что вы желаете сделать?", reply_markup=reply_markup)
    return CITY_REGISTRATION_CALLBACKS


async def add_one_more_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.callback_query.answer()
    buttons = [
        [
            InlineKeyboardButton(text='Отменить', callback_data=str(STOP_ADD_CITIES)),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.callback_query.edit_message_text('Введите еще один город', reply_markup=keyboard)
    return CITY_REGISTRATION


async def stop_add_cities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = 'Введенные вами города:'
    for city in context.user_data[CITIES]:
        text += f'\n{city}'
    await update.effective_message.reply_text(text)
    return END


async def apply_city_variant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    city_name = context.user_data['VARIANT']
    cities_data = context.user_data[CITIES]
    if city_name in cities_data:
        await update.effective_message.reply_text(f"Город {city_name} уже был добавлен")
    else:
        cities_data.append(city_name)
        await update.effective_message.reply_text(f"Город {city_name} был добавлен")

    keyboard = [
        [
            InlineKeyboardButton("Добавить еще один город", callback_data=str(CONTINUE_ADD_CITIES)),
            InlineKeyboardButton("Прекратить добавление городов", callback_data=str(STOP_ADD_CITIES)),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_message.reply_text("Что вы желаете сделать?", reply_markup=reply_markup)
    return CITY_REGISTRATION_CALLBACKS


async def deny_city_variant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    keyboard = [
        [
            InlineKeyboardButton("Добавить еще один город", callback_data=str(CONTINUE_ADD_CITIES)),
            InlineKeyboardButton("Прекратить добавление городов", callback_data=str(STOP_ADD_CITIES)),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Что вы желаете сделать?", reply_markup=reply_markup)
    return CITY_REGISTRATION_CALLBACKS


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Всего хорошего.')
    return END


def main() -> None:
    load_dotenv()
    print('launch the bot')
    application = Application.builder().token(getenv('BOT_TOKEN')).build()

    city_add_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CITY_REGISTRATION: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                               add_city)],
            CITY_REGISTRATION_CALLBACKS: [
                CallbackQueryHandler(add_one_more_city, pattern=f'^{CONTINUE_ADD_CITIES}$'),
                CallbackQueryHandler(stop_add_cities, pattern=f'^{STOP_ADD_CITIES}$'),
                CallbackQueryHandler(apply_city_variant, pattern=f'^{APPLY_ADD_VARIANT}$'),
                CallbackQueryHandler(deny_city_variant, pattern=f'^{DENY_ADD_VARIANT}$'),
            ],
        },
        fallbacks=[CommandHandler("stop", end)],
    )

    application.add_handler(city_add_conv_handler)

    print('successful launch')
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
