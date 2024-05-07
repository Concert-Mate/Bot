import logging
from asyncio import sleep
from contextlib import suppress

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import keyboards
from bot.keyboards import KeyboardCallbackData
from bot.states import MenuStates
from concert_message_builder import get_date_time, get_lon_lat_from_yandex_map_link
from services.user_service import UserServiceAgent
from .constants import INTERNAL_ERROR_DEFAULT_TEXT, CHOOSE_ACTION_TEXT
from .user_data_manager import set_last_keyboard_id

menu_router = Router()


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == KeyboardCallbackData.CHANGE_DATA)
async def show_change_data_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await state.set_state(MenuStates.CHANGE_DATA)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT,
                                               reply_markup=keyboards.get_change_data_keyboard())


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == KeyboardCallbackData.FAQ)
async def show_faq_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await state.set_state(MenuStates.FAQ)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_faq_keyboard())


@menu_router.callback_query(MenuStates.FAQ, F.data == KeyboardCallbackData.MAIN_INFO)
async def show_main_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await state.set_state(MenuStates.FAQ_DEAD_END)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text='Информация',
                                               reply_markup=keyboards.get_back_keyboard())


@menu_router.callback_query(MenuStates.FAQ, F.data == KeyboardCallbackData.DEVELOPMENT_COMMUNICATION)
async def show_dev_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await state.set_state(MenuStates.FAQ_DEAD_END)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text='Создатель бота: @urberton',
                                               reply_markup=keyboards.get_back_keyboard())


@menu_router.callback_query(MenuStates.FAQ, F.data == KeyboardCallbackData.BACK)
async def go_to_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await state.set_state(MenuStates.MAIN_MENU)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_main_menu_keyboard())


@menu_router.callback_query(MenuStates.FAQ_DEAD_END, F.data == KeyboardCallbackData.BACK)
async def go_to_faq(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await state.set_state(MenuStates.FAQ)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_faq_keyboard())


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == KeyboardCallbackData.USER_INFO)
async def show_user_info_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await state.set_state(MenuStates.USER_INFO)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_user_info_keyboard())


@menu_router.callback_query(MenuStates.USER_INFO, F.data == KeyboardCallbackData.CITIES)
async def show_cities(callback_query: CallbackQuery, state: FSMContext, agent: UserServiceAgent) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return

    await state.set_state(MenuStates.WAITING)
    await callback_query.answer()
    try:
        cities = await agent.get_user_cities(user_id)
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
        logging.log(level=logging.WARNING, msg=str(e))
        with suppress(TelegramBadRequest):
            await callback_query.message.edit_text(text=INTERNAL_ERROR_DEFAULT_TEXT,
                                                   reply_markup=keyboards.get_back_keyboard())

    await state.set_state(MenuStates.USER_INFO_DEAD_END)


@menu_router.callback_query(MenuStates.USER_INFO, F.data == KeyboardCallbackData.LINKS)
async def show_all_links(callback_query: CallbackQuery, state: FSMContext, agent: UserServiceAgent) -> None:
    if not isinstance(callback_query.message, Message):
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return

    await state.set_state(MenuStates.WAITING)
    await callback_query.answer()

    try:
        playlists = await agent.get_user_track_lists(user_id)
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
        logging.log(level=logging.WARNING, msg=str(e))
        with suppress(TelegramBadRequest):
            await callback_query.message.edit_text(text=INTERNAL_ERROR_DEFAULT_TEXT,
                                                   reply_markup=keyboards.get_back_keyboard())

    await state.set_state(MenuStates.USER_INFO_DEAD_END)


@menu_router.callback_query(MenuStates.USER_INFO_DEAD_END, F.data == KeyboardCallbackData.BACK)
async def go_to_faq_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await state.set_state(MenuStates.USER_INFO)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_user_info_keyboard())


@menu_router.callback_query(MenuStates.USER_INFO, F.data == KeyboardCallbackData.BACK)
async def show_change_data_variants_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await state.set_state(MenuStates.MAIN_MENU)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_main_menu_keyboard())


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == KeyboardCallbackData.TOOLS)
async def show_tools(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await state.set_state(MenuStates.TOOLS)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_tools_keyboard())


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == KeyboardCallbackData.SHOW_CONCERTS)
async def show_all_concerts(callback_query: CallbackQuery, state: FSMContext, agent: UserServiceAgent) -> None:
    bot = callback_query.bot
    if bot is None or callback_query is None or callback_query.message is None:
        return
    if callback_query.from_user is None:
        return
    user_id = callback_query.from_user.id
    if user_id is None:
        return

    with suppress(TelegramBadRequest):
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await state.set_state(MenuStates.WAITING)

    try:
        await bot.send_chat_action(chat_id=callback_query.message.chat.id, action='typing')
        concerts = await agent.get_user_concerts(user_id)

        if len(concerts) == 0:
            await bot.send_message(chat_id=callback_query.message.chat.id, text='Концерты не обнаружены')
        else:
            for pos, concert in enumerate(concerts):
                if pos % 30 == 0 and pos != 0:
                    await sleep(1)
                txt = ''

                if len(concert.artists) != 1 or concert.artists[0].name != concert.title:
                    txt += f'Название: <i>{concert.title}</i>\n\n'

                if len(concert.artists) == 1:
                    txt += 'Исполнитель:'
                else:
                    txt += 'Исполнители:'

                for artist in concert.artists:
                    txt += f' {artist.name},'
                txt = txt[:-1]

                txt += (f'\n\nМесто: город <b>{concert.city}</b>,'
                        f' адрес <b>{concert.address}</b>\n')
                if concert.place is not None:
                    txt += f'в <i>{concert.place}</i>\n\n'
                else:
                    txt += '\n'

                if concert.concert_datetime is not None:
                    txt += f'Время: {get_date_time(concert.concert_datetime, True)}\n\n'
                if concert.min_price is not None:
                    txt += f'Минимальная цена билета: <b>{concert.min_price.price}</b> <b>{concert.min_price.currency}</b>\n\n'
                txt += f'Купить билет можно <a href=\"{concert.afisha_url}\">здесь</a>'

                await bot.send_message(chat_id=callback_query.message.chat.id,
                                       text=txt,
                                       parse_mode=ParseMode.HTML,
                                       disable_web_page_preview=True)

                if concert.map_url is not None:
                    try:
                        lon, lat = get_lon_lat_from_yandex_map_link(concert.map_url)
                        await bot.send_location(chat_id=callback_query.message.chat.id,
                                                longitude=lon, latitude=lat)
                    except ValueError as e:
                        logging.log(level=logging.WARNING, msg=str(e))

    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        await bot.send_message(chat_id=callback_query.message.chat.id, text=INTERNAL_ERROR_DEFAULT_TEXT)

    msg = await bot.send_message(chat_id=callback_query.message.chat.id, text=CHOOSE_ACTION_TEXT,
                                 reply_markup=keyboards.get_main_menu_keyboard())

    await set_last_keyboard_id(msg.message_id, state)
    await state.set_state(MenuStates.MAIN_MENU)



@menu_router.callback_query(MenuStates.TOOLS, F.data == KeyboardCallbackData.BACK)
async def go_to_menu_tools(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await state.set_state(MenuStates.MAIN_MENU)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text=CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_main_menu_keyboard())


@menu_router.callback_query(MenuStates.TOOLS, F.data == KeyboardCallbackData.NOTICE_MANAGEMENT)
async def show_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
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
    await state.set_state(MenuStates.TOOLS)
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(CHOOSE_ACTION_TEXT, reply_markup=keyboards.get_tools_keyboard())
