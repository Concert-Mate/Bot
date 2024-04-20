from contextlib import suppress

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from bot import keyboards
from bot.states import RegistrationStates, MenuStates
from services.user_service import UserServiceAgent

registration_router = Router()

__after_first_city_msg = ('Вы можете вводить дальше города по одному. Если желаете прекратить это - введите команду '
                          '/skip или нажмите кнокну снизу')

__after_first_link_msg = ('Вы можете вводить дальше ссылки по одной. Если желаете прекратить это - введите команду '
                          '/skip или нажмите кнокну снизу')


async def __send_fuzz_variant_message(city: str, message: Message, state: FSMContext) -> None:
    await message.answer(text=f'Города {city} не существует, может быть вы имели ввиду Челябинск?',
                         reply_markup=ReplyKeyboardRemove())
    await state.update_data(variant='Челябинск')
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


async def __add_link(link: str, is_first_link: bool, state: FSMContext) -> bool:
    if is_first_link:
        await state.update_data(links=[link])
        return True
    user_data = await state.get_data()
    if link in user_data['links']:
        return False
    user_data['links'].append(link)
    return True


@registration_router.message(RegistrationStates.ADD_FIRST_CITY, F.content_type == ContentType.LOCATION)
async def add_first_city_from_location(message: Message, state: FSMContext) -> None:
    if message.location is None or message.location.latitude is None or message.location.longitude is None:
        await message.answer('Некорректный формат координат, попробуйте еще раз')
        return
    coords = f'lat:{message.location.latitude}, lng:{message.location.longitude}'
    await __add_city(coords, True, state)
    await message.answer(text=f"Ваши координаты: {coords}", reply_markup=ReplyKeyboardRemove())
    await state.update_data(is_first_city=False)
    await message.answer(text=__after_first_city_msg, reply_markup=keyboards.get_skip_add_cities_markup())
    await state.set_state(state=RegistrationStates.ADD_CITIES_IN_LOOP)
    # QUESTION: Может ли быть тут некорректный город?


@registration_router.message(RegistrationStates.ADD_FIRST_CITY, F.content_type == ContentType.TEXT and F.text[0] != '/')
async def add_first_city_from_text(message: Message, state: FSMContext) -> None:
    city = message.text
    # if city is None:
    #     await message.answer(text='Неверный формат текста')
    #     return
    # if message.from_user is None:
    #     return
    # user_id = message.from_user.id
    # if user_id is None:
    #     return
    # try:
    #     response = add_city(user_id, city)
    # except ValueError as e:
    #     print(e)
    #     return
    #
    # if response.code == ResponseCodes.SUCCESS:
    #     await __add_city(city, True, state)
    #     await message.answer(text=f'Город {city} добавлен успешно.', reply_markup=ReplyKeyboardRemove())
    #     await state.update_data(is_first_city=False)
    #     await message.answer(text=__after_first_city_msg, reply_markup=keyboards.get_skip_add_cities_markup())
    #     await state.set_state(state=RegistrationStates.ADD_CITIES_IN_LOOP)
    #     return
    # if response.code == ResponseCodes.INVALID_CITY:
    #     await message.answer(text='Некорректно введен город или его не существует')
    #     return
    # if response.code == ResponseCodes.FUZZY_CITY:
    #     await __send_fuzz_variant_message(city, message, state)
    #     return
    # if (response.code == ResponseCodes.CITY_ALREADY_ADDED or
    #         response.code == ResponseCodes.NO_CONNECTION or
    #         response.code == ResponseCodes.INTERNAL_ERROR or
    #         response.code == ResponseCodes.USER_NOT_FOUND):
    #     await message.answer(text='Ошибки на стороне сервиса, попробуйте еще раз')


@registration_router.message(RegistrationStates.ADD_CITIES_IN_LOOP, F.text == keyboards.skip_add_cities_texts)
@registration_router.message(RegistrationStates.ADD_CITIES_IN_LOOP, Command('skip'))
async def skip_add_cities(message: Message, state: FSMContext) -> None:
    await message.answer(text='Введите ссылку, откуда мы будем выбирать ваших любимых исполнителей',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.ADD_LINK)


@registration_router.message(RegistrationStates.ADD_CITIES_IN_LOOP, (F.content_type == ContentType.TEXT
                                                                     and F.text[0] != '/'))
async def add_city_in_loop(message: Message, state: FSMContext) -> None:
    city = message.text
    # if city is None:
    #     await message.answer(text='Неверный формат текста')
    #     return
    # if message.from_user is None:
    #     return
    # user_id = message.from_user.id
    # if user_id is None:
    #     return
    #
    # try:
    #     response = add_city(message.from_user.id, city)
    # except ValueError as e:
    #     print(e)
    #     return
    #
    # if response.code == ResponseCodes.SUCCESS:
    #     is_city_was_added = await __add_city(city, False, state)
    #
    #     if not is_city_was_added:
    #         await message.answer(text='Город уже был добавлен')
    #         return
    #
    #     await message.answer(text=f'Город {city} добавлен успешно.')
    #     return
    #
    # if response.code == ResponseCodes.INVALID_CITY:
    #     await message.answer(text='Некорректно введен город или его не существует')
    #     return
    # if response.code == ResponseCodes.FUZZY_CITY:
    #     await __send_fuzz_variant_message(city, message, state)
    #     return
    # if (response.code == ResponseCodes.CITY_ALREADY_ADDED or
    #         response.code == ResponseCodes.NO_CONNECTION or
    #         response.code == ResponseCodes.INTERNAL_ERROR or
    #         response.code == ResponseCodes.USER_NOT_FOUND):
    #     await message.answer(text='Ошибки на стороне сервиса, попробуйте еще раз')


@registration_router.callback_query(RegistrationStates.ADD_CITY_CALLBACKS, F.data == 'apply')
async def apply_city_callback(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_data = await state.get_data()
    # city = user_data['variant']
    # bot = callback_query.bot
    # if bot is None or callback_query.message is None:
    #     return
    # try:
    #     response = add_city(callback_query.from_user.id, city)
    # except ValueError as e:
    #     print(e)
    #     return
    # await callback_query.answer()
    # if response.code == ResponseCodes.SUCCESS:
    #     is_city_was_added = await __add_city(city, user_data['is_first_city'], state)
    #     await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
    #                                         message_id=callback_query.message.message_id,
    #                                         reply_markup=None)
    #
    #     if user_data['is_first_city']:
    #         await bot.send_message(chat_id=callback_query.message.chat.id,
    #                                text='Город добавлен')
    #         await bot.send_message(chat_id=callback_query.message.chat.id,
    #                                text=__after_first_city_msg,
    #                                reply_markup=keyboards.get_skip_add_cities_markup())
    #         await state.update_data(is_first_city=False)
    #         await state.set_state(RegistrationStates.ADD_CITIES_IN_LOOP)
    #         return
    #
    #     await state.set_state(RegistrationStates.ADD_CITIES_IN_LOOP)
    #
    #     if not is_city_was_added:
    #         await bot.send_message(chat_id=callback_query.message.chat.id,
    #                                text='Город уже был добавлен',
    #                                reply_markup=keyboards.get_skip_add_cities_markup())
    #         return
    #
    #     await bot.send_message(chat_id=callback_query.message.chat.id,
    #                            text='Город добавлен',
    #                            reply_markup=keyboards.get_skip_add_cities_markup())
    #
    # if (response.code == ResponseCodes.CITY_ALREADY_ADDED or
    #         response.code == ResponseCodes.NO_CONNECTION or
    #         response.code == ResponseCodes.INTERNAL_ERROR or
    #         response.code == ResponseCodes.USER_NOT_FOUND or
    #         response.code == ResponseCodes.FUZZY_CITY or
    #         response.code == ResponseCodes.INVALID_CITY):
    #     with suppress(TelegramBadRequest):
    #         if isinstance(callback_query.message, Message):
    #             await callback_query.message.edit_text(text='Ошибки на стороне сервиса, попробуйте еще раз',
    #                                                    reply_markup=keyboards.get_fuzz_variants_markup())


@registration_router.callback_query(RegistrationStates.ADD_CITY_CALLBACKS, F.data == 'deny')
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
@registration_router.message(RegistrationStates.ADD_LINK, Command('skip'))
async def skip_add_links(message: Message, state: FSMContext) -> None:
    await message.answer(text='Регистрация окончена', reply_markup=ReplyKeyboardRemove())
    await message.answer(text='Выберите действие', reply_markup=keyboards.get_main_menu_keyboard())
    await state.set_state(MenuStates.MAIN_MENU)


@registration_router.message(RegistrationStates.ADD_LINK, F.content_type == ContentType.TEXT and F.text[0] != '/')
async def add_link(message: Message, state: FSMContext) -> None:
    link = message.text
    # if link is None:
    #     await message.answer(text='Неверный формат текста')
    #     return
    # if message.from_user is None:
    #     return
    # user_id = message.from_user.id
    # if user_id is None:
    #     return
    #
    # try:
    #     response = add_playlist(message.from_user.id, link)
    # except ValueError as e:
    #     print(e)
    #     return
    # if response.code == ResponseCodes.SUCCESS:
    #     user_data = await state.get_data()
    #     if len(user_data['links']) == 0:
    #         await __add_link(link, True, state)
    #         await message.answer(text='Ссылка успешно добавлена')
    #         await message.answer(text=__after_first_link_msg, reply_markup=keyboards.get_skip_add_links_markup())
    #         return
    #
    #     is_link_was_added = await __add_link(link, False, state)
    #     if not is_link_was_added:
    #         await message.answer(text='Ссылка уже была добавлена')
    #         return
    #
    #     await message.answer(text='Ссылка успешно добавлена')
    # if response.code == ResponseCodes.INVALID_TRACKS_LIST:
    #     await message.answer(text='Ссылка недействительна')
    #     return
    # if (response.code == ResponseCodes.USER_NOT_FOUND or
    #         response.code == ResponseCodes.INTERNAL_ERROR or
    #         response.code == ResponseCodes.NO_CONNECTION or
    #         response.code == ResponseCodes.TRACKS_LIST_ALREADY_ADDED):
    #     await message.answer(text='Ошибка на стороне сервиса, попробуйте позже')
