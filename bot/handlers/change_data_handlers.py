import random
from contextlib import suppress

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import keyboards
from bot.states import MenuStates, ChangeDataStates
from services.user_service_agent import add_city, add_playlist, ResponseCodes

change_data_router = Router()


async def __send_fuzz_variant_message(city: str, message: Message, state: FSMContext) -> None:
    await message.answer(text=f'Города {city} не существует, может быть вы имели ввиду Челябинск?')
    await state.update_data(variant='Челябинск')
    await message.answer('Выберите вариант действий', reply_markup=keyboards.get_fuzz_variants_markup())
    await state.set_state(ChangeDataStates.CITY_NAME_IS_FUZZY)


@change_data_router.callback_query(MenuStates.CHANGE_DATA, F.data == 'back')
async def show_change_data_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text('Выберите действие', reply_markup=keyboards.get_main_menu_keyboard())
        await state.set_state(MenuStates.MAIN_MENU)


@change_data_router.callback_query(MenuStates.CHANGE_DATA, F.data == 'add_city')
async def add_city_text_send(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text(text='Введите название города', reply_markup=keyboards.get_cancel_keyboard())
    await state.set_state(ChangeDataStates.ENTER_NEW_CITY)


@change_data_router.message(MenuStates.CHANGE_DATA)
async def resent(message: Message, state: FSMContext) -> None:
    bot = message.bot
    if bot is None:
        return
    await bot.delete_message(chat_id=message.chat.id, message_id=(message.message_id - 1))
    await bot.send_message(chat_id=message.chat.id, text='Выберите действие',
                           reply_markup=keyboards.get_change_data_keyboard())


@change_data_router.callback_query(ChangeDataStates.ENTER_NEW_CITY, F.data == 'cancel')
async def cancel_add_city(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text(text='Выберите действие', reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.message(ChangeDataStates.ENTER_NEW_CITY, (F.content_type == ContentType.TEXT
                                                              and F.text[0] != '/'))
async def add_one_city(message: Message, state: FSMContext) -> None:
    bot = message.bot
    # if bot is None:
    #     return
    # await bot.delete_message(message.chat.id, message.message_id - 1)
    # city = message.text
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
    # user_data = await state.get_data()
    #
    # if response.code == ResponseCodes.SUCCESS:
    #     if city in user_data['cities']:
    #         await message.answer(text='Город уже был добавлен')
    #     else:
    #         user_data['cities'].append(city)
    #         await message.answer(text=f'Город {city} добавлен успешно.')
    # if response.code == ResponseCodes.INVALID_CITY:
    #     await message.answer(text='Некорректно введен город или его не существует')
    # if response.code == ResponseCodes.FUZZY_CITY:
    #     await __send_fuzz_variant_message(city, message, state)
    #     return
    # if (response.code == ResponseCodes.CITY_ALREADY_ADDED or
    #         response.code == ResponseCodes.NO_CONNECTION or
    #         response.code == ResponseCodes.INTERNAL_ERROR or
    #         response.code == ResponseCodes.USER_NOT_FOUND):
    #     await message.answer(text='Ошибки на стороне сервиса, попробуйте еще раз')
    #
    # await message.answer(text='Выберите вариант', reply_markup=keyboards.get_change_data_keyboard())
    # await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(ChangeDataStates.CITY_NAME_IS_FUZZY, F.data == 'apply')
async def apply_city_variant(callback_query: CallbackQuery, state: FSMContext) -> None:
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
    #
    # if response.code == ResponseCodes.SUCCESS:
    #     if city not in user_data['cities']:
    #         user_data['cities'].append(city)
    #         await bot.edit_message_text(chat_id=callback_query.message.chat.id, text='Город успешно добавлен',
    #                                     message_id=callback_query.message.message_id, reply_markup=None)
    #     else:
    #         await bot.edit_message_text(chat_id=callback_query.message.chat.id, text='Город уже был добавлен',
    #                                     message_id=callback_query.message.message_id, reply_markup=None)
    #
    #     await bot.send_message(chat_id=callback_query.message.chat.id, text='Выберите вариант',
    #                            reply_markup=keyboards.get_change_data_keyboard())
    #     await state.set_state(MenuStates.CHANGE_DATA)
    #     return
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


@change_data_router.callback_query(ChangeDataStates.CITY_NAME_IS_FUZZY, F.data == 'deny')
async def deny_city_variant(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text(text='Выберите вариант', reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(MenuStates.CHANGE_DATA, F.data == 'remove_city')
async def show_cities_as_inline_keyboard(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    user_data = await state.get_data()

    await callback_query.message.edit_text(text='Выберите город, который нужно удалить',
                                           reply_markup=keyboards.create_inline_keyboard_with_back(user_data['cities']))
    await state.set_state(ChangeDataStates.REMOVE_CITY)


@change_data_router.callback_query(ChangeDataStates.REMOVE_CITY, F.data == 'back')
async def return_from_remove(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text(text='Выберите действие',
                                           reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(ChangeDataStates.REMOVE_CITY, F.data != 'back')
async def remove_city(callback_query: CallbackQuery, state: FSMContext) -> None:
    city = callback_query.data
    bot = callback_query.bot
    if bot is None or callback_query.message is None:
        return

    if random.randint(0, 1) == 1:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=f'Проблемы на стороне сервиса, попробуйте позже', reply_markup=None)
        await bot.send_message(chat_id=callback_query.message.chat.id, text='Выберите вариант',
                               reply_markup=keyboards.get_change_data_keyboard())
        await state.set_state(MenuStates.CHANGE_DATA)
        return

    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                text=f'Город {city} успешно удалён')
    user_data = await state.get_data()
    user_data['cities'].remove(city)
    await bot.send_message(chat_id=callback_query.message.chat.id, text='Выберите вариант',
                           reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(MenuStates.CHANGE_DATA, F.data == 'add_playlist')
async def add_one_playlist_show_msg(callback_query: CallbackQuery, state: FSMContext) -> None:
    bot = callback_query.bot
    if bot is None or callback_query is None or callback_query.message is None:
        return

    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                text='Введите ссылку на плейлист',
                                reply_markup=keyboards.get_cancel_keyboard())
    await state.set_state(ChangeDataStates.ENTER_NEW_PLAYLIST)


@change_data_router.message(ChangeDataStates.ENTER_NEW_PLAYLIST, (F.content_type == ContentType.TEXT
                                                                  and F.text[0] != '/'))
async def add_one_playlist(message: Message, state: FSMContext) -> None:
    bot = message.bot
    # if bot is None:
    #     return
    # await bot.delete_message(message.chat.id, message.message_id - 1)
    # link = message.text
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
    #
    # if response.code == ResponseCodes.SUCCESS:
    #     user_data = await state.get_data()
    #     if link in user_data['links']:
    #         await message.answer('Ссылка уже была добавлена')
    #     else:
    #         await message.answer(text='Ссылка успешно добавлена')
    #         user_data['links'].append(link)
    #
    # if response.code == ResponseCodes.INVALID_TRACKS_LIST:
    #     await message.answer(text='Ссылка недействительна')
    # if (response.code == ResponseCodes.USER_NOT_FOUND or
    #         response.code == ResponseCodes.INTERNAL_ERROR or
    #         response.code == ResponseCodes.NO_CONNECTION or
    #         response.code == ResponseCodes.TRACKS_LIST_ALREADY_ADDED):
    #     await message.answer(text='Ошибка на стороне сервиса, попробуйте позже')
    #
    # await message.answer(text='Выберите вариант', reply_markup=keyboards.get_change_data_keyboard())
    # await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(ChangeDataStates.ENTER_NEW_PLAYLIST, F.data == 'cancel')
async def return_from_add_playlist(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text(text='Выберите действие', reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(MenuStates.CHANGE_DATA, F.data == 'remove_playlist')
async def show_playlists_as_inline_keyboard(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return

    user_data = await state.get_data()

    await callback_query.message.edit_text(text='Выберите ссылку, которую нужно удалить',
                                           reply_markup=keyboards.create_inline_keyboard_with_back(
                                               user_data['links']))
    await state.set_state(ChangeDataStates.REMOVE_PLAYLIST)


@change_data_router.callback_query(ChangeDataStates.REMOVE_PLAYLIST, F.data == 'back')
async def return_from_remove_playlist(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text(text='Выберите действие',
                                           reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(ChangeDataStates.REMOVE_PLAYLIST, F.data != 'back')
async def remove_playlist(callback_query: CallbackQuery, state: FSMContext) -> None:
    playlist = callback_query.data
    bot = callback_query.bot
    if bot is None or callback_query.message is None:
        return
    if random.randint(0, 1) == 1:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=f'Проблемы на стороне сервиса, попробуйте позже', reply_markup=None)
        await bot.send_message(chat_id=callback_query.message.chat.id, text='Выберите вариант',
                               reply_markup=keyboards.get_change_data_keyboard())
        await state.set_state(MenuStates.CHANGE_DATA)
        return
    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                text=f'Ссылка {playlist} успешно удалёна', reply_markup=None)
    user_data = await state.get_data()
    user_data['links'].remove(playlist)
    await bot.send_message(chat_id=callback_query.message.chat.id, text='Выберите вариант',
                           reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)
