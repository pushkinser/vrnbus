from logging import Logger

from cds import CdsRequest
from data_types import UserLoc
from helpers import parse_routes, natural_sort_key


class BaseDataProcessor:
    def __init__(self, cds: CdsRequest, logger: Logger):
        self.cds = cds
        self.logger = logger


class WebDataProcessor(BaseDataProcessor):
    def __init__(self, cds: CdsRequest, logger: Logger):
        super().__init__(cds, logger)

    def get_bus_info(self, query, lat, lon):
        user_loc = None
        if lat and lon:
            user_loc = UserLoc(float(lat), float(lon))
        result = self.cds.bus_request(parse_routes(query), user_loc=user_loc, short_format=True)
        return {'q': query, 'text': result[0],
                'buses': [(x[0]._asdict(), x[1]._asdict() if x[1] else {}) for x in result[1]]}

    def get_arrival(self, query, lat, lon):
        matches = self.cds.matches_bus_stops(lat, lon)
        self.logger.info(f'{lat};{lon} {";".join([str(i) for i in matches])}')
        result = self.cds.next_bus_for_matches(tuple(matches), parse_routes(query))
        response = {'lat': lat, 'lon': lon, 'text': result[0], 'header': result[1], 'bus_stops': result[2]}
        return response

    def get_arrival_by_name(self, query, station_query):
        result_tuple = self.cds.next_bus(station_query, parse_routes(query))
        response = {'text': result_tuple[0], 'header': result_tuple[1], 'bus_stops': result_tuple[2]}
        return response

    def get_bus_list(self):
        codd_buses = list(self.cds.codd_routes.keys())
        codd_buses.sort(key=natural_sort_key)
        response = {'result': codd_buses}
        return response


class TelegramDataProcessor(BaseDataProcessor):
    def __init__(self, cds: CdsRequest, logger: Logger):
        super().__init__(cds, logger)
