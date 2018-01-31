import logging
import math
import re
import time
from datetime import datetime
from functools import wraps
from itertools import zip_longest

import pytz

tz = pytz.timezone('Europe/Moscow')
logger = logging.getLogger("vrnbus")

def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


def parse_routes(text):
    args = re.split("[ ,;]+", text)
    if not args:
        return False, tuple(), ''
    result = []
    bus_filter_start = False
    bus_filter = ''
    for i in args:
        if i in '\/|':
            bus_filter_start = True
            continue
        if bus_filter_start:
            bus_filter += i
            continue
        if result and result[-1] == 'Тр.':
            result[-1] += ' ' + i
            continue
        result.append(i)
    full_info = result[0].upper() in ['PRO', 'ПРО']
    if full_info:
        result = result[1:]

    return full_info, tuple(result), bus_filter


def distance(lat1, lon1, lat2, lon2):
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5


def distance_km(glat1, glon1, glat2, glon2):
    r = 6373.0

    lat1 = math.radians(glat1)
    lon1 = math.radians(glon1)
    lat2 = math.radians(glat2)
    lon2 = math.radians(glon2)

    diff_lon = lon2 - lon1
    diff_lat = lat2 - lat1

    a = math.sin(diff_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(diff_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    result = r * c
    return result


def get_time(s):
    return tz.localize(datetime.strptime(s, '%b %d, %Y %I:%M:%S %p'))


def grouper(n, iterable, fill_value=None):
    """grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"""
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fill_value, *args)


def retry_multi(max_retries=5):
    """ Retry a function `max_retries` times. """

    def retry(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            num_retries = 0
            ret = None
            while num_retries <= max_retries:
                try:
                    ret = func(*args, **kwargs)
                    break
                except Exception as e:
                    logger.error(e)
                    if num_retries == max_retries:
                        raise
                    num_retries += 1
                    time.sleep(5)
            return ret

        return wrapper

    return retry
