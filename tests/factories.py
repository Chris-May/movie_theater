import itertools
import string

from polyfactory.factories.pydantic_factory import ModelFactory

from movie.domain import events


class MovieAddedFactory(ModelFactory[events.MovieAdded]):
    __use_defaults__ = True


class ShowingAddedFactory(ModelFactory[events.ShowingAdded]):
    __use_defaults__ = True

    @classmethod
    def available_seats(cls):
        max_row_count = cls.__random__.randint(3, 15)
        max_seat_count = cls.__random__.randint(3, 15)
        seat_combos = itertools.product(
            string.ascii_uppercase[:max_row_count],
            map(str, range(1, max_seat_count + 1)),
        )
        return [''.join(combo) for combo in seat_combos]


class TicketReservedFactory(ModelFactory[events.TicketReserved]):
    __use_defaults__ = True
