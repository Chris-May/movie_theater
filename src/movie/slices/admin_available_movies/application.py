import sqlite3
from uuid import UUID

from eventsourcing.application import ProcessingEvent
from eventsourcing.dispatch import singledispatchmethod
from eventsourcing.domain import DomainEventProtocol
from eventsourcing.system import Follower

from movie.domain.models import Movie

from .models import AvailableMovie


class AdminAvailableMovies(Follower):
    def set_db(self, db_connection: sqlite3.Connection) -> None:
        self._db = db_connection
        cursor = db_connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS available_movies (
            movie_id TEXT PRIMARY KEY,
            movie_name TEXT NOT NULL,
            movie_poster TEXT NOT NULL,
            movie_duration INTEGER NOT NULL
        )""")

    @singledispatchmethod
    def policy(self, domain_event: DomainEventProtocol, processing_event: ProcessingEvent) -> None:
        # This runs for other events
        pass

    @policy.register(Movie.Added)
    def on_movie_added(self, domain_event: DomainEventProtocol, _: ProcessingEvent) -> None:
        """
        When a movie is added, we need to add its data as an AvailableMovie to the database.
        """
        # Create an AvailableMovie object
        available_movie = AvailableMovie(
            movie_id=domain_event.originator_id,
            movie_name=domain_event.title,
            movie_poster=domain_event.poster_url,
            movie_duration=domain_event.duration,
        )

        # Store it in our repository
        cur = self._db.cursor()
        cur.execute('INSERT INTO available_movies VALUES (?, ?, ?, ?)', available_movie.to_row)

    def get_available_movies(self) -> list[AvailableMovie]:
        """Get all available movies from the database."""
        return self.repository.get_all()

    def get_available_movie(self, movie_id: UUID) -> AvailableMovie:
        """Get a specific available movie from the database."""
        return self.repository.get(movie_id)
