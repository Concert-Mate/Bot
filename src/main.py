import logging
from os import getenv

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, filters, ConversationHandler, ContextTypes, MessageHandler, \
    CallbackQueryHandler

from FSM import states
from handlers import registration_handlers

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user = update.effective_user

    context.user_data['CITIES'] = []
    context.user_data['VARIANT'] = ''
    context.user_data['LINKS'] = []
    context.user_data['IS_SHOWED_LOOP_MSG'] = False

    initial_message = f'Приветствую тебя {user.username} в нашем Concerts mate bot'
    if True:
        await update.message.reply_text(f'{initial_message}. '
                                        f'{"Поскольку вы здесь впервые, нужно пройти процесс регистрации."}',
                                        reply_markup=ReplyKeyboardRemove())
        await update.message.reply_text('Введите город в котором вы желаете посещать концерты')
        return states.GlobalStates.REGISTRATION.value
    else:
        return END


async def stop_nested(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Всего хорошего.')
    return states.END


async def show_secret(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Помогите. Меня держат в подвале и заставляют делать фронтенд(бота этого)')
    return states.END


def main() -> None:
    load_dotenv()
    print('launch the bot')
    print(states.GlobalStates.CITY_REGISTRATION)
    application = Application.builder().token(getenv('BOT_TOKEN')).build()

    registration_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex('^Прекратить ввод городов$')),
                                     registration_handlers.add_city)],
        states={
            states.GlobalStates.CITY_REGISTRATION.value: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex('^Прекратить ввод городов$')),
                               registration_handlers.add_city),
                CommandHandler('skip', registration_handlers.stop_adding_cities),
                MessageHandler(filters.TEXT & filters.Regex('^Прекратить ввод городов$'),
                               registration_handlers.stop_adding_cities)],
            states.GlobalStates.CITY_REGISTRATION_CALLBACKS.value: [
                CallbackQueryHandler(registration_handlers.apply_city_variant,
                                     pattern=f'^{str(states.CityStates.APPLY_ADD_VARIANT)}$'),
                CallbackQueryHandler(registration_handlers.deny_city_variant,
                                     pattern=f'^{str(states.CityStates.DENY_ADD_VARIANT)}$'),
            ],
            states.GlobalStates.LINK_REGISTRATION.value: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex('^Прекратить ввод ссылок')),
                               registration_handlers.add_link),
                CommandHandler('skip', registration_handlers.stop_adding_links),
                MessageHandler(filters.TEXT & filters.Regex('^Прекратить ввод ссылок'),
                               registration_handlers.stop_adding_links)
            ]
        },
        fallbacks=[CommandHandler("stop", stop_nested),
                   ],
        map_to_parent={
            states.END: states.GlobalStates.IDLE.value,
            states.GlobalStates.STOPPING.value: states.END
        }
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            states.GlobalStates.REGISTRATION.value: [registration_conv_handler],
            states.GlobalStates.IDLE.value: [CommandHandler("secret", show_secret)],

        },
        fallbacks=[CommandHandler("stop", stop_nested),
                   ],
    )

    application.add_handler(conv_handler)

    print('successful launch')
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
