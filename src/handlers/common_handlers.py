from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from src.states import RegistrationStates, MenuStates
from src.keyboards import get_location_keyboard_markup, get_main_menu_keyboard
from src.api_service import register_user, UserRegistrateCodes

common_router = Router()


@common_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return
    user_id = message.from_user.id
    if user_id is None:
        return
    try:
        response = register_user(message.from_user.id)
    except ValueError:
        print('Некорректный код')
        return
    await state.update_data(notices_enabled=True)
    if response.code == UserRegistrateCodes.SUCCESS:
        await message.answer(text=f'Привет, {message.from_user.username},'
                                  f' поскольку вы в нашем боте еще не зарегистрированы - самое время сделать это.'
                                  f' Введите название города, в котором желаете посещать концерты, или нажмите кнопку'
                                  f' ,чтобы отправить геолокацию.', reply_markup=get_location_keyboard_markup())
        await state.update_data(is_first_city=True)
        await state.set_state(RegistrationStates.ADD_FIRST_CITY)
        return
    if response.code == UserRegistrateCodes.USER_ALREADY_EXISTS:
        await message.answer(text=f'Привет, {message.from_user.username},'
                                  f' мы вас помним, вы регистрировались {response.registration_date} числа',
                             reply_markup=ReplyKeyboardRemove())
        await state.set_state(MenuStates.MAIN_MENU)
        await state.update_data(is_first_city=False)
        await state.update_data(cities=[])
        await state.update_data(links=[])
        await message.answer('Выберите действие', reply_markup=get_main_menu_keyboard())
        return
    if response.code == UserRegistrateCodes.NO_CONNECTION or response.code == UserRegistrateCodes.INTERNAL_SERVER_ERROR:
        await message.answer(text='Внутрение проблемы сервиса, попробуйте позже')
        return


@common_router.message(Command('stop'))
async def command_stop(message: Message, state: FSMContext) -> None:
    await message.answer(text='До скорых встреч')
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
