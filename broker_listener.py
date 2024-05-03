import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import LinkPreviewOptions

from services.broker import Broker, BrokerEvent, BrokerException
from services.broker.impl.rabbitmq_broker import RabbitMQBroker
from settings import settings
from utils import create_bot
from urllib.parse import urlparse, parse_qs

bot: Bot = create_bot(settings)

months = {
    1: 'января',
    2: 'февраля',
    3: 'марта',
    4: 'апреля',
    5: 'мая',
    6: 'июня',
    7: 'июля',
    8: 'августа',
    9: 'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря'
}


def format_number(num: int) -> str:
    if num < 10:
        return f'0{num}'
    return f'{num}'


async def on_message(event: BrokerEvent) -> None:
    print(f'Received message for {event.user.telegram_id}')

    for concert in event.concerts:
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
        txt += f'\n\nМесто: город <b>{concert.city}</b>, адрес <b>{concert.address}</b>\nв <i>{concert.place}</i>\n\n'
        txt += (f'Время: <u>{concert.concert_datetime.day} {months.get(concert.concert_datetime.month)} в '
                f'{format_number(concert.concert_datetime.time().hour)}:'
                f'{format_number(concert.concert_datetime.time().minute)}</u>\n\n')
        txt += f'Минимальная цена билета: <b>{concert.min_price.price}</b> <b>{concert.min_price.currency}</b>'

        await bot.send_message(chat_id=event.user.telegram_id,
                               text=txt,
                               parse_mode=ParseMode.HTML,
                               disable_web_page_preview=True)

        parsed_url = urlparse(concert.map_url)
        parsed_query = parse_qs(parsed_url.query)
        lat_lon_parsed = parsed_query.get('l')
        if lat_lon_parsed is None:
            return
        lat_lon_parsed = lat_lon_parsed[0].split(',')
        try:
            await bot.send_location(chat_id=event.user.telegram_id,
                                    longitude=float(lat_lon_parsed[0]), latitude=float(lat_lon_parsed[1]))
        except ValueError:
            return



async def on_error(exception: Exception) -> None:
    logging.error('An error with broker occurred: %s' % exception)


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

        logging.info('Starting listening broker ...')
        await rabbitmq_broker.start_listening(
            on_message_callback=on_message,
            on_error_callback=on_error,
        )
    except BrokerException as e:
        logging.warning(e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
