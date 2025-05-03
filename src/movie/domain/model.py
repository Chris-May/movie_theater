from uuid import UUID, uuid4

from movie.domain.events import MovieAdded, ShowingAdded
from movie.infrastructure.entity import Entity


class Movie(Entity):
    title: str
    duration: int
    poster_url: str

    def __repr__(self):
        return (
            f'<Movie title={self.title}, duration={self.duration}, '
            f'poster_url={self.poster_url}, '
            f'id={self.id}, version={self.version}>'
        )

    @property
    def movie_id(self):
        return self.id

    @classmethod
    def create(cls, name, duration, poster_url):
        event = MovieAdded(
            movie_name=name, duration=duration, movie_poster=poster_url, entity_id=uuid4(), entity_version=1
        )
        movie = cls(event)
        movie.publish(event)
        return movie

    def _on_creation(self, event: MovieAdded):
        self.title = event.movie_name
        self.duration = event.duration
        self.poster_url = event.movie_poster
        self.id = event.entity_id

    def register_events(self):
        self.apply.register(MovieAdded, self._on_creation)


class Showing(Entity):
    movie_id: UUID
    start_time: str
    available_seats: list[str]

    def __repr__(self):
        return (
            f'<Showing movie_id={self.movie_id}, start_time={self.start_time}, '
            f'available_seats={self.available_seats}, '
            f'id={self.id}, version={self.version}>'
        )

    @property
    def showing_id(self):
        return self.id

    @classmethod
    def create(cls, movie_id, start_time, available_seats):
        event = ShowingAdded(
            movie_id=movie_id,
            start_time=start_time,
            available_seats=available_seats,
            entity_id=uuid4(),
            entity_version=1,
        )
        showing = cls(event)
        showing.publish(event)
        return showing

    def _on_creation(self, event: ShowingAdded):
        self.movie_id = event.movie_id
        self.start_time = event.start_time
        self.available_seats = event.available_seats
        self.id = event.entity_id

    def register_events(self):
        self.apply.register(ShowingAdded, self._on_creation)
