import sqlite3
from uuid import UUID

from eventsourcing.application import ProcessingEvent
from eventsourcing.dispatch import singledispatchmethod
from eventsourcing.domain import DomainEventProtocol
from eventsourcing.persistence import Tracking
from eventsourcing.projection import Projection
from eventsourcing.sqlite import SQLiteDatastore, SQLiteTrackingRecorder
from eventsourcing.system import Follower

from movie.domain.models import Movie

from .models import AvailableMovie


class AvailableMovieView(SQLiteTrackingRecorder):
    _movies_table = 'available_movies'
    def __init__(self, datastore: SQLiteDatastore, **kwargs ):
        super().__init__(datastore=datastore, **kwargs)
        self.create_table_statements.append(
            'CREATE TABLE IF NOT EXISTS {0} ('
            'movie_id TEXT PRIMARY KEY,'
            'movie_name TEXT NOT NULL,'
            'movie_poster TEXT NOT NULL,'
            'movie_duration INTEGER NOT NULL)'
        ).format(self._movies_table)

    def add(self, movie: AvailableMovie) -> None:
        with self.datastore.transaction(commit=True) as curs:
            curs.execute(
                f"INSERT OR REPLACE INTO {self._movies_table} (movie_id, movie_name, movie_poster, movie_duration) VALUES (?, ?, ?, ?)",
                (str(movie.movie_id), movie.movie_name, movie.movie_poster, movie.movie_duration)
            )

    def get_all(self) -> list[AvailableMovie]:
        with self.datastore.transaction(commit=False) as curs:
            curs.execute(f"SELECT movie_id, movie_name, movie_poster, movie_duration FROM {self._movies_table}")
            rows = curs.fetchall()
            return [
                AvailableMovie(
                    movie_id=row["movie_id"],
                    movie_name=row["movie_name"],
                    movie_poster=row["movie_poster"],
                    movie_duration=row["movie_duration"],
                )
                for row in rows
            ]


class AvailableMovieProjection(Projection[AvailableMovieView]):

    def process_event(self, domain_event: DomainEventProtocol, tracking: Tracking) -> None:
        if isinstance(domain_event, Movie.Added):
            # Create an AvailableMovie object
            available_movie = AvailableMovie(
                movie_id=domain_event.originator_id,
                movie_name=domain_event.title,
                movie_poster=domain_event.poster_url,
                movie_duration=domain_event.duration,
            )

            # Store it in our repository
            self.view.add(available_movie)

