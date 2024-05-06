import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.keyboards import get_location_keyboard_markup, get_main_menu_keyboard
from bot.states import RegistrationStates, MenuStates
from services.user_service import UserServiceAgent, UserAlreadyExistsException
from .constants import INTERNAL_ERROR_DEFAULT_TEXT, CHOOSE_ACTION_TEXT
from .user_data_manager import get_last_keyboard_id, set_last_keyboard_id

common_router = Router()


@common_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext, agent: UserServiceAgent) -> None:
    if message.from_user is None:
        return
    user_id = message.from_user.id

    await state.update_data(notices_enabled=True)  # Temp!

    try:
        await agent.create_user(user_id)
        await message.answer(text=f'Привет, {message.from_user.username},'
                                  f' поскольку вы в нашем боте еще не зарегистрированы - самое время сделать это.'
                                  f' Введите название города, в котором желаете посещать концерты, или нажмите кнопку'
                                  f' ,чтобы отправить геолокацию.', reply_markup=get_location_keyboard_markup())

        await state.update_data(is_first_city=True)
        await set_last_keyboard_id(-1, state)
        await state.set_state(RegistrationStates.ADD_FIRST_CITY)
    except UserAlreadyExistsException:
        await message.answer(text=f'Привет, {message.from_user.username},'
                                  f' мы вас помним, вы уже регистрировались',
                             reply_markup=ReplyKeyboardRemove())
        await state.set_state(MenuStates.MAIN_MENU)
        await state.update_data(is_first_city=False)
        user_data = await state.get_data()
        bot = message.bot
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=get_last_keyboard_id(user_data))
        except Exception as ex:
            logging.log(level=logging.ERROR, msg=str(ex))

        msg = await message.answer(CHOOSE_ACTION_TEXT, reply_markup=get_main_menu_keyboard())
        await set_last_keyboard_id(msg.message_id, state)

    except Exception as e:
        logging.log(level=logging.WARNING, msg=str(e))
        await message.answer(text=INTERNAL_ERROR_DEFAULT_TEXT)


@common_router.message(Command('stop'))
async def command_stop(message: Message, state: FSMContext) -> None:
    await message.answer(text='До скорых встреч')
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
