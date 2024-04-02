from telegram.ext import ConversationHandler
FIRST_CITY_REGISTRATION, FIRST_PLAYLIST_REGISTRATION = map(chr, range(2))
END = ConversationHandler.END

__all__ = ['FIRST_PLAYLIST_REGISTRATION', 'FIRST_CITY_REGISTRATION', 'END']
