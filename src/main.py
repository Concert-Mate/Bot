from os import getenv
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, filters, ConversationHandler, ContextTypes, MessageHandler, \
    CallbackQueryHandler

FIRST_CITY_REGISTRATION, CONV_HANDLERS = map(chr, range(2))

ONE, TWO = map(chr, range(2, 4))

END = ConversationHandler.END


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user = update.effective_user
    initial_message = f'Приветствую тебя {user.username} в нашем Concerts mate bot'
    if True:
        await update.message.reply_text(f'{initial_message}. '
                                        f'{"Поскольку вы здесь впервые, нужно пройти процесс регистрации."}')
        await update.message.reply_text('Введите город в котором вы желаете посещать концерты')
        return FIRST_CITY_REGISTRATION
    else:
        return END


async def first_city_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    city_name = update.message.text

    await update.message.reply_text(f"Город {city_name} добавлен успешно")
    # await update.message.reply_text(
    #   'Введите ссылку на плейст/альбом из которого мы будем выбирать вашу любимую музыку')

    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=str(ONE)),
            InlineKeyboardButton("2", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Start handler, Choose a route", reply_markup=reply_markup)
    return CONV_HANDLERS


async def one(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | str:
    query = update.callback_query
    await query.edit_message_text('Укажите новый город')
    ## А можно update.reply_text ??? иначе exception ?
    return END


async def two(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | str:
    res = await first_city_registration(update, context)
    return res


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text('Всего хорошего.')
    return END


def main() -> None:
    load_dotenv()
    print('launch the bot')
    application = Application.builder().token(getenv('BOT_TOKEN')).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIRST_CITY_REGISTRATION: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                                     first_city_registration)],
            CONV_HANDLERS: [
                CallbackQueryHandler(one, pattern=f'^{ONE}$'),
                CallbackQueryHandler(two, pattern=f'^{TWO}$'),
            ],
        },
        fallbacks=[CommandHandler("stop", end)],
    )

    application.add_handler(conv_handler)

    print('successful launch')
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
