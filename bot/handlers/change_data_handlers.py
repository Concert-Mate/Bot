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

bot_logger = logging.getLogger('bot')


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
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return
    bot_logger.info(f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
                    f' on state:{await state.get_state()} for show_change_data_variants')
    await state.set_state(MenuStates.MAIN_MENU)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_main_menu_keyboard())


@change_data_router.callback_query(MenuStates.CHANGE_DATA, F.data == KeyboardCallbackData.ADD_CITY)
async def add_city_text_send(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return
    bot_logger.info(f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
                    f' on state:{await state.get_state()} for add_city_text_send')

    await state.set_state(ChangeDataStates.ENTER_NEW_CITY)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text='Введите название города',
                                               reply_markup=keyboards.get_cancel_keyboard())


@change_data_router.message(MenuStates.CHANGE_DATA)
async def resent(message: Message, state: FSMContext) -> None:
    bot = message.bot
    if bot is None:
        return
    user_data = await state.get_data()

    if message.from_user is None:
        return
    user_id = message.from_user.id
    if user_id is None:
        return
    bot_logger.info(f'Got message {message.message_id} from {user_id}-{message.from_user.username}'
                    f' on state:{await state.get_state()} for resent')

    with suppress(TelegramBadRequest):
        await bot.delete_message(chat_id=message.chat.id, message_id=get_last_keyboard_id(user_data))

    msg = await bot.send_message(chat_id=message.chat.id, text=CHOOSE_ACTION_TEXT,
                                 reply_markup=keyboards.get_change_data_keyboard())
    await set_last_keyboard_id(msg.message_id, state)


@change_data_router.callback_query(ChangeDataStates.ENTER_NEW_CITY, F.data == KeyboardCallbackData.CANCEL)
async def cancel_add_city(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return
    bot_logger.info(f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
                    f' on state:{await state.get_state()} for cancel_add_city')
    await state.set_state(MenuStates.CHANGE_DATA)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT,
                                               reply_markup=keyboards.get_change_data_keyboard())


@change_data_router.message(ChangeDataStates.ENTER_NEW_CITY, TEXT_WITHOUT_COMMANDS_FILTER)
async def add_one_city(message: Message, state: FSMContext, agent: UserServiceAgent) -> None:
    if message.from_user is None:
        return
    user_id = message.from_user.id
    if user_id is None:
        return
    bot = message.bot
    if bot is None:
        return
    city = message.text

    bot_logger.info(f'Got message {message.message_id} from {user_id}-{message.from_user.username}'
                    f' on state:{await state.get_state()} for add_one_city. City:{city}')

    if city is None:
        await message.answer(text='Неверный формат текста')

        return

    user_data = await state.get_data()

    await state.set_state(MenuStates.WAITING)
    with suppress(TelegramBadRequest):
        await bot.delete_message(chat_id=message.chat.id, message_id=get_last_keyboard_id(user_data))

    if len(city) > MAXIMUM_CITY_LEN:
        await message.answer(text='Слишком длинное название города')
        bot_logger.debug(f'Too long city name for {message.message_id} of'
                         f' {user_id}-{message.from_user.username}')
        msg = await message.answer(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_change_data_keyboard())
        await set_last_keyboard_id(msg.message_id, state)
        await state.set_state(MenuStates.CHANGE_DATA)
        return

    try:
        await agent.add_user_city(user_id, city)
        await message.answer(text=f'Город {city} добавлен успешно.')
        bot_logger.info(f'Successfully city {city} added for {message.message_id} of'
                        f' {user_id}-{message.from_user.username}')
    except InvalidCityException:
        await message.answer(text='Некорректно введен город или его не существует')
        bot_logger.debug(f'Get incorrect city for {message.message_id} of'
                         f' {user_id}-{message.from_user.username}')
    except FuzzyCityException as e:
        if e.variant is not None:
            bot_logger.debug(f'Get fuzzy city with variant:{e.variant} for {message.message_id} of'
                             f' {user_id}-{message.from_user.username}')
            await __send_fuzz_variant_message(city, e.variant, message, state)
            return
        else:
            bot_logger.warning(f'Get fuzzy without variant for {message.message_id} of'
                               f' {user_id}-{message.from_user.username}')
            await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)
    except CityAlreadyAddedException:
        await message.answer(text='Город уже был добавлен')
        bot_logger.debug(f'City already added for {message.message_id} of'
                         f' {user_id}-{message.from_user.username}')
    except Exception as e:
        bot_logger.warning(f'On {message.message_id} for {user_id}-{message.from_user.username}: {str(e)}')
        await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)

    msg = await message.answer(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_change_data_keyboard())
    await set_last_keyboard_id(msg.message_id, state)
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(ChangeDataStates.CITY_NAME_IS_FUZZY, F.data == KeyboardCallbackData.APPLY)
async def apply_city_variant(callback_query: CallbackQuery, state: FSMContext, agent: UserServiceAgent) -> None:
    if callback_query.from_user is None:
        return
    if callback_query.message is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return
    bot = callback_query.bot
    if bot is None:
        return

    bot_logger.info(f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
                    f' on state:{await state.get_state()} for apply_city_variant')

    await state.set_state(MenuStates.WAITING)

    user_data = await state.get_data()
    city = user_data['variant']
    try:
        await agent.add_user_city(user_id, city)

        bot_logger.info(f'Successfully added city:{city} for {callback_query.message.message_id} of'
                        f' {user_id}-{callback_query.from_user.username}')

        with suppress(TelegramBadRequest):
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, text='Город успешно добавлен',
                                        message_id=callback_query.message.message_id, reply_markup=None)
        msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                     reply_markup=keyboards.get_change_data_keyboard())
        await set_last_keyboard_id(msg.message_id, state)

        user_data = await state.get_data()
        user_data.pop('variant')
        await state.set_data(user_data)
        await state.set_state(MenuStates.CHANGE_DATA)

    except CityAlreadyAddedException:

        bot_logger.debug(f'City already added for {callback_query.message.message_id} of'
                         f' {user_id}-{callback_query.from_user.username}')

        with suppress(TelegramBadRequest):
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, text='Город уже был добавлен',
                                        message_id=callback_query.message.message_id, reply_markup=None)
        msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                     reply_markup=keyboards.get_change_data_keyboard())
        await set_last_keyboard_id(msg.message_id, state)
        user_data = await state.get_data()
        user_data.pop('variant')
        await state.set_data(user_data)
        await state.set_state(MenuStates.CHANGE_DATA)
    except Exception as e:
        bot_logger.warning(f'On {callback_query.message.message_id}'
                           f' for {user_id}-{callback_query.from_user.username}: {str(e)}')
        with suppress(TelegramBadRequest):
            if isinstance(callback_query.message, Message):
                await callback_query.message.edit_text(text=INTERNAL_ERROR_DEFAULT_TEXT,
                                                       reply_markup=keyboards.get_fuzz_variants_markup())


@change_data_router.callback_query(ChangeDataStates.CITY_NAME_IS_FUZZY, F.data == KeyboardCallbackData.DENY)
async def deny_city_variant(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return
    bot_logger.info(f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
                    f' on state:{await state.get_state()} for deny_city_variant')
    await state.set_state(MenuStates.CHANGE_DATA)

    user_data = await state.get_data()
    user_data.pop('variant')
    await state.set_data(user_data)

    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT,
                                               reply_markup=keyboards.get_change_data_keyboard())


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

    bot_logger.info(f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
                    f' on state:{await state.get_state()} for show_cities_as_inline_keyboard')

    await state.set_state(MenuStates.WAITING)
    try:
        cities = await agent.get_user_cities(user_id)
        bot_logger.info(f'Got cities:{cities} for {callback_query.message.message_id} of'
                        f' {user_id}-{callback_query.from_user.username}')
        if len(cities) == 0:
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(text='У вас не указан ни один город',
                                                       reply_markup=keyboards.get_back_keyboard())
        else:
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(text='Выберите город, который нужно удалить',
                                                       reply_markup=keyboards.get_inline_keyboard_with_back(cities))
        await state.set_state(ChangeDataStates.REMOVE_CITY)
    except Exception as e:
        bot_logger.warning(f'On {callback_query.message.message_id}'
                           f' for {user_id}-{callback_query.from_user.username}: {str(e)}')
        with suppress(TelegramBadRequest):
            await callback_query.message.edit_text(text=INTERNAL_ERROR_DEFAULT_TEXT,
                                                   reply_markup=keyboards.get_back_keyboard())
        await state.set_state(ChangeDataStates.REMOVE_CITY)


@change_data_router.callback_query(ChangeDataStates.REMOVE_CITY, F.data == KeyboardCallbackData.BACK)
async def return_from_remove(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return
    bot_logger.info(f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
                    f' on state:{await state.get_state()} for return_from_remove')
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT,
                                               reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(ChangeDataStates.REMOVE_CITY, F.data != KeyboardCallbackData.BACK)
async def remove_city(callback_query: CallbackQuery, state: FSMContext, agent: UserServiceAgent) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return
    city = callback_query.data
    if city is None:
        return

    bot_logger.info(f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
                    f' on state:{await state.get_state()} for remove_city. Remove city: {city}')

    bot = callback_query.bot
    if bot is None or callback_query.message is None:
        return

    try:
        await agent.delete_user_city(user_id, city)
        bot_logger.info(f'Successfully removed city:{city} for {callback_query.message.message_id} of'
                        f' {user_id}-{callback_query.from_user.username}')
        with suppress(TelegramBadRequest):
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        text=f'Город {city} успешно удалён')

        msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                     reply_markup=keyboards.get_change_data_keyboard())
        await set_last_keyboard_id(msg.message_id, state)
        await state.set_state(MenuStates.CHANGE_DATA)
    except Exception as e:
        bot_logger.warning(f'On {callback_query.message.message_id}'
                           f' for {user_id}-{callback_query.from_user.username}: {str(e)}')

        with suppress(TelegramBadRequest):
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
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user
    if user_id is None:
        return
    bot_logger.info(f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
                    f' on state:{await state.get_state()} for add_one_playlist_show_msg')

    await state.set_state(ChangeDataStates.ENTER_NEW_PLAYLIST)
    with suppress(TelegramBadRequest):
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Введите ссылку на трек-лист',
                                    reply_markup=keyboards.get_cancel_keyboard())


@change_data_router.message(ChangeDataStates.ENTER_NEW_PLAYLIST, TEXT_WITHOUT_COMMANDS_FILTER)
async def add_one_playlist(message: Message, state: FSMContext, agent: UserServiceAgent) -> None:
    bot = message.bot
    if bot is None:
        return
    user_data = await state.get_data()
    link = message.text
    if message.from_user is None:
        return
    user_id = message.from_user.id
    if user_id is None:
        return
    bot_logger.info(f'Got message {message.message_id} from {user_id}-{message.from_user.username}'
                    f' on state:{await state.get_state()} for add_one_playlist. Link: {link}')
    if link is None:
        await message.answer(text='Неверный формат текста')
        bot_logger.debug(f'Incorrect text format for {message.message_id} of'
                         f' {user_id}-{message.from_user.username}')
        return
    with suppress(TelegramBadRequest):
        await bot.delete_message(chat_id=message.chat.id, message_id=get_last_keyboard_id(user_data))
    await state.set_state(MenuStates.WAITING)
    if len(link) > MAXIMUM_LINK_LEN:
        await message.answer(text='Слишком длинная ссылка')
        bot_logger.debug(f'Too long link for {message.message_id} of'
                         f' {user_id}-{message.from_user.username}')
        msg = await message.answer(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_change_data_keyboard())
        await set_last_keyboard_id(msg.message_id, state)
        await state.set_state(MenuStates.CHANGE_DATA)
        return

    try:
        track_list = await agent.add_user_track_list(user_id, link)
        bot_logger.debug(f'Successfully added track-list:{track_list} for {message.message_id} of'
                         f' {user_id}-{message.from_user.username}')
        await message.answer(text=f'Трек-лист {track_list.title} успешно добавлен')
    except TrackListAlreadyAddedException:
        await message.answer(text='Трек-лист уже был добавлен')
        bot_logger.debug(f'Track-list already added for {message.message_id} of'
                         f' {user_id}-{message.from_user.username}')
    except InvalidTrackListException:
        await message.answer(text='Ссылка недействительна')
        bot_logger.debug(f'Invalid track-list for {message.message_id} of'
                         f' {user_id}-{message.from_user.username}')
    except Exception as e:
        bot_logger.warning(f'On {message.message_id} for {user_id}-{message.from_user.username}: {str(e)}')
        await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)

    msg = await message.answer(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_change_data_keyboard())
    await set_last_keyboard_id(msg.message_id, state)
    await state.set_state(MenuStates.CHANGE_DATA)


@change_data_router.callback_query(ChangeDataStates.ENTER_NEW_PLAYLIST, F.data == KeyboardCallbackData.CANCEL)
async def return_from_add_playlist(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return
    bot_logger.info(f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
                    f' on state:{await state.get_state()} for return_from_add_playlist')
    await state.set_state(MenuStates.CHANGE_DATA)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT,
                                               reply_markup=keyboards.get_change_data_keyboard())


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

    bot_logger.info(f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
                    f' on state:{await state.get_state()} for show_playlists_as_inline_keyboard')

    await state.set_state(MenuStates.WAITING)
    try:
        playlists = await agent.get_user_track_lists(user_id)
        bot_logger.debug(f'Got track-lists:{playlists} for {callback_query.message.message_id} of'
                         f' {user_id}-{callback_query.from_user.username}')
        if len(playlists) == 0:
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(text='У вас не указан ни один трек-лист',
                                                       reply_markup=keyboards.get_back_keyboard())
        else:
            text = 'Трек-листы'
            pos = 1
            for playlist in playlists:
                text += f'\n{pos}: {playlist.title}'
                pos += 1
            with suppress(TelegramBadRequest):
                await bot.edit_message_text(text=text, chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id, reply_markup=None,
                                            disable_web_page_preview=True)
            msg = await bot.send_message(chat_id=callback_query.message.chat.id,
                                         text='Выберите трек-лист, который нужно удалить',
                                         reply_markup=keyboards.get_inline_keyboard_for_playlists(
                                             playlists))
            await set_last_keyboard_id(msg.message_id, state)
        await state.set_state(ChangeDataStates.REMOVE_PLAYLIST)
    except Exception as e:
        bot_logger.warning(f'On {callback_query.message.message_id}'
                           f' for {user_id}-{callback_query.from_user.username}: {str(e)}')
        with suppress(TelegramBadRequest):
            await callback_query.message.edit_text(text=INTERNAL_ERROR_DEFAULT_TEXT,
                                                   reply_markup=keyboards.get_back_keyboard())
        await state.set_state(ChangeDataStates.REMOVE_PLAYLIST)


@change_data_router.callback_query(ChangeDataStates.REMOVE_PLAYLIST, F.data == KeyboardCallbackData.BACK)
async def return_from_remove_playlist(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return
    bot_logger.info(f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
                    f' on state:{await state.get_state()} for return_from_remove_playlist')
    await state.set_state(MenuStates.CHANGE_DATA)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT,
                                               reply_markup=keyboards.get_change_data_keyboard())


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

    bot_logger.info(f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
                    f' on state:{await state.get_state()} for remove_playlist. Playlist:{playlist}')

    await state.set_state(MenuStates.WAITING)
    try:
        await agent.delete_user_track_list(user_id, playlist)
        bot_logger.debug(f'Successfully removed track-list:{playlist} for {callback_query.message.message_id} of'
                         f' {user_id}-{callback_query.from_user.username}')
        with suppress(TelegramBadRequest):
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        text=f'Трек-лист успешно удалён', reply_markup=None)

        msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                     reply_markup=keyboards.get_change_data_keyboard())
        await set_last_keyboard_id(msg.message_id, state)
        await state.set_state(MenuStates.CHANGE_DATA)
    except Exception as e:
        bot_logger.warning(f'On {callback_query.message.message_id}'
                           f' for {user_id}-{callback_query.from_user.username}: {str(e)}')

        with suppress(TelegramBadRequest):
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        text=INTERNAL_ERROR_DEFAULT_TEXT, reply_markup=None)

        msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                     reply_markup=keyboards.get_change_data_keyboard())
        await state.update_data(last_keyboard_id=msg.message_id)
        await state.set_state(MenuStates.CHANGE_DATA)
