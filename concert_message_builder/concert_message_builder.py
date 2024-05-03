from datetime import datetime
from urllib.parse import urlparse, parse_qs

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


def get_date_time(concert_datetime: datetime, is_underlined: bool) -> str:
    internal_txt = (f'{concert_datetime.day} {months.get(concert_datetime.month)} в '
                    f'{format_number(concert_datetime.time().hour)}:'
                    f'{format_number(concert_datetime.time().minute)}')
    if is_underlined:
        return f'<u>{internal_txt}</u>'
    else:
        return internal_txt


def get_lon_lat_from_yandex_map_link(map_url: str) -> (float, float):
    parsed_url = urlparse(map_url)
    parsed_query = parse_qs(parsed_url.query)
    lat_lon_parsed = parsed_query.get('ll')
    if lat_lon_parsed is None:
        raise ValueError('No coordinates in query in link of yandex map')
    lat_lon_parsed = lat_lon_parsed[0].split(',')
    if len(lat_lon_parsed) != 2:
        raise ValueError('Bad count of coordinates')
    try:
        return float(lat_lon_parsed[0]), float(lat_lon_parsed[1])
    except ValueError as e:
        raise ValueError('Bad value of coordinates') from e
