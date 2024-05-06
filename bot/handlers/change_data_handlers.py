import logging
from contextlib import suppress

from aiogram import F
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import keyboards
from bot.keyboards import KeyboardCallbackData
from bot.states import MenuStates, ChangeDataStates
from services.user_service import (UserServiceAgent, InvalidCityException,
                                   FuzzyCityException, CityAlreadyAddedException,
                                   TrackListAlreadyAddedException, InvalidTrackListException)
from .constants import (TEXT_WITHOUT_COMMANDS_FILTER, INTERNAL_ERROR_DEFAULT_TEXT,
                        CHOOSE_ACTION_TEXT, MAXIMUM_CITY_LEN, MAXIMUM_LINK_LEN)
from .user_data_manager import set_last_keyboard_id, get_last_keyboard_id

change_data_router = Router()


async def __send_fuzz_variant_message(city: str, variant: str, message: Message, state: FSMContext) -> None:
    await message.answer(text=f'Города {city} не существует, может быть вы имели ввиду {variant}?')
    await state.update_data(variant=variant)
    msg = await message.answer(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_fuzz_variants_markup())
    await set_last_keyboard_id(msg.message_id, state)
    await state.set_state(ChangeDataStates.CITY_NAME_IS_FUZZY)


@change_data_router.callback_query(MenuStates.CHANGE_DATA, F.data == KeyboardCallbackData.BACK)
async def show_change_data_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_main_menu_keyboard())
        await state.set_state(MenuStates.MAIN_MENU)


@change_data_router.callback_query(MenuStates.CHANGE_DATA, F.data == KeyboardCallbackData.ADD_CITY)
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
    user_data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=get_last_keyboard_id(user_data))
    msg = await bot.send_message(chat_id=message.chat.id, text=CHOOSE_ACTION_TEXT,
                                 reply_markup=keyboards.get_change_data_keyboard())
    await set_last_keyboard_id(msg.message_id, state)


@change_data_router.callback_query(ChangeDataStates.ENTER_NEW_CITY, F.data == KeyboardCallbackData.CANCEL)
async def cancel_add_city(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.message(ChangeDataStates.ENTER_NEW_CITY, TEXT_WITHOUT_COMMANDS_FILTER)
async def add_one_city(message: Message, state: FSMContext, agent: UserServiceAgent) -> None:
    bot = message.bot
    if bot is None:
        return
    city = message.text

    if city is None:
        await message.answer(text='Неверный формат текста')
        return

    if message.from_user is None:
        return
    user_id = message.from_user.id
    if user_id is None:
        return

    user_data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=get_last_keyboard_id(user_data))

    if len(city) > MAXIMUM_CITY_LEN:
        await message.answer(text='Слишком длинное название города')
        msg = await message.answer(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_change_data_keyboard())
        await set_last_keyboard_id(msg.message_id, state)
        await state.set_state(MenuStates.CHANGE_DATA)
        return

    try:
        await agent.add_user_city(user_id, city)
        await message.answer(text=f'Город {city} добавлен успешно.')
    except InvalidCityException:
        await message.answer(text='Некорректно введен город или его не существует')
    except FuzzyCityException as e:
        if e.variant is not None:
            await __send_fuzz_variant_message(city, e.variant, message, state)
            return
        else:
            await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)
    except CityAlreadyAddedException:
        await message.answer(text='Город уже был добавлен')
    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)

    msg = await message.answer(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_change_data_keyboard())
    await set_last_keyboard_id(msg.message_id, state)
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(ChangeDataStates.CITY_NAME_IS_FUZZY, F.data == KeyboardCallbackData.APPLY)
async def apply_city_variant(callback_query: CallbackQuery, state: FSMContext, agent: UserServiceAgent) -> None:
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
    try:
        await agent.add_user_city(user_id, city)
        await bot.edit_message_text(chat_id=callback_query.message.chat.id, text='Город успешно добавлен',
                                    message_id=callback_query.message.message_id, reply_markup=None)
        msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                     reply_markup=keyboards.get_change_data_keyboard())
        await set_last_keyboard_id(msg.message_id, state)
        await state.set_state(MenuStates.CHANGE_DATA)

    except CityAlreadyAddedException:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id, text='Город уже был добавлен',
                                    message_id=callback_query.message.message_id, reply_markup=None)
        msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                     reply_markup=keyboards.get_change_data_keyboard())
        await set_last_keyboard_id(msg.message_id, state)
        await state.set_state(MenuStates.CHANGE_DATA)
    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        with suppress(TelegramBadRequest):
            if isinstance(callback_query.message, Message):
                await callback_query.message.edit_text(text=INTERNAL_ERROR_DEFAULT_TEXT,
                                                       reply_markup=keyboards.get_fuzz_variants_markup())


@change_data_router.callback_query(ChangeDataStates.CITY_NAME_IS_FUZZY, F.data == KeyboardCallbackData.DENY)
async def deny_city_variant(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(MenuStates.CHANGE_DATA, F.data == KeyboardCallbackData.REMOVE_CITY)
async def show_cities_as_inline_keyboard(callback_query: CallbackQuery, state: FSMContext,
                                         agent: UserServiceAgent) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return
    try:
        cities = await agent.get_user_cities(user_id)
        if len(cities) == 0:
            await callback_query.message.edit_text(text='У вас не указан ни один город',
                                                   reply_markup=keyboards.get_back_keyboard())
        else:
            await callback_query.message.edit_text(text='Выберите город, который нужно удалить',
                                                   reply_markup=keyboards.get_inline_keyboard_with_back(cities))
        await state.set_state(ChangeDataStates.REMOVE_CITY)
    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        await callback_query.message.edit_text(text=INTERNAL_ERROR_DEFAULT_TEXT,
                                               reply_markup=keyboards.get_back_keyboard())
        await state.set_state(ChangeDataStates.REMOVE_CITY)


@change_data_router.callback_query(ChangeDataStates.REMOVE_CITY, F.data == KeyboardCallbackData.BACK)
async def return_from_remove(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT,
                                           reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(ChangeDataStates.REMOVE_CITY, F.data != KeyboardCallbackData.BACK)
async def remove_city(callback_query: CallbackQuery, state: FSMContext, agent: UserServiceAgent) -> None:
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return
    city = callback_query.data
    if city is None:
        return
    bot = callback_query.bot
    if bot is None or callback_query.message is None:
        return

    try:
        await agent.delete_user_city(user_id, city)
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=f'Город {city} успешно удалён')
        msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                     reply_markup=keyboards.get_change_data_keyboard())
        await set_last_keyboard_id(msg.message_id, state)
        await state.set_state(MenuStates.CHANGE_DATA)
    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=INTERNAL_ERROR_DEFAULT_TEXT, reply_markup=None)
        msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                     reply_markup=keyboards.get_change_data_keyboard())
        await set_last_keyboard_id(msg.message_id, state)
        await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(MenuStates.CHANGE_DATA, F.data == KeyboardCallbackData.ADD_LINK)
async def add_one_playlist_show_msg(callback_query: CallbackQuery, state: FSMContext) -> None:
    bot = callback_query.bot
    if bot is None or callback_query is None or callback_query.message is None:
        return

    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                text='Введите ссылку на трек-лист',
                                reply_markup=keyboards.get_cancel_keyboard())
    await state.set_state(ChangeDataStates.ENTER_NEW_PLAYLIST)


@change_data_router.message(ChangeDataStates.ENTER_NEW_PLAYLIST, TEXT_WITHOUT_COMMANDS_FILTER)
async def add_one_playlist(message: Message, state: FSMContext, agent: UserServiceAgent) -> None:
    bot = message.bot
    if bot is None:
        return
    user_data = await state.get_data()
    link = message.text
    if link is None:
        await message.answer(text='Неверный формат текста')
        return
    if message.from_user is None:
        return
    user_id = message.from_user.id
    if user_id is None:
        return

    await bot.delete_message(chat_id=message.chat.id, message_id=get_last_keyboard_id(user_data))

    if len(link) > MAXIMUM_LINK_LEN:
        await message.answer(text='Слишком длинная ссылка')
        msg = await message.answer(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_change_data_keyboard())
        await set_last_keyboard_id(msg.message_id, state)
        await state.set_state(MenuStates.CHANGE_DATA)
        return

    try:
        track_list = await agent.add_user_track_list(user_id, link)
        await message.answer(text=f'Трек-лист {track_list.title} успешно добавлен')
    except TrackListAlreadyAddedException:
        await message.answer(text='Трек-лист уже был добавлен')
    except InvalidTrackListException:
        await message.answer(text='Ссылка недействительна')
    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)

    msg = await message.answer(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_change_data_keyboard())
    await set_last_keyboard_id(msg.message_id, state)
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(ChangeDataStates.ENTER_NEW_PLAYLIST, F.data == KeyboardCallbackData.CANCEL)
async def return_from_add_playlist(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(MenuStates.CHANGE_DATA, F.data == KeyboardCallbackData.REMOVE_LINK)
async def show_playlists_as_inline_keyboard(callback_query: CallbackQuery, state: FSMContext,
                                            agent: UserServiceAgent) -> None:
    if not isinstance(callback_query.message, Message):
        return
    bot = callback_query.bot
    if bot is None:
        return

    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return

    try:
        playlists = await agent.get_user_track_lists(user_id)
        if len(playlists) == 0:
            await callback_query.message.edit_text(text='У вас не указан ни один трек-лист',
                                                   reply_markup=keyboards.get_back_keyboard())
        else:
            text = 'Трек-листы'
            pos = 1
            for playlist in playlists:
                text += f'\n{pos}: {playlist.title}'
                pos += 1
            await bot.edit_message_text(text=text, chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id, reply_markup=None,
                                        disable_web_page_preview=True)
            await bot.send_message(chat_id=callback_query.message.chat.id,
                                   text='Выберите трек-лист, который нужно удалить',
                                   reply_markup=keyboards.get_inline_keyboard_for_playlists(
                                       playlists))
        await state.set_state(ChangeDataStates.REMOVE_PLAYLIST)
    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        await callback_query.message.edit_text(text=INTERNAL_ERROR_DEFAULT_TEXT,
                                               reply_markup=keyboards.get_back_keyboard())
        await state.set_state(ChangeDataStates.REMOVE_PLAYLIST)


@change_data_router.callback_query(ChangeDataStates.REMOVE_PLAYLIST, F.data == KeyboardCallbackData.BACK)
async def return_from_remove_playlist(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT,
                                           reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(ChangeDataStates.REMOVE_PLAYLIST, F.data != KeyboardCallbackData.BACK)
async def remove_playlist(callback_query: CallbackQuery, state: FSMContext, agent: UserServiceAgent) -> None:
    playlist = callback_query.data
    if playlist is None:
        return
    bot = callback_query.bot
    if bot is None or callback_query.message is None:
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return
    try:
        await agent.delete_user_track_list(user_id, playlist)
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=f'Трек-лист успешно удалён', reply_markup=None)

        msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                     reply_markup=keyboards.get_change_data_keyboard())
        await set_last_keyboard_id(msg.message_id, state)
        await state.set_state(MenuStates.CHANGE_DATA)
    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=INTERNAL_ERROR_DEFAULT_TEXT, reply_markup=None)
        msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                     reply_markup=keyboards.get_change_data_keyboard())
        await state.update_data(last_keyboard_id=msg.message_id)
        await state.set_state(MenuStates.CHANGE_DATA)
