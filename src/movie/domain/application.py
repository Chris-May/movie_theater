from uuid import UUID

from eventsourcing.application import Application

from movie.domain.models import Movie


class MovieApplication(Application):
    def add_movie(self, title: str, duration: int, poster_url) -> UUID:
        movie = Movie(title=title, duration=duration, poster_url=poster_url)
        self.save(movie)
        return movie.id
