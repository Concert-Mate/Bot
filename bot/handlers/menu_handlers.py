from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import keyboards
from bot.keyboards import KeyboardCallbackData
from bot.states import MenuStates

menu_router = Router()


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == KeyboardCallbackData.CHANGE_DATA)
async def show_change_data_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text('Выберите действие', reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == KeyboardCallbackData.FAQ)
async def show_faq_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text('Выберите действие', reply_markup=keyboards.get_faq_keyboard())
    await state.set_state(MenuStates.FAQ)


@menu_router.callback_query(MenuStates.FAQ, F.data == KeyboardCallbackData.MAIN_INFO)
async def show_main_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text('Информация',
                                           reply_markup=keyboards.get_back_keyboard())
    await state.set_state(MenuStates.FAQ_DEAD_END)


@menu_router.callback_query(MenuStates.FAQ, F.data == KeyboardCallbackData.DEVELOPMENT_COMMUNICATION)
async def show_dev_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text('Создатель бота: @urberton',
                                           reply_markup=keyboards.get_back_keyboard())
    await state.set_state(MenuStates.FAQ_DEAD_END)


@menu_router.callback_query(MenuStates.FAQ, F.data == KeyboardCallbackData.BACK)
async def go_to_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text('Выберите действие', reply_markup=keyboards.get_main_menu_keyboard())
    await state.set_state(MenuStates.MAIN_MENU)


@menu_router.callback_query(MenuStates.FAQ_DEAD_END, F.data == KeyboardCallbackData.BACK)
async def go_to_faq(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text('Выберите действие', reply_markup=keyboards.get_faq_keyboard())
    await state.set_state(MenuStates.FAQ)


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == KeyboardCallbackData.USER_INFO)
async def show_user_info_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text('Выберите действие', reply_markup=keyboards.get_user_info_keyboard())
    await state.set_state(MenuStates.USER_INFO)


@menu_router.callback_query(MenuStates.USER_INFO, F.data == KeyboardCallbackData.CITIES)
async def show_cities(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    txt = 'Ваши города:'
    user_data = await state.get_data()
    for city in user_data['cities']:
        txt += f'\n{city}'
    await callback_query.message.edit_text(text=txt, reply_markup=keyboards.get_back_keyboard())
    await state.set_state(MenuStates.USER_INFO_DEAD_END)


@menu_router.callback_query(MenuStates.USER_INFO, F.data == KeyboardCallbackData.LINKS)
async def show_all_links(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    txt = 'Ваши плейлисты:'
    user_data = await state.get_data()
    for link in user_data['links']:
        txt += f'\n{link}'
    await callback_query.message.edit_text(text=txt, reply_markup=keyboards.get_back_keyboard(),
                                           disable_web_page_preview=True)
    await state.set_state(MenuStates.USER_INFO_DEAD_END)


@menu_router.callback_query(MenuStates.USER_INFO_DEAD_END, F.data == KeyboardCallbackData.BACK)
async def go_to_faq_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text('Выберите действие', reply_markup=keyboards.get_user_info_keyboard())
    await state.set_state(MenuStates.USER_INFO)


@menu_router.callback_query(MenuStates.USER_INFO, F.data == KeyboardCallbackData.BACK)
async def show_change_data_variants_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text(text='Выберите действие', reply_markup=keyboards.get_main_menu_keyboard())
    await state.set_state(MenuStates.MAIN_MENU)


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == KeyboardCallbackData.TOOLS)
async def show_tools(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text('Выберите действие', reply_markup=keyboards.get_tools_keyboard())
    await state.set_state(MenuStates.TOOLS)


@menu_router.callback_query(MenuStates.TOOLS, F.data == KeyboardCallbackData.SHOW_CONCERTS)
async def show_all_concerts(callback_query: CallbackQuery, state: FSMContext) -> None:
    bot = callback_query.bot
    if bot is None or callback_query is None or callback_query.message is None:
        return
    # TODO: Обращение к бэку
    txt = 'Информация о концерте'
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text=txt, reply_markup=None)
    await bot.send_message(chat_id=callback_query.message.chat.id, text='Выберите действие',
                           reply_markup=keyboards.get_tools_keyboard())
    await state.set_state(MenuStates.TOOLS)


@menu_router.callback_query(MenuStates.TOOLS, F.data == KeyboardCallbackData.BACK)
async def go_to_menu_tools(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text('Выберите действие', reply_markup=keyboards.get_main_menu_keyboard())
    await state.set_state(MenuStates.MAIN_MENU)


@menu_router.callback_query(MenuStates.TOOLS, F.data == KeyboardCallbackData.NOTICE_MANAGEMENT)
async def show_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    user_data = await state.get_data()
    await callback_query.message.edit_text('Выберите действие',
                                           reply_markup=keyboards.
                                           get_notify_management_keyboard(user_data['notices_enabled']))
    await state.set_state(MenuStates.MANAGING_NOTIFICATIONS)


@menu_router.callback_query(MenuStates.MANAGING_NOTIFICATIONS, F.data == KeyboardCallbackData.ENABLE)
async def swap_notice_enable(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    user_data = await state.get_data()
    user_data['notices_enabled'] = True
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text='Выберите действие',
                                               reply_markup=keyboards.
                                               get_notify_management_keyboard(True))


@menu_router.callback_query(MenuStates.MANAGING_NOTIFICATIONS, F.data == KeyboardCallbackData.DISABLE)
async def swap_notice_enable_disable(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    user_data = await state.get_data()
    user_data['notices_enabled'] = False
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(text='Выберите действие',
                                               reply_markup=keyboards.
                                               get_notify_management_keyboard(False))


@menu_router.callback_query(MenuStates.MANAGING_NOTIFICATIONS, F.data == KeyboardCallbackData.BACK)
async def go_to_tools(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text('Выберите действие', reply_markup=keyboards.get_tools_keyboard())
    await state.set_state(MenuStates.TOOLS)
