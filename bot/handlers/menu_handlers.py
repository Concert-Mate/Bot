import json
import logging
from contextlib import suppress
from typing import List

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis

from bot import keyboards
from bot.keyboards import KeyboardCallbackData
from bot.states import MenuStates
from concert_message_builder import get_date_time
from services.user_service import UserServiceAgent
from .cache_models import CachePlaylists, CacheCities, CacheConcerts
from .constants import INTERNAL_ERROR_DEFAULT_TEXT, CHOOSE_ACTION_TEXT, ABOUT_TEXT, FAQ_TEXT, DEV_COMM_TEXT, \
    INSTRUCTION_PHOTO_LINK
from .user_data_manager import set_last_keyboard_id, get_last_keyboard_id

menu_router = Router()

bot_logger = logging.getLogger('bot')


async def __check_user_and_logging(callback_query: CallbackQuery, func_name: str, state: FSMContext) -> bool:
    if not isinstance(callback_query.message, Message):
        return False
    if callback_query.from_user is None:
        return False
    user_id = callback_query.from_user.id
    if user_id is None:
        return False

    bot_logger.info(
        f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
        f' on state:{await state.get_state()} for {func_name}')
    return True


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == KeyboardCallbackData.CHANGE_DATA)
async def show_change_data_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if not await __check_user_and_logging(callback_query, 'show_change_data_variants', state):
        return

    await state.set_state(MenuStates.CHANGE_DATA)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT,
                                               reply_markup=keyboards.get_change_data_keyboard())


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == KeyboardCallbackData.HELP)
async def show_help_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return

    if not await __check_user_and_logging(callback_query, 'show_help_variants', state):
        return
    await state.set_state(MenuStates.HELP)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_help_keyboard())


@menu_router.callback_query(MenuStates.HELP, F.data == KeyboardCallbackData.MAIN_INFO)
async def show_main_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return

    if not await __check_user_and_logging(callback_query, 'show_main_info', state):
        return

    await state.set_state(MenuStates.HELP_DEAD_END)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=ABOUT_TEXT,
                                               reply_markup=keyboards.get_back_keyboard())


@menu_router.callback_query(MenuStates.HELP, F.data == KeyboardCallbackData.DEVELOPMENT_COMMUNICATION)
async def show_dev_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return

    if not await __check_user_and_logging(callback_query, 'show_dev_info', state):
        return

    await state.set_state(MenuStates.HELP_DEAD_END)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=DEV_COMM_TEXT,
                                               reply_markup=keyboards.get_back_keyboard(),
                                               parse_mode=ParseMode.HTML,
                                               disable_web_page_preview=True)


@menu_router.callback_query(MenuStates.HELP, F.data == KeyboardCallbackData.FAQ)
async def show_faq_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return

    if not await __check_user_and_logging(callback_query, 'show_faq_info', state):
        return
    bot = callback_query.bot
    if bot is None:
        return

    user_data = await state.get_data()

    await state.set_state(MenuStates.HELP_DEAD_END)
    with suppress(TelegramBadRequest):
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=get_last_keyboard_id(user_data))
    try:
        await bot.send_photo(chat_id=callback_query.message.chat.id,
                             photo=INSTRUCTION_PHOTO_LINK,
                             caption='Инструкция как получить ссылку на альбом/плейлист')
    except Exception as e:
        bot_logger.warning(f'Failed to send photo from'
                           f' {callback_query.from_user.id}-{callback_query.from_user.username}'
                           f' on state:{await state.get_state()}. {str(e)}')

    msg = await bot.send_message(chat_id=callback_query.message.chat.id,
                                 text=FAQ_TEXT,
                                 reply_markup=keyboards.get_back_keyboard(),
                                 parse_mode=ParseMode.HTML)
    await set_last_keyboard_id(msg.message_id, state)


@menu_router.callback_query(MenuStates.HELP, F.data == KeyboardCallbackData.BACK)
async def go_to_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if not await __check_user_and_logging(callback_query, 'go_to_menu', state):
        return
    await state.set_state(MenuStates.MAIN_MENU)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_main_menu_keyboard())


@menu_router.callback_query(MenuStates.HELP_DEAD_END, F.data == KeyboardCallbackData.BACK)
async def go_to_faq(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return

    if not await __check_user_and_logging(callback_query, 'go_to_faq', state):
        return

    await state.set_state(MenuStates.HELP)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_help_keyboard())


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == KeyboardCallbackData.USER_INFO)
async def show_user_info_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if not await __check_user_and_logging(callback_query, 'show_user_info_variants', state):
        return
    await state.set_state(MenuStates.USER_INFO)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_user_info_keyboard())


@menu_router.callback_query(MenuStates.USER_INFO, F.data == KeyboardCallbackData.CITIES)
async def show_cities(callback_query: CallbackQuery, state: FSMContext, agent: UserServiceAgent,
                      redis_storage: Redis) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return

    bot_logger.info(
        f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
        f' on state:{await state.get_state()} for show_cities')

    await state.set_state(MenuStates.WAITING)
    await callback_query.answer()
    from_cache = await redis_storage.get(name=f'{user_id}:cities')
    if from_cache is not None:
        try:
            cities = CacheCities.model_validate_json(from_cache).cities
            bot_logger.debug(f'Got cities:{cities} from cache for {callback_query.message.message_id} of'
                             f' {user_id}-{callback_query.from_user.username}')
            if len(cities) == 0:
                with suppress(TelegramBadRequest):
                    await callback_query.message.edit_text(text='У вас не указан ни один город',
                                                           reply_markup=keyboards.get_back_keyboard())
            else:
                txt = 'Ваши города:'
                for pos, city in enumerate(cities):
                    txt += f'\n{pos + 1}.{city}'

                with suppress(TelegramBadRequest):
                    await callback_query.message.edit_text(text=txt, reply_markup=keyboards.get_back_keyboard())

            await state.set_state(MenuStates.USER_INFO_DEAD_END)
            return
        except Exception as e:
            bot_logger.debug(f'Caching cities (no data) error for {callback_query.message.message_id} of'
                             f' {user_id}-{callback_query.from_user.username}. {str(e)}')

    try:
        cities = await agent.get_user_cities(user_id)

        json_str = json.dumps({'cities': cities})
        await redis_storage.set(name=f'{user_id}:cities', value=json_str, ex=120)
        bot_logger.debug(f'Set cities cache for {callback_query.message.message_id} of'
                         f' {user_id}-{callback_query.from_user.username}')

        bot_logger.info(f'Got cities:{cities} for {callback_query.message.message_id} of'
                        f' {user_id}-{callback_query.from_user.username}')
        if len(cities) == 0:
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(text='У вас не указан ни один город',
                                                       reply_markup=keyboards.get_back_keyboard())
        else:
            txt = 'Ваши города:'
            for pos, city in enumerate(cities):
                txt += f'\n{pos + 1}.{city}'

            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(text=txt, reply_markup=keyboards.get_back_keyboard())

    except Exception as e:
        bot_logger.warning(f'On {callback_query.message.message_id}'
                           f' for {user_id}-{callback_query.from_user.username}: {str(e)}')
        with suppress(TelegramBadRequest):
            await callback_query.message.edit_text(text=INTERNAL_ERROR_DEFAULT_TEXT,
                                                   reply_markup=keyboards.get_back_keyboard())

    await state.set_state(MenuStates.USER_INFO_DEAD_END)


@menu_router.callback_query(MenuStates.USER_INFO, F.data == KeyboardCallbackData.LINKS)
async def show_all_links(callback_query: CallbackQuery, state: FSMContext, agent: UserServiceAgent,
                         redis_storage: Redis) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return

    bot_logger.info(
        f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
        f' on state:{await state.get_state()} for show_all_links')

    await state.set_state(MenuStates.WAITING)
    await callback_query.answer()
    from_cache = await redis_storage.get(name=f'{user_id}:track-lists')
    if from_cache is not None:
        try:
            playlists = CachePlaylists.model_validate_json(from_cache).track_lists

            bot_logger.debug(f'Got playlists:{playlists} from cache for {callback_query.message.message_id} of'
                             f' {user_id}-{callback_query.from_user.username}')
            if len(playlists) == 0:
                with suppress(TelegramBadRequest):
                    await callback_query.message.edit_text(text='У вас не указан ни один трек-лист',
                                                           reply_markup=keyboards.get_back_keyboard())
            else:
                txt = 'Ваши трек-листы:'
                for pos, playlist in enumerate(playlists):
                    txt += f'\n{pos + 1}.<a href=\"{playlist.url}\">{playlist.title}</a>'
                with suppress(TelegramBadRequest):
                    await callback_query.message.edit_text(text=txt, reply_markup=keyboards.get_back_keyboard(),
                                                           disable_web_page_preview=True,
                                                           parse_mode=ParseMode.HTML)

            await state.set_state(MenuStates.USER_INFO_DEAD_END)
            return
        except Exception as e:
            bot_logger.debug(f'Caching track-lists (no data) error for {callback_query.message.message_id} of'
                             f' {user_id}-{callback_query.from_user.username}. {str(e)}')

    try:
        playlists = await agent.get_user_track_lists(user_id)
        bot_logger.info(f'Got links:{playlists} on {callback_query.message.message_id}'
                        f' for {user_id}-{callback_query.from_user.username}')
        to_json_model = CachePlaylists(track_lists=playlists)
        json_str = to_json_model.model_dump_json()
        await redis_storage.set(name=f'{user_id}:track-lists', value=json_str, ex=120)
        bot_logger.debug(f'Set playlists cache for {callback_query.message.message_id} of'
                         f' {user_id}-{callback_query.from_user.username}')

        if len(playlists) == 0:
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(text='У вас не указан ни один трек-лист',
                                                       reply_markup=keyboards.get_back_keyboard())
        else:
            txt = 'Ваши трек-листы:'
            for pos, playlist in enumerate(playlists):
                txt += f'\n{pos + 1}.<a href=\"{playlist.url}\">{playlist.title}</a>'
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(text=txt, reply_markup=keyboards.get_back_keyboard(),
                                                       disable_web_page_preview=True,
                                                       parse_mode=ParseMode.HTML)
    except Exception as e:
        bot_logger.warning(f'On {callback_query.message.message_id}'
                           f' for {user_id}-{callback_query.from_user.username}: {str(e)}')
        with suppress(TelegramBadRequest):
            await callback_query.message.edit_text(text=INTERNAL_ERROR_DEFAULT_TEXT,
                                                   reply_markup=keyboards.get_back_keyboard())

    await state.set_state(MenuStates.USER_INFO_DEAD_END)


@menu_router.callback_query(MenuStates.USER_INFO_DEAD_END, F.data == KeyboardCallbackData.BACK)
async def go_to_faq_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if not await __check_user_and_logging(callback_query, 'go_to_faq_info', state):
        return
    await state.set_state(MenuStates.USER_INFO)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_user_info_keyboard())


@menu_router.callback_query(MenuStates.USER_INFO, F.data == KeyboardCallbackData.BACK)
async def show_change_data_variants_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if not await __check_user_and_logging(callback_query, 'show_change_data_variants_info', state):
        return
    await state.set_state(MenuStates.MAIN_MENU)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_main_menu_keyboard())


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == KeyboardCallbackData.TOOLS)
async def show_tools(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if not await __check_user_and_logging(callback_query, 'show_tools', state):
        return
    await state.set_state(MenuStates.TOOLS)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_tools_keyboard())


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == KeyboardCallbackData.SHOW_CONCERTS)
async def show_all_concerts(callback_query: CallbackQuery, state: FSMContext, agent: UserServiceAgent,
                            redis_storage: Redis) -> None:
    if not isinstance(callback_query.message, Message):
        return
    bot = callback_query.bot
    if bot is None or callback_query is None or callback_query.message is None:
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return

    bot_logger.info(
        f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
        f' on state:{await state.get_state()} for show_all_concerts')

    with suppress(TelegramBadRequest):
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await state.set_state(MenuStates.WAITING)

    concerts_list = []

    from_cache = await redis_storage.get(name=f'{user_id}:concerts')
    if from_cache is not None:
        try:
            concerts_list = CacheConcerts.model_validate_json(from_cache).concerts
            if len(concerts_list) == 0:
                await bot.send_message(chat_id=callback_query.message.chat.id, text='Концерты не обнаружены')
                msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                             reply_markup=keyboards.get_main_menu_keyboard())

                await set_last_keyboard_id(msg.message_id, state)
                await state.set_state(MenuStates.MAIN_MENU)
                return

            await state.update_data(concerts=concerts_list)
            await state.update_data(current_page=0)

            page_txt = ''
            for i in range(0, 5):
                if i == len(concerts_list):
                    break
                page_txt += f'{i + 1}\n{concerts_list[i]}\n\n'
            all_pages = len(concerts_list) // 5
            if len(concerts_list) % 5 != 0:
                all_pages += 1
            page_txt += f'Страница 1 из {all_pages}'
            await state.set_state(MenuStates.CONCERTS_SHOW)
            msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=page_txt,
                                         reply_markup=keyboards.get_show_concerts_keyboard(),
                                         parse_mode=ParseMode.HTML,
                                         disable_web_page_preview=True)
            await set_last_keyboard_id(msg.message_id, state)
            return
        except Exception as e:
            bot_logger.debug(f'Caching track-lists (no data) error for {callback_query.message.message_id} of'
                             f' {user_id}-{callback_query.from_user.username}. {str(e)}')

    try:
        await bot.send_chat_action(chat_id=callback_query.message.chat.id, action='typing')
        concerts = await agent.get_user_concerts(user_id)
        bot_logger.debug(f'Got concerts for {callback_query.message.message_id} of'
                         f' {user_id}-{callback_query.from_user.username}')

        for pos, concert in enumerate(concerts):
            txt = ''

            if len(concert.artists) != 1 or concert.artists[0].name != concert.title:
                txt += f'Название: <i>{concert.title}</i>\n'

            if len(concert.artists) == 1:
                txt += 'Исполнитель:'
            else:
                txt += 'Исполнители:'

            for artist in concert.artists:
                txt += f' {artist.name},'
            txt = txt[:-1]
            if concert.map_url is None:
                txt += (f'\nМесто: город <b>{concert.city}</b>,'
                        f' адрес <b>{concert.address}</b>\n')
            else:
                txt += (f'\nМесто: город <b>{concert.city}</b>,'
                        f' адрес <a href=\"{concert.map_url}\"><b>{concert.address}</b></a>\n')
            if concert.place is not None:
                txt += f'в <i>{concert.place}</i>\n'
            else:
                txt += '\n'

            if concert.concert_datetime is not None:
                txt += f'Время: {get_date_time(concert.concert_datetime, True)}\n'
            if concert.min_price is not None:
                txt += (f'Минимальная цена билета: <b>{concert.min_price.price}</b>'
                        f' <b>{concert.min_price.currency}</b>\n')
            txt += f'Купить билет можно <a href=\"{concert.afisha_url}\">здесь</a>'
            concerts_list.append(txt)

        json_model = CacheConcerts(concerts=concerts_list)
        json_str = json_model.model_dump_json()
        await redis_storage.set(name=f'{user_id}:concerts', value=json_str, ex=300)
        bot_logger.debug(f'Cached concerts for {callback_query.message.message_id} of'
                         f' {user_id}-{callback_query.from_user.username}')

        if len(concerts) == 0:
            await bot.send_message(chat_id=callback_query.message.chat.id, text='Концерты не обнаружены')
            msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                         reply_markup=keyboards.get_main_menu_keyboard())

            await set_last_keyboard_id(msg.message_id, state)
            await state.set_state(MenuStates.MAIN_MENU)
            return

        await state.update_data(concerts=concerts_list)
        await state.update_data(current_page=0)

        page_txt = ''
        for i in range(0, 5):
            if i == len(concerts_list):
                break
            page_txt += f'{i + 1}\n{concerts_list[i]}\n\n'
        all_pages = len(concerts_list) // 5
        if len(concerts_list) % 5 != 0:
            all_pages += 1
        page_txt += f'Страница 1 из {all_pages}'
        await state.set_state(MenuStates.CONCERTS_SHOW)
        msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=page_txt,
                                     reply_markup=keyboards.get_show_concerts_keyboard(),
                                     parse_mode=ParseMode.HTML,
                                     disable_web_page_preview=True)
        await set_last_keyboard_id(msg.message_id, state)

    except Exception as e:
        bot_logger.warning(f'On {callback_query.message.message_id}'
                           f' for {user_id}-{callback_query.from_user.username}: {str(e)}')
        await bot.send_message(chat_id=callback_query.message.chat.id, text=INTERNAL_ERROR_DEFAULT_TEXT)
        msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                     reply_markup=keyboards.get_main_menu_keyboard())

        await set_last_keyboard_id(msg.message_id, state)
        await state.set_state(MenuStates.MAIN_MENU)


@menu_router.callback_query(MenuStates.CONCERTS_SHOW, F.data == KeyboardCallbackData.BACK)
async def return_from_show_concerts(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if not await __check_user_and_logging(callback_query, 'return_from_show_concerts', state):
        return
    if callback_query.message is None:
        return
    await state.set_state(MenuStates.MAIN_MENU)
    user_data = await state.get_data()
    user_data.pop('current_page')
    user_data.pop('concerts')
    await state.set_data(user_data)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_main_menu_keyboard())


@menu_router.callback_query(MenuStates.CONCERTS_SHOW, F.data == KeyboardCallbackData.BACKWARD)
@menu_router.callback_query(MenuStates.CONCERTS_SHOW, F.data == KeyboardCallbackData.FORWARD)
async def show_concerts_page(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return

    bot_logger.info(
        f'Got message {callback_query.message.message_id} from {user_id}-{callback_query.from_user.username}'
        f' on state:{await state.get_state()} for show_concert_page')
    user_data = await state.get_data()
    current_page = user_data['current_page']
    concerts: List[str] = user_data['concerts']
    if callback_query.data == KeyboardCallbackData.BACKWARD:
        current_page -= 1
    else:
        current_page += 1

    if current_page < 0:
        current_page = len(concerts) // 5
        if len(concerts) % 5 == 0 and current_page > 0:
            current_page -= 1
    elif current_page * 5 >= len(concerts):
        current_page = 0

    page_txt = ''
    for i in range(current_page * 5, current_page * 5 + 5):
        if i == len(concerts):
            break
        page_txt += f'{i + 1}\n{concerts[i]}\n\n'

    all_pages = len(concerts) // 5
    if len(concerts) % 5 != 0:
        all_pages += 1
    page_txt += f'Страница {current_page + 1} из {all_pages}'

    bot_logger.debug(
        f'Showing page {current_page + 1} of {all_pages} for {callback_query.message.message_id}'
        f' from {user_id}-{callback_query.from_user.username}')

    await state.update_data(current_page=current_page)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=page_txt,
                                               reply_markup=keyboards.get_show_concerts_keyboard(),
                                               parse_mode=ParseMode.HTML,
                                               disable_web_page_preview=True
                                               )


@menu_router.callback_query(MenuStates.TOOLS, F.data == KeyboardCallbackData.BACK)
async def go_to_menu_tools(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if not await __check_user_and_logging(callback_query, 'go_to_menu_tools', state):
        return
    await state.set_state(MenuStates.MAIN_MENU)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_main_menu_keyboard())


@menu_router.callback_query(MenuStates.TOOLS, F.data == KeyboardCallbackData.NOTICE_MANAGEMENT)
async def show_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if not await __check_user_and_logging(callback_query, 'show_variants', state):
        return
    user_data = await state.get_data()
    await state.set_state(MenuStates.MANAGING_NOTIFICATIONS)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT,
                                               reply_markup=keyboards.
                                               get_notify_management_keyboard(user_data['notices_enabled']))


@menu_router.callback_query(MenuStates.MANAGING_NOTIFICATIONS, F.data == KeyboardCallbackData.ENABLE)
async def swap_notice_enable(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if not await __check_user_and_logging(callback_query, 'swap_notice_enable', state):
        return
    user_data = await state.get_data()
    user_data['notices_enabled'] = True
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT,
                                               reply_markup=keyboards.
                                               get_notify_management_keyboard(True))


@menu_router.callback_query(MenuStates.MANAGING_NOTIFICATIONS, F.data == KeyboardCallbackData.DISABLE)
async def swap_notice_enable_disable(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if not await __check_user_and_logging(callback_query, 'show_notice_enable_disable', state):
        return
    user_data = await state.get_data()
    user_data['notices_enabled'] = False
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT,
                                               reply_markup=keyboards.
                                               get_notify_management_keyboard(False))


@menu_router.callback_query(MenuStates.MANAGING_NOTIFICATIONS, F.data == KeyboardCallbackData.BACK)
async def go_to_tools(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if not await __check_user_and_logging(callback_query, 'go_to_tools', state):
        return
    await state.set_state(MenuStates.TOOLS)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_tools_keyboard())
