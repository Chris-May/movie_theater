import sqlite3

from eventsourcing.system import System

from movie.domain.application import MovieApplication
from movie.slices.admin_available_movies.application import AvailableMovieProjection

system = System(pipes=[[MovieApplication]])


class MovieSystem(System):
    def __init__(self):
        super().__init__(pipes=[[MovieApplication]])
