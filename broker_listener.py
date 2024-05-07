import asyncio
import logging
import sys
from asyncio import sleep
from urllib.parse import urlparse, parse_qs

from aiogram import Bot
from aiogram.enums import ParseMode

from services.broker import Broker, BrokerEvent, BrokerException
from services.broker.impl.rabbitmq_broker import RabbitMQBroker
from settings import settings
from utils import create_bot

from concert_message_builder import get_date_time, get_lon_lat_from_yandex_map_link

bot: Bot = create_bot(settings)


async def on_message(event: BrokerEvent) -> None:
    print(f'Received message for {event.user.telegram_id}')

    for pos, concert in enumerate(event.concerts):
        if pos % 30 == 0 and pos != 0:
            await sleep(1)
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

        await bot.send_message(chat_id=event.user.telegram_id,
                               text=txt,
                               parse_mode=ParseMode.HTML,
                               disable_web_page_preview=True)
        if concert.map_url is not None:
            try:
                lon, lat = get_lon_lat_from_yandex_map_link(concert.map_url)
                await bot.send_location(chat_id=event.user.telegram_id,
                                        longitude=lon, latitude=lat)
            except ValueError as e:
                logging.log(level=logging.WARNING, msg=str(e))



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
