import random
import logging
from os import getenv

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, filters, ConversationHandler, ContextTypes, MessageHandler, \
    CallbackQueryHandler

CITY_REGISTRATION, CITY_REGISTRATION_CALLBACKS, LINK_REGISTRATION = map(
    chr, range(3))

(CONTINUE_ADD_CITIES,
 STOP_ADD_CITIES,
 APPLY_ADD_VARIANT,
 DENY_ADD_VARIANT) = map(chr, range(3, 7))

(
    CITIES,
    LINKS,
    VARIANT,
    IS_SHOWED_LOOP_MSG
) = map(chr, range(120, 124))

END = ConversationHandler.END

keyboard_city = [
    [
        'Прекратить ввод городов'
    ]
]
markup_city = ReplyKeyboardMarkup(keyboard_city, one_time_keyboard=True, resize_keyboard=True)

keyboard_links = [
    [
        'Прекратить ввод ссылок'
    ]
]
markup_links = ReplyKeyboardMarkup(keyboard_links, one_time_keyboard=True, resize_keyboard=True)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user = update.effective_user

    context.user_data[CITIES] = []
    context.user_data[VARIANT] = ''
    context.user_data[LINKS] = []
    context.user_data[IS_SHOWED_LOOP_MSG] = False

    initial_message = f'Приветствую тебя {user.username} в нашем Concerts mate bot'
    if True:
        await update.message.reply_text(f'{initial_message}. '
                                        f'{"Поскольку вы здесь впервые, нужно пройти процесс регистрации."}',
                                        reply_markup=ReplyKeyboardRemove())
        await update.message.reply_text('Введите город в котором вы желаете посещать концерты')
        return CITY_REGISTRATION
    else:
        return END


async def add_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    city_name = update.message.text
    logger.info(msg=f'{city_name} by {update.effective_user.name}')
    cities_data = context.user_data[CITIES]
    if city_name in cities_data:
        await update.message.reply_text(f"Город {city_name} уже был добавлен")
    else:
        luck_factor = random.randrange(0, 2)

        if luck_factor % 2 == 1:
            inline_keyboard = [
                [
                    InlineKeyboardButton('Добавить', callback_data=str(APPLY_ADD_VARIANT)),
                    InlineKeyboardButton('Отказаться', callback_data=str(DENY_ADD_VARIANT))
                ]
            ]
            await update.message.reply_text(f'Города {city_name} не существует, может вы имели ввиду Мурманск?',
                                            reply_markup=ReplyKeyboardRemove())
            reply_markup = InlineKeyboardMarkup(inline_keyboard)
            context.user_data[VARIANT] = 'Мурманск'
            await update.message.reply_text(f'Выберите вариант действий',
                                            reply_markup=reply_markup)
            return CITY_REGISTRATION_CALLBACKS

        cities_data.append(city_name)
        await update.message.reply_text(f"Город {city_name} добавлен успешно")
    if not context.user_data[IS_SHOWED_LOOP_MSG]:
        await update.message.reply_text(f'Вы можете продолжать вводить города по одному,'
                                        f' чтобы пропустить этот процесс введите /skip или нажмите на кнопку снизу',
                                        reply_markup=markup_city)
        context.user_data[IS_SHOWED_LOOP_MSG] = True
    return CITY_REGISTRATION


async def stop_adding_cities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if len(context.user_data[CITIES]) == 0:
        await update.message.reply_text('Вы не ввели ни одного города, введите город')
        return CITY_REGISTRATION
    text = 'Введенные вами города:'
    for city in context.user_data[CITIES]:
        text += f'\n{city}'
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text('Укажите ссылку на плейлист/альбом откуда мы будем брать информацию о ваших '
                                    'предпочтениях')
    context.user_data[IS_SHOWED_LOOP_MSG] = False
    return LINK_REGISTRATION


async def add_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    msg = update.message.text
    # TODO: Проветка ссылки на адекватность
    if msg in context.user_data[LINKS]:
        await update.message.reply_text('Такая ссылка уже была добавлена')
        return LINK_REGISTRATION
    else:
        context.user_data[LINKS].append(msg)
        await update.message.reply_text('Ссылка была добавлена успешно')
    if not context.user_data[IS_SHOWED_LOOP_MSG]:
        await update.message.reply_text(f'Вы можете продолжать вводить ссылки по одной,'
                                        f' чтобы пропустить этот процесс введите /skip или нажмите на кнопку снизу',
                                        reply_markup=markup_links)
        context.user_data[IS_SHOWED_LOOP_MSG] = True
    return LINK_REGISTRATION


async def stop_adding_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if len(context.user_data[LINKS]) == 0:
        await update.message.reply_text('Вы не ввели ни одной ссылки, введите ссылку')
        return LINK_REGISTRATION
    text = 'Введенные вами ссылки:'
    for link in context.user_data[LINKS]:
        text += f'\n{link}'
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return END


async def apply_city_variant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    city_name = context.user_data[VARIANT]
    cities_data = context.user_data[CITIES]
    await update.callback_query.edit_message_reply_markup(None)
    if city_name in cities_data:
        await update.effective_message.reply_text(f'Город {city_name} уже был добавлен', reply_markup=markup_city)
    else:
        cities_data.append(city_name)
        await update.effective_message.reply_text(f'Город {city_name} был добавлен', reply_markup=markup_city)
        if not context.user_data[IS_SHOWED_LOOP_MSG]:
            await update.effective_message.reply_text(f'Вы можете продолжать вводить города по одному,'
                                                      f' чтобы пропустить этот процесс введите /skip или нажмите на '
                                                      f'кнопку снизу',
                                                      reply_markup=markup_city)
            context.user_data[IS_SHOWED_LOOP_MSG] = True

    return CITY_REGISTRATION


async def deny_city_variant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.callback_query.edit_message_reply_markup(None)
    await update.effective_message.reply_text('Вариант отклонён', reply_markup=markup_city)
    return CITY_REGISTRATION


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Всего хорошего.')
    return END


def main() -> None:
    load_dotenv()
    print('launch the bot')
    application = Application.builder().token(getenv('BOT_TOKEN')).build()

    registration_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CITY_REGISTRATION: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex('^Прекратить ввод городов$')),
                               add_city),
                CommandHandler('skip', stop_adding_cities),
                MessageHandler(filters.TEXT & filters.Regex('^Прекратить ввод городов$'),
                               stop_adding_cities)],
            CITY_REGISTRATION_CALLBACKS: [
                CallbackQueryHandler(apply_city_variant, pattern=f'^{APPLY_ADD_VARIANT}$'),
                CallbackQueryHandler(deny_city_variant, pattern=f'^{DENY_ADD_VARIANT}$'),
            ],
            LINK_REGISTRATION: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex('^Прекратить ввод ссылок')),
                               add_link),
                CommandHandler('skip', stop_adding_links),
                MessageHandler(filters.TEXT & filters.Regex('^Прекратить ввод ссылок'),
                               stop_adding_links)
            ]
        },
        fallbacks=[CommandHandler("stop", end)],
    )

    application.add_handler(registration_conv_handler)

    print('successful launch')
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
