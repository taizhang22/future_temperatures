"""Main script to be run"""

import pygame
import graph_objects as go
import py_shapes as ps
import calculations as calc

import random
import datetime

from typing import List, Tuple, Any

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 800

background_color = "white"

G_X = 50
G_Y = 100
G_COORDINATE = (G_X, G_Y)

G_WIDTH = 1000
G_HEIGHT = 500
G_SIZE = (G_WIDTH, G_HEIGHT)

G_LEFT = 30
G_BOTTOM = 30
G_RIGHT = 20
G_TOP = 50
G_MARGINS = (G_LEFT, G_BOTTOM, G_RIGHT, G_TOP)

G_TITLE = "Basic Graph Test"

G_FAKE_DATA = [
    [(0.0, 10.0), (10.0, 30.0), (40.0, 20.0)],
]
G_BOUNDS = ((0, 40), (10, 30))


objects: List[ps.Drawable] = []


def random_data() -> List[Tuple[float, float]]:
    """Return a random set of data
    Only creates one set of data
    """
    n = random.randint(3, 10)
    cap = 1000.0
    data_set = [(random.random() * cap, random.random() * cap) for _ in range(n)]
    data_set.sort(key=lambda x: x[0])

    return data_set


def random_time_data() -> List[Tuple[datetime.datetime, float]]:
    """Return random set of data with dates as the manipulated variable
    """

    cur_date = datetime.date.today()
    dates = []
    year = cur_date.year
    month = cur_date.month
    for i in range(120):
        month = month % 12 + 1
        if month == 1:
            year += 1
        dates.append(datetime.date(year=year, month=month, day=1))

    n = random.randint(3, 10)
    cap = 1000
    data_set = [(random.choice(dates), random.random() * cap) for _ in range(n)]
    data_set.sort(key=lambda x: x[0])

    return data_set


def designer() -> None:
    """Creates all the visual objects"""

    # graph = go.Graph(g_title, g_coordinate, g_size, g_margins, ((0, 1000), (0, 1000)))
    # graph = go.Graph(g_title, g_coordinate, g_size, g_margins,
    #                  ((datetime.date.today(), datetime.date(year=2030, month=12, day=31)),
    #                   (0, 1000)))

    graph = go.Graph(G_TITLE, G_COORDINATE, G_SIZE, G_MARGINS)
    temp_data = calc.read_temperature_data("temperature_data.csv")
    carbon_data = calc.read_carbon_data('co2_data.csv')
    graph.add_data_set(temp_data, marker_color="transparent")
    graph.add_data_set(carbon_data, marker_color="transparent")

    objects.append(graph)


def draw(screen: pygame.Surface) -> None:
    """Draws all the objects"""

    screen.fill(background_color)

    for drawable in objects:
        drawable.draw(screen)

    pygame.display.flip()


def main() -> None:
    """Entry point for the program"""

    screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    running = True

    designer()
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            ps.CustomMouseEvent.play_events(event)

        draw(screen)

    pygame.display.quit()


if __name__ == "__main__":
    main()
