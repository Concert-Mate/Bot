import asyncio
import json
import logging
import logging.config
from asyncio import sleep

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from redis import BusyLoadingError
from redis.asyncio import Redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff

from bot.handlers.constants import CHOOSE_ACTION_TEXT
from bot.keyboards.menu_keyboards import get_main_menu_keyboard
from bot.states.menu_states import MenuStates
from concert_message_builder import get_date_time, get_lon_lat_from_yandex_map_link
from model import TelegramUserData
from services.broker import Broker, BrokerEvent
from services.broker.impl.rabbitmq_broker import RabbitMQBroker
from settings import settings
from utils import create_bot

bot: Bot = create_bot(settings)

REQUESTS_COUNT = 100000
RETRY = 3
TIMEOUT = 2


class Singleton:
    _instance = None

    @staticmethod
    def get_connection():
        if not Singleton._instance:
            Singleton._instance = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                socket_timeout=TIMEOUT,
                retry=Retry(ExponentialBackoff(), RETRY),
                retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError]
            )
        return Singleton._instance


async def on_message(event: BrokerEvent) -> None:
    broker_logger.info(f'got info for {event.user.telegram_id}')
    connection = Singleton.get_connection()
    removed_kb = False
    data = await connection.get(name=f'fsm:{event.user.telegram_id}:{event.user.telegram_id}:data')
    if data is not None:
        broker_logger.debug(f'got data from redis for {event.user.telegram_id}')
        try:
            keyboard_id = TelegramUserData.model_validate_json(data).last_keyboard_id
            await bot.delete_message(chat_id=event.user.telegram_id, message_id=keyboard_id)
            removed_kb = True
        except Exception as ex:
            broker_logger.warning(f'on {event.user.telegram_id} when tried to delete keyboard exception: {str(ex)}')

    for pos, concert in enumerate(event.concerts):
        txt = f'Скоро состоится <a href=\"{concert.afisha_url}\">концерт</a>!!!\n\n'

        if len(concert.artists) != 1 or concert.artists[0].name != concert.title:
            txt += f'Название: <i>{concert.title}</i>\n\n'

        if len(concert.artists) == 1:
            txt += 'Исполнитель:'
        else:
            txt += 'Исполнители:'

        for artist in concert.artists:
            txt += f' {artist.name},'
        txt = txt[:-1]

        txt += f'\n\nМесто: город <b>{concert.city}</b>, адрес <b>{concert.address}</b>\n'
        if concert.place is not None:
            txt += f'в <i>{concert.place}</i>\n\n'
        else:
            txt += '\n'

        if concert.concert_datetime is not None:
            txt += f'Время: {get_date_time(concert.concert_datetime, True)}\n\n'
        if concert.min_price is not None:
            txt += f'Минимальная цена билета: <b>{concert.min_price.price}</b> <b>{concert.min_price.currency}</b>'
        try:
            await bot.send_message(chat_id=event.user.telegram_id,
                                   text=txt,
                                   parse_mode=ParseMode.HTML,
                                   disable_web_page_preview=True)
        except TelegramForbiddenError as e:
            broker_logger.warning(f'on {event.user.telegram_id} when tried to send concert exception: {str(e)}')
            return


        if concert.map_url is not None:
            try:
                lon, lat = get_lon_lat_from_yandex_map_link(concert.map_url)
                await bot.send_location(chat_id=event.user.telegram_id,
                                        longitude=lon, latitude=lat)
            except ValueError as e:
                broker_logger.warning(f'on {event.user.telegram_id} when tried to get location exception: {str(e)}')
            except TelegramForbiddenError as e:
                broker_logger.warning(f'on {event.user.telegram_id} when tried to send location exception: {str(e)}')
                return

        await sleep(1)

    if removed_kb:
        await connection.set(name=f'fsm:{event.user.telegram_id}:{event.user.telegram_id}:state',
                             value=str(MenuStates.MAIN_MENU.state))
        try:
            msg = await bot.send_message(chat_id=event.user.telegram_id, text=CHOOSE_ACTION_TEXT,
                                         reply_markup=get_main_menu_keyboard())
        except TelegramBadRequest as e:
            broker_logger.warning(f'on {event.user.telegram_id} when tried to send keyboard exception: {str(e)}')
            return
        json_data = json.loads(data)
        json_data['last_keyboard_id'] = msg.message_id
        await connection.set(f'fsm:{event.user.telegram_id}:{event.user.telegram_id}:data',
                             value=json.dumps(json_data))


async def on_error(exception: Exception) -> None:
    root_logger.error('An error with broker occurred: %s' % exception)


async def main() -> None:
    try:
        rabbitmq_broker: Broker = RabbitMQBroker()
        await rabbitmq_broker.connect(
            queue_name=settings.rabbitmq_queue,
            user_name=settings.rabbitmq_user,
            password=settings.rabbitmq_password,
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
        )

        await Singleton.get_connection().ping()
        root_logger.info('Connection with redis on broker is OK')

        root_logger.info('Starting listening broker ...')
        await rabbitmq_broker.start_listening(
            on_message_callback=on_message,
            on_error_callback=on_error,
        )
    except Exception as e:
        logging.warning(e)


if __name__ == "__main__":
    logging.config.fileConfig(fname='broker_logging.ini')
    root_logger = logging.getLogger('root')
    broker_logger = logging.getLogger('broker')
    asyncio.run(main())
