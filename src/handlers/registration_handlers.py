import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from src.FSM import states

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

keyboard_idle = [
    [
        InlineKeyboardButton(text="Изменение данных", callback_data=str('CHANGE_DATA'))
    ]
]

idle_markup = InlineKeyboardMarkup(keyboard_idle)

__all__ = ['stop_adding_cities', 'stop_adding_links', 'add_link', 'apply_city_variant', 'deny_city_variant', 'add_city']


async def stop_adding_cities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if len(context.user_data['CITIES']) == 0:
        await update.message.reply_text('Вы не ввели ни одного города, введите город')
        return states.GlobalStates.CITY_REGISTRATION.value
    text = 'Введенные вами города:'
    for city in context.user_data['CITIES']:
        text += f'\n{city}'
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text('Укажите ссылку на плейлист/альбом откуда мы будем брать информацию о ваших '
                                    'предпочтениях')
    context.user_data['IS_SHOWED_LOOP_MSG'] = False
    return states.GlobalStates.LINK_REGISTRATION.value


async def add_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    msg = update.message.text
    # TODO: Проветка ссылки на адекватность
    if msg in context.user_data['LINKS']:
        await update.message.reply_text('Такая ссылка уже была добавлена')
        return states.GlobalStates.LINK_REGISTRATION.value
    else:
        context.user_data['LINKS'].append(msg)
        await update.message.reply_text('Ссылка была добавлена успешно')
    if not context.user_data['IS_SHOWED_LOOP_MSG']:
        await update.message.reply_text(f'Вы можете продолжать вводить ссылки по одной,'
                                        f' чтобы пропустить этот процесс введите /skip или нажмите на кнопку снизу',
                                        reply_markup=markup_links)
        context.user_data['IS_SHOWED_LOOP_MSG'] = True
    return states.GlobalStates.LINK_REGISTRATION.value


async def stop_adding_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | int:
    if len(context.user_data['LINKS']) == 0:
        await update.message.reply_text('Вы не ввели ни одной ссылки, введите ссылку')
        return states.GlobalStates.LINK_REGISTRATION.value
    text = 'Введенные вами ссылки:'
    for link in context.user_data['LINKS']:
        text += f'\n{link}'
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text('Выберите действие', reply_markup=idle_markup)
    return states.END


async def apply_city_variant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    city_name = context.user_data['VARIANT']
    cities_data = context.user_data['CITIES']
    await update.callback_query.edit_message_reply_markup(None)
    if city_name in cities_data:
        await update.effective_message.reply_text(f'Город {city_name} уже был добавлен', reply_markup=markup_city)
    else:
        cities_data.append(city_name)
        await update.effective_message.reply_text(f'Город {city_name} был добавлен', reply_markup=markup_city)
        if not context.user_data['IS_SHOWED_LOOP_MSG']:
            await update.effective_message.reply_text(f'Вы можете продолжать вводить города по одному,'
                                                      f' чтобы пропустить этот процесс введите /skip или нажмите на '
                                                      f'кнопку снизу',
                                                      reply_markup=markup_city)
            context.user_data['IS_SHOWED_LOOP_MSG'] = True

    return states.GlobalStates.CITY_REGISTRATION.value


async def deny_city_variant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.callback_query.edit_message_reply_markup(None)
    await update.effective_message.reply_text('Вариант отклонён', reply_markup=markup_city)
    return states.GlobalStates.CITY_REGISTRATION.value


async def add_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    city_name = update.message.text
    cities_data = context.user_data['CITIES']
    if city_name in cities_data:
        await update.message.reply_text(f"Город {city_name} уже был добавлен")
    else:
        luck_factor = random.randrange(0, 2)

        if luck_factor % 2 == 1:
            inline_keyboard = [
                [
                    InlineKeyboardButton('Добавить', callback_data=str(states.CityStates.APPLY_ADD_VARIANT)),
                    InlineKeyboardButton('Отказаться', callback_data=str(states.CityStates.DENY_ADD_VARIANT))
                ]
            ]
            await update.message.reply_text(f'Города {city_name} не существует, может вы имели ввиду Мурманск?',
                                            reply_markup=ReplyKeyboardRemove())
            reply_markup = InlineKeyboardMarkup(inline_keyboard)
            context.user_data['VARIANT'] = 'Мурманск'
            await update.message.reply_text(f'Выберите вариант действий',
                                            reply_markup=reply_markup)
            return states.GlobalStates.CITY_REGISTRATION_CALLBACKS.value

        cities_data.append(city_name)
        await update.message.reply_text(f"Город {city_name} добавлен успешно")
    if not context.user_data['IS_SHOWED_LOOP_MSG']:
        await update.message.reply_text(f'Вы можете продолжать вводить города по одному,'
                                        f' чтобы пропустить этот процесс введите /skip или нажмите на кнопку снизу',
                                        reply_markup=markup_city)
        context.user_data['IS_SHOWED_LOOP_MSG'] = True
    print(states.GlobalStates.CITY_REGISTRATION)
    return states.GlobalStates.CITY_REGISTRATION.value
