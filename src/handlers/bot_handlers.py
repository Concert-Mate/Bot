from telegram import ForceReply, Update
from telegram.ext import ContextTypes
from .states import *

__all__ = ['start', 'end', 'first_city_registration', 'first_playlist_registration']


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_text(f'Hello {user.username} , welcome to bot. Please enter your city')
    return FIRST_CITY_REGISTRATION


async def first_city_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    city_name = update.message.text
    print(city_name)

    if (True):
        await update.message.reply_text(f"Successful added city: {city_name}")
        return FIRST_PLAYLIST_REGISTRATION
    else:
        await update.message.reply_text(f"Error adding city: {city_name}. Try again")
        return FIRST_CITY_REGISTRATION


async def first_playlist_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    playlist_path = update.message.text
    print(playlist_path)

    if (True):
        await update.message.reply_text(f"Successful added playlist: {playlist_path}")
        return END
    else:
        await update.message.reply_text(f"Error adding playlist: {playlist_path}. Try again")
        return FIRST_PLAYLIST_REGISTRATION

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Thanks) Have fun later")
    return END
