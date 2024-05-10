from aiogram import F
from aiogram.enums import ContentType
from aiogram.filters import Command

SKIP_COMMAND_FILTER = Command('skip')

TEXT_WITHOUT_COMMANDS_FILTER = F.content_type == ContentType.TEXT and F.text[0] != '/'

INTERNAL_ERROR_DEFAULT_TEXT = 'Внутренние проблемы сервиса, попробуйте позже.'

CHOOSE_ACTION_TEXT = 'Выберите действие'

MAXIMUM_CITY_LEN = 40

INSTRUCTION_PHOTO_ID = 'AgACAgIAAxkBAAIGWmY-VV6cOd8gpLlshlZrTizjTvBIAAKJ3jEb7FD5SRxxe_eRk7HQAQADAgADeAADNQQ'

MAXIMUM_LINK_LEN = 100

DEV_COMM_TEXT = ('Репозиторий бота в <a href=\"https://github.com/Concert-Mate/Bot\">github</a>\n'
                 'Создатель бота @urberton')

FAQ_TEXT = ('<b>Могу ли я прислать ссылки из ВК? Из Spotify?</b>\n'
            'Нет, на данный момент мы работаем только с \"Яндекс-Музыкой\"\n\n'
            '<b>Могу ли узнать о концертах в другой стране?</b>\n'
            'Нет, на данный момент мы работаем только в России\n\n'
            '<b>Что делать при возникновении ошибки?</b>\n'
            'Обратиться к разработчикам бота: нажмите Назад->Связь с разработчиком\n\n'
            '<b>Как добавить/удалить город/трек-лист?</b>\n'
            'Перейдите в главное меню и нажмите на кнопку \"Изменение данных\"\n\n'
            '<b>Как получить все концерты?</b>\n'
            'Перейдите в главное меню и нажмите кнопку \"Показать доступные концерты\"\n\n'
            '<b>Где можно посмотреть свои города/трек-листы?</b>\n'
            'Перейдите в главное меню и нажмите на кнопку \"Информация о пользователе\"')

ABOUT_TEXT = ('Данный бот умеет присылать уведомления о концертах любимых исполнителей.\n'
              'Любимых исполнителей мы выбираем по плейлистам и альбомам,'
              ' на текущий момент мы поддерживаем только Яндекс Музыку и Россию.\n')
