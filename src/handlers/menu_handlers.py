from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src import keyboards
from src.states import MenuStates

menu_router = Router()


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == 'change_data')
async def show_change_data_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.edit_text('Выберите действие', reply_markup=keyboards.get_change_data_keyboard())
    await state.set_state(MenuStates.CHANGE_DATA)


@menu_router.callback_query(MenuStates.MAIN_MENU, F.data == 'FAQ')
async def show_faq_variants(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.edit_text('Выберите действие', reply_markup=keyboards.get_faq_keyboard())
    await state.set_state(MenuStates.FAQ)


@menu_router.callback_query(MenuStates.FAQ, F.data == 'main_info')
async def show_main_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.edit_text('ЗДЕСЬ МОЖЕТ БЫТЬ ВАША РЕКЛАМА'
                                           , reply_markup=keyboards.get_back_keyboard())
    await state.set_state(MenuStates.FAQ_DEAD_END)


@menu_router.callback_query(MenuStates.FAQ, F.data == 'dev_comm')
async def show_main_info(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.edit_text('Создатель бота: @urberton',
                                           reply_markup=keyboards.get_back_keyboard())
    await state.set_state(MenuStates.FAQ_DEAD_END)


@menu_router.callback_query(MenuStates.FAQ, F.data == 'back')
async def go_to_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.edit_text('Выберите действие', reply_markup=keyboards.get_main_menu_keyboard())
    await state.set_state(MenuStates.MAIN_MENU)


@menu_router.callback_query(MenuStates.FAQ_DEAD_END, F.data == 'back')
async def go_to_faq(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.edit_text('Выберите действие', reply_markup=keyboards.get_faq_keyboard())
    await state.set_state(MenuStates.FAQ)
    bot = callback_query.message.bot
    bot.send_animation()
