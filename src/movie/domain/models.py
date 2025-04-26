from eventsourcing.domain import Aggregate, event


class Movie(Aggregate):
    @event('Added')
    def __init__(self, title: str, duration: int, poster_url):
        self.title = title
        self.duration = duration
        self.poster_url = poster_url
