from pydantic import BaseModel


class TelegramUserData(BaseModel):
    last_keyboard_id: int
