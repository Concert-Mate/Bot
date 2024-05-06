from typing import Any

from aiogram.fsm.context import FSMContext


async def set_last_keyboard_id(msg_id: int, state: FSMContext):
    await state.update_data(last_keyboard_id=msg_id)


def get_last_keyboard_id(user_data: dict[str, Any]) -> int:
    return user_data['last_keyboard_id']
