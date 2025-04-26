from eventsourcing.system import System

from movie.domain.application import MovieApplication

system = System(pipes=[[MovieApplication]])
