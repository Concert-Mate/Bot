import logging
from contextlib import suppress

from aiogram import F
from aiogram import Router
from aiogram.enums import ContentType
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
from .constants import SKIP_COMMAND_FILTER, TEXT_WITHOUT_COMMANDS_FILTER, INTERNAL_ERROR_DEFAULT_TEXT

registration_router = Router()

__after_first_city_msg = ('Вы можете вводить дальше города по одному. Если желаете прекратить это - введите команду '
                          '/skip или нажмите кнопку снизу')

__after_first_link_msg = ('Вы можете вводить дальше ссылки по одной. Если желаете прекратить это - введите команду '
                          '/skip или нажмите кнопку снизу')


async def __send_fuzz_variant_message(city: str, variant: str, message: Message, state: FSMContext) -> None:
    await message.answer(text=f'Города {city} не существует, может быть вы имели ввиду {variant}?',
                         reply_markup=ReplyKeyboardRemove())
    await state.update_data(variant=variant)
    await message.answer('Выберите вариант действий', reply_markup=keyboards.get_fuzz_variants_markup())
    await state.set_state(RegistrationStates.ADD_CITY_CALLBACKS)


async def __add_city(city: str, is_first_city: bool, state: FSMContext) -> bool:
    if is_first_city:
        await state.update_data(cities=[city])
        return True
    user_data = await state.get_data()
    if city in user_data['cities']:
        return False
    user_data['cities'].append(city)
    return True


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
        await message.answer(text='Неверный формат текста')
        return
    if message.from_user is None:
        return
    user_id = message.from_user.id
    if user_id is None:
        return
    try:
        await agent.add_user_city(user_id, city)
        await message.answer(text=f'Город {city} добавлен успешно.')
        await message.answer(text=__after_first_city_msg, reply_markup=keyboards.get_skip_add_cities_markup())
        await state.set_state(state=RegistrationStates.ADD_CITIES_IN_LOOP)
    except InvalidCityException:
        await message.answer(text='Некорректно введен город или его не существует')
    except FuzzyCityException as e:
        if e.variant is None:
            await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)
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
    await state.update_data(is_first_link=True)
    await state.update_data(is_first_city=None)
    await message.answer(text='Введите ссылку, откуда мы будем выбирать ваших любимых исполнителей',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.ADD_LINK)


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

    try:
        await agent.add_user_city(user_id, city)
        await message.answer(text=f'Город {city} добавлен успешно.')
    except InvalidCityException:
        await message.answer(text='Некорректно введен город или его не существует')
    except FuzzyCityException as e:
        if e.variant is None:
            await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)
            return
        await __send_fuzz_variant_message(city, e.variant, message, state)
    except CityAlreadyAddedException:
        await message.answer('Город уже был добавлен')
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
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text='Город добавлен')
        if user_data['is_first_city']:
            await bot.send_message(chat_id=callback_query.message.chat.id,
                                   text=__after_first_city_msg,
                                   reply_markup=keyboards.get_skip_add_cities_markup())
            await state.update_data(is_first_city=False)

        await state.set_state(RegistrationStates.ADD_CITIES_IN_LOOP)

    except CityAlreadyAddedException:
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
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=None)
    user_data = await state.get_data()
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
    await state.update_data(is_first_link=None)
    await message.answer(text='Регистрация окончена', reply_markup=ReplyKeyboardRemove())
    await message.answer(text='Выберите действие', reply_markup=keyboards.get_main_menu_keyboard())
    await state.set_state(MenuStates.MAIN_MENU)


@registration_router.message(RegistrationStates.ADD_LINK, TEXT_WITHOUT_COMMANDS_FILTER)
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
    try:
        track_list = await agent.add_user_track_list(user_id, link)
        user_data = await state.get_data()
        if user_data['is_first_link']:
            await message.answer(text=__after_first_link_msg, reply_markup=keyboards.get_skip_add_links_markup())
            await state.update_data(is_first_link=False)
        await message.answer(text=f'Альбом {track_list.title} успешн добавлен')
    except InvalidTrackListException:
        await message.answer(text='Ссылка недействительна')
    except TrackListAlreadyAddedException:
        await message.answer(text='Альбом уже был добавлен')
    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)
