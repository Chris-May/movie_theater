import asyncio
import calendar
from datetime import date, datetime, time
from pathlib import Path

import httpx

movies = (
    (
        'Aladdin',
        128,
        'https://webneel.com/daily/sites/default/files/images/daily/09-2019/2-movie-poster-design-aladdin-disney-glossy-composite.jpg',
    ),
    ('Movie', 102, 'https://img.freepik.com/premium-psd/movie-poster_841014-31866.jpg?w=2000'),
    (
        'Movie Title',
        114,
        'https://s.studiobinder.com/wp-content/uploads/2017/12/Movie-Poster-Template-Dark-with-Image.jpg?x81279',
    ),
)
times = (time(19, 15), time(19, 20), time(19, 30), time(20, 50), time(21, 00), time(21, 10))


project_root = next(p for p in Path(__file__).parents if (p / '.git').exists())


async def add_movie(name, duration, poster, client):
    r = await client.post(
        "/movie",
        json={
            "name": name,
            "duration": duration,
            "poster_url": poster,
        },
    )
    result = r.json()
    return result['movie_id']


async def add_showing(movie_id, start_time: datetime, client, semaphore):
    available_seats = [
        "A1",
        "A2",
        "A3",
        "A4",
        "A5",
        "A6",
        "B1",
        "B2",
        "B3",
        "B4",
        "B5",
        "B6",
        "B7",
        "B8",
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6",
        "C7",
        "C8",
        "C9",
        "C10",
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
        "D6",
        "D7",
        "D8",
        "D9",
        "D10",
        "D11",
        "D12",
        "E1",
        "E2",
        "E3",
        "E4",
        "E5",
        "E6",
        "E7",
        "E8",
        "E9",
        "E10",
        "E11",
        "E12",
        "F1",
        "F2",
        "F3",
        "F4",
        "F5",
        "F6",
        "F7",
        "F8",
        "F9",
        "F10",
        "F11",
        "F12",
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6",
        "G7",
        "G8",
        "G9",
        "G10",
        "G11",
        "G12",
        "H1",
        "H2",
        "H3",
        "H4",
        "H5",
        "H6",
        "H7",
        "H8",
        "H9",
        "H10",
        "H11",
        "H12",
        "I1",
        "I2",
        "I3",
        "I4",
        "I5",
        "I6",
        "I7",
        "I8",
        "I9",
        "I10",
        "I11",
        "I12",
        "J1",
        "J2",
        "J3",
        "J4",
        "J5",
        "J6",
        "J7",
        "J8",
        "J9",
        "J10",
        "J11",
        "J12",
        "K1",
        "K2",
        "K3",
        "K4",
        "K5",
        "K6",
        "K7",
        "K8",
        "K9",
        "K10",
        "K11",
        "K12",
    ]
    async with semaphore:
        await client.post(
            "/showing",
            json={
                "movie_id": movie_id,
                "start_time": start_time.isoformat(),
                "available_seats": available_seats,
            },
        )


async def main():
    semaphore = asyncio.Semaphore(10)
    client = httpx.AsyncClient(base_url="http://localhost:5001")
    movie_ids = [await add_movie(movie[0], movie[1], movie[2], client) for movie in movies]
    this_year = datetime.today().year
    this_month = datetime.today().month
    _, days_this_month = calendar.monthrange(datetime.today().year, datetime.today().month)
    start_times = []
    for day in range(1, days_this_month + 1):
        start_times.extend([datetime.combine(date(this_year, this_month, day), t) for t in times])
    movie_times = list(zip(movie_ids * (len(start_times) // len(movie_ids)), start_times, strict=True))
    await asyncio.gather(
        *[add_showing(movie_id, start_time, client, semaphore) for movie_id, start_time in movie_times]
    )


def go():
    asyncio.run(main())
