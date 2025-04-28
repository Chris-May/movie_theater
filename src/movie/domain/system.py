import sqlite3

from eventsourcing.system import System

from movie.domain.application import MovieApplication
from movie.slices.admin_available_movies.application import AdminAvailableMovies

system = System(pipes=[[MovieApplication, AdminAvailableMovies]])


class MovieSystem(System):
    def __init__(self, db_connection: sqlite3.Connection):
        self._db = db_connection
        super().__init__(pipes=[[MovieApplication, AdminAvailableMovies]])
