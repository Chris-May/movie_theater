from uuid import uuid4

from movie.domain.events import MovieAdded
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
