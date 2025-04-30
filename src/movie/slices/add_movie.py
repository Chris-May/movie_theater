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
