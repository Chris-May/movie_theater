from dataclasses import dataclass
from uuid import UUID


@dataclass
class AvailableMovie:
    movie_id: UUID
    movie_name: str
    movie_poster: str
    movie_duration: int

    @property
    def to_row(self):
        return (
            str(self.movie_id),
            self.movie_name,
            self.movie_poster,
            self.movie_duration,
        )
