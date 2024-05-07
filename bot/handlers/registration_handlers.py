import logging
from contextlib import suppress

from aiogram import F
from aiogram import Router
from aiogram.enums import ContentType, ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from bot import keyboards
from bot.keyboards import KeyboardCallbackData
from bot.states import RegistrationStates, MenuStates
from services.user_service import (UserServiceAgent, InvalidCityException,
                                   FuzzyCityException, CityAlreadyAddedException,
                                   InvalidTrackListException, TrackListAlreadyAddedException)
from services.user_service.exceptions import InvalidCoordsException
from .constants import (SKIP_COMMAND_FILTER, TEXT_WITHOUT_COMMANDS_FILTER,
                        INTERNAL_ERROR_DEFAULT_TEXT, MAXIMUM_CITY_LEN, MAXIMUM_LINK_LEN)
from .user_data_manager import set_last_keyboard_id, get_last_keyboard_id

registration_router = Router()

__after_first_city_msg = ('Вы можете вводить дальше города по одному.'
                          ' Если желаете перейти к следующему этапу регистрации:\n'
                          'введите команду /skip или нажмите кнопку снизу')

__after_first_link_msg = ('Вы можете вводить дальше ссылки по одной.'
                          ' Если желаете перейти к следующему этапу регистрации:\n'
                          'введите команду /skip или нажмите кнопку снизу')


async def __send_fuzz_variant_message(city: str, variant: str, message: Message, state: FSMContext) -> None:
    await message.answer(text=f'Города {city} не существует, может быть вы имели ввиду {variant}?',
                         reply_markup=ReplyKeyboardRemove())
    await state.update_data(variant=variant)
    msg = await message.answer('Выберите вариант действий', reply_markup=keyboards.get_fuzz_variants_markup())
    await set_last_keyboard_id(msg.message_id, state)
    await state.set_state(RegistrationStates.ADD_CITY_CALLBACKS)


@registration_router.message(RegistrationStates.ADD_FIRST_CITY, F.content_type == ContentType.LOCATION)
async def add_first_city_from_location(message: Message, state: FSMContext, agent: UserServiceAgent) -> None:
    if message.location is None or message.location.latitude is None or message.location.longitude is None:
        await message.answer('Некорректный формат координат, попробуйте еще раз')
        return
    if message.from_user is None:
        return
    user_id = message.from_user.id
    if user_id is None:
        return

    try:
        city = await agent.add_user_city_by_coordinates(user_id, message.location.latitude, message.location.longitude)
        await message.answer(text=f'Город {city} добавлен успешно')
        await state.update_data(is_first_city=False)
        await message.answer(text=__after_first_city_msg, reply_markup=keyboards.get_skip_add_cities_markup())
        await state.set_state(state=RegistrationStates.ADD_CITIES_IN_LOOP)
        return
    except InvalidCityException:
        await message.answer(text='Города не обнаружены')
    except InvalidCoordsException:
        await message.answer(text='Координаты не действительны')
    except CityAlreadyAddedException:
        await message.answer(text='Город уже был добавлен')
    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)


@registration_router.message(RegistrationStates.ADD_FIRST_CITY, TEXT_WITHOUT_COMMANDS_FILTER)
async def add_first_city_from_text(message: Message, state: FSMContext, agent: UserServiceAgent) -> None:
    city = message.text
    if city is None:
        await message.answer(text='Неверный формат текста', reply_markup=keyboards.get_location_keyboard_markup())
        return
    if message.from_user is None:
        return
    user_id = message.from_user.id
    if user_id is None:
        return
    if len(city) > MAXIMUM_CITY_LEN:
        await message.answer(text='Слишком длинное название города',
                             reply_markup=keyboards.get_location_keyboard_markup())
        return
    try:
        await agent.add_user_city(user_id, city)
        await message.answer(text=__after_first_city_msg,
                             reply_markup=keyboards.get_skip_add_cities_markup())
        await message.answer(text=f'Город {city} добавлен успешно.')
        await state.update_data(is_first_city=False)
        await state.set_state(state=RegistrationStates.ADD_CITIES_IN_LOOP)
    except InvalidCityException:
        await message.answer(text='Некорректно введен город или его не существует',
                             reply_markup=keyboards.get_location_keyboard_markup())
    except FuzzyCityException as e:
        if e.variant is None:
            await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT, reply_markup=keyboards.get_location_keyboard_markup())
            return
        await __send_fuzz_variant_message(city, e.variant, message, state)
    except CityAlreadyAddedException:
        await message.answer('Город уже был добавлен')
    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)


@registration_router.message(RegistrationStates.ADD_CITIES_IN_LOOP, F.text == keyboards.skip_add_cities_texts)
@registration_router.message(RegistrationStates.ADD_CITIES_IN_LOOP, SKIP_COMMAND_FILTER)
async def skip_add_cities(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationStates.ADD_LINK)
    await state.update_data(is_first_link=True)
    await state.update_data(is_first_city=None)
    await message.answer(text='Введите ссылку, откуда мы будем выбирать ваших любимых исполнителей',
                         reply_markup=ReplyKeyboardRemove())


@registration_router.message(RegistrationStates.ADD_CITIES_IN_LOOP, TEXT_WITHOUT_COMMANDS_FILTER)
async def add_city_in_loop(message: Message, state: FSMContext, agent: UserServiceAgent) -> None:
    city = message.text

    if city is None:
        await message.answer(text='Неверный формат текста')
        return

    if message.from_user is None:
        return
    user_id = message.from_user.id
    if user_id is None:
        return

    if len(city) > MAXIMUM_CITY_LEN:
        await message.answer(text='Слишком длинное название города',
                             reply_markup=keyboards.get_skip_add_cities_markup())
        return

    try:
        await agent.add_user_city(user_id, city)
        await message.answer(text=f'Город {city} добавлен успешно.\n'
                                  f'Напоминание: можно ввести /skip',
                             reply_markup=keyboards.get_skip_add_cities_markup())
    except InvalidCityException:
        await message.answer(text='Некорректно введен город или его не существует',
                             reply_markup=keyboards.get_skip_add_cities_markup())
    except FuzzyCityException as e:
        if e.variant is None:
            await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)
            return
        await __send_fuzz_variant_message(city, e.variant, message, state)
    except CityAlreadyAddedException:
        await message.answer('Город уже был добавлен', reply_markup=keyboards.get_skip_add_cities_markup())
    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)


@registration_router.callback_query(RegistrationStates.ADD_CITY_CALLBACKS, F.data == KeyboardCallbackData.APPLY)
async def apply_city_callback(callback_query: CallbackQuery, state: FSMContext, agent: UserServiceAgent) -> None:
    bot = callback_query.bot
    if bot is None:
        return

    if callback_query.from_user is None:
        return
    if callback_query.message is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return
    user_data = await state.get_data()
    city = user_data['variant']
    await callback_query.answer()
    try:
        await agent.add_user_city(user_id, city)
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=get_last_keyboard_id(user_data))
        if user_data['is_first_city']:
            await bot.send_message(chat_id=callback_query.message.chat.id,
                                   text='Город добавлен',
                                   reply_markup=keyboards.get_skip_add_cities_markup())
            await bot.send_message(chat_id=callback_query.message.chat.id,
                                   text=__after_first_city_msg,
                                   reply_markup=keyboards.get_skip_add_cities_markup())
            await state.update_data(is_first_city=False)
        else:
            await bot.send_message(chat_id=callback_query.message.chat.id,
                                   text='Город добавлен\n'
                                        'Напоминание: можно ввести /skip',
                                   reply_markup=keyboards.get_skip_add_cities_markup())

        await state.set_state(RegistrationStates.ADD_CITIES_IN_LOOP)

    except CityAlreadyAddedException:
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=get_last_keyboard_id(user_data))
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text='Город уже был добавлен',
                               reply_markup=keyboards.get_skip_add_cities_markup())
    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        with suppress(TelegramBadRequest):
            if isinstance(callback_query.message, Message):
                await callback_query.message.edit_text(text=INTERNAL_ERROR_DEFAULT_TEXT,
                                                       reply_markup=keyboards.get_fuzz_variants_markup())


@registration_router.callback_query(RegistrationStates.ADD_CITY_CALLBACKS, F.data == KeyboardCallbackData.DENY)
async def deny_city_variant(callback_query: CallbackQuery, state: FSMContext) -> None:
    bot = callback_query.bot
    if bot is None or callback_query is None or callback_query.message is None:
        return
    user_data = await state.get_data()
    with suppress(TelegramBadRequest):
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=get_last_keyboard_id(user_data))
    if user_data['is_first_city']:
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text='Вариант был отклонён',
                               reply_markup=keyboards.get_location_keyboard_markup())
        await state.set_state(RegistrationStates.ADD_FIRST_CITY)
        return

    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Вариант был отклонён',
                           reply_markup=keyboards.get_skip_add_cities_markup())
    await state.set_state(RegistrationStates.ADD_CITIES_IN_LOOP)


@registration_router.message(RegistrationStates.ADD_LINK, F.text == keyboards.skip_add_links_texts)
@registration_router.message(RegistrationStates.ADD_LINK, SKIP_COMMAND_FILTER)
async def skip_add_links(message: Message, state: FSMContext) -> None:
    await state.set_state(MenuStates.MAIN_MENU)
    await state.update_data(is_first_link=None)
    await message.answer(text='Регистрация окончена', reply_markup=ReplyKeyboardRemove())
    msg = await message.answer(text='Выберите действие', reply_markup=keyboards.get_main_menu_keyboard())
    await state.update_data(last_keyboard_id=msg.message_id)


@registration_router.message(RegistrationStates.ADD_LINK, TEXT_WITHOUT_COMMANDS_FILTER
                             and F.text != keyboards.skip_add_cities_texts)
async def add_link(message: Message, state: FSMContext, agent: UserServiceAgent) -> None:
    link = message.text
    if link is None:
        await message.answer(text='Неверный формат текста')
        return
    if message.from_user is None:
        return
    user_id = message.from_user.id
    if user_id is None:
        return

    if len(link) > MAXIMUM_LINK_LEN:
        await message.answer(text='Слишком длинная ссылка', reply_markup=keyboards.get_skip_add_links_markup())
        return

    try:
        track_list = await agent.add_user_track_list(user_id, link)
        user_data = await state.get_data()
        if user_data['is_first_link']:
            await message.answer(text=__after_first_link_msg, reply_markup=keyboards.get_skip_add_links_markup())
            await state.update_data(is_first_link=False)
            await message.answer(text=f'Трек-лист {track_list.title} успешно добавлен')
        else:
            await message.answer(f'Трек-лист {track_list.title} успешно добавлен.\n'
                                 f'Напоминание: можно ввести /skip', reply_markup=keyboards.get_skip_add_links_markup())
    except InvalidTrackListException:
        await message.answer(text='Ссылка недействительна')
    except TrackListAlreadyAddedException:
        await message.answer(text='Трек-лист уже был добавлен')
    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)
