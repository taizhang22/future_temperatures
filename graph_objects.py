"""Module containing custom written Pygame objects"""

from __future__ import annotations
from py_shapes import Panel, Size, Point, Data, Rectangle, Line, TextBox, CustomMouseEvent
from extra_objects import Observer, Observable
import math
import pygame
from typing import Union, List, Tuple, Dict, Any, Optional, Final


class Graph(Panel):
    """Drawable class that displays sets of data

    A set of data is defined as a list of Tuple[float, float]

    Instance Attributes:
        - title: the title of the graph displayed at the top
        - data: list containing the definition of a full set of data for each figure.
        - position: a tuple (x, y) storing the top left position of the graph
        - size: a tuple (width, height) storing the width and height of the graph

    """

    _margins: Tuple[float, float, float, float]

    title: str
    title_color: Tuple[int, int, int] = (255, 0, 0)

    _data: List[Data]

    left: float
    bottom: float
    right: float
    top: float

    graph_panel: Panel
    visible_domain: Tuple[float, float]
    visible_range: Tuple[float, float]

    _auto: bool
    _bounds: Tuple[Tuple[float, float], Tuple[float, float]]

    def __init__(self, title: str = '', position: Union[Point, Tuple[float, float]] = Point(0, 0),
                 size: Union[Size, Tuple[float, float]] = Size(0, 0),
                 margins: Tuple[float, float, float, float] = (0, 0, 0, 0),
                 bounds: Tuple[Tuple[Data.SUPPORTED_X, Data.SUPPORTED_X],
                               Tuple[Data.SUPPORTED_Y, Data.SUPPORTED_Y]] = None):
        super().__init__(position, size)

        self.title = title
        self._data = []

        self.title_color = (255, 0, 0)

        self._margins = self.margins = margins

        self._auto = bounds is None
        self.visible_domain = (0, 1) if self._auto else bounds[0]
        self.visible_range = (0, 1) if self._auto else bounds[1]
        self._bounds = bounds

        # Overriding constants from Panel
        self.background_color = "yellow"
        self.line_color = "black"
        self.text_color = "black"

        self.designer()

    def draw(self, screen: pygame.Surface, position: Point = Point(0, 0)) -> None:
        """Draws a graph object
        """
        super().draw(screen, position)

        self.draw_graph(screen, position.increment(self.position).increment(self.graph_panel.position))

    def designer(self) -> None:
        """Section for designing the visual aesthetic of the Graph
        """

        left = self.left
        right = self.width - self.right
        top = self.top
        bottom = self.height - self.bottom

        p_position = Point(left, top)
        p_size = Size(right - left, bottom - top)
        visual_panel = Panel(p_position, p_size)
        self.add_component(visual_panel, "visual panel")
        self.graph_panel = visual_panel

        left_line = Line(self.line_color, Point(left, top), Point(left, bottom))
        bottom_line = Line(self.line_color, Point(left, bottom), Point(right, bottom))

        self.add_component(left_line, "left line")
        self.add_component(bottom_line, "bottom line")

        title_half_point = Point(self.width / 2, self.top / 2)
        title_text = TextBox(self.title, self.title_color, title_half_point,
                             horizontal_alignment=1, vertical_alignment=1,
                             background_color="green")

        self.add_component(title_text, "title text")

    def draw_graph(self, screen: pygame.Surface, position: Union[Point, Tuple[float, float]]):
        """Draws the graph"""

        if self._auto:
            self.resize_bounds()

        x_1, x_2 = self.visible_domain
        y_1, y_2 = self.visible_range

        upper_y_label = TextBox(f'y={str(int(y_2))}', (0, 0, 0), (0, 0), background_color="transparent", font_size=15,
                                horizontal_alignment=2)
        upper_y_label.draw(screen, position)

        lower_y_label = TextBox(f'y={str(int(y_1))}', (0, 0, 0), (0, self.graph_panel.height),
                                background_color="transparent", font_size=15,
                                horizontal_alignment=2, vertical_alignment=2)
        lower_y_label.draw(screen, position)

        upper_x_label = TextBox(f'x={str(x_2)}', (0, 0, 0), (self.graph_panel.width, self.graph_panel.height),
                                background_color="transparent", font_size=15)
        upper_x_label.draw(screen, position)

        lower_x_label = TextBox(f'x={str(x_1)}', (0, 0, 0), (0, self.graph_panel.height),
                                background_color="transparent", font_size=15)
        lower_x_label.draw(screen, position)

        g_width = x_2 - x_1
        g_height = y_2 - y_1

        def is_over(x: float, y: float) -> bool:
            """Check if data point is in the visible area"""
            return x_1 <= x <= x_2 and y_1 <= y <= y_2

        graph_points = []

        for data_set in self.data:

            data_points = []

            for data_point in data_set:

                x_pos = self.graph_panel.width * (data_point[0] - x_1) / g_width
                y_pos = self.graph_panel.height * (1 - (data_point[1] - y_1) / g_height)

                data_points.append(Point(x_pos, y_pos))

                if is_over(*data_point) and data_set.marker_color != "transparent":

                    marker = Rectangle(data_set.marker_color, (x_pos - 5, y_pos - 5), (10, 10))
                    marker.draw(screen, position)

            graph_points.append((data_points, data_set.line_color))

        def on_graph(x: float, y: float) -> bool:
            """Return whether the coordinate point is in the visual area"""
            lower_x = position[0]
            upper_x = self.graph_panel.width + position[0]
            within_x = lower_x <= x <= upper_x
            close_to_x = math.isclose(x, lower_x) or math.isclose(x, upper_x)

            lower_y = position[1]
            upper_y = self.graph_panel.height + position[1]
            within_y = lower_y <= y <= upper_y
            close_to_y = math.isclose(y, lower_y) or math.isclose(y, upper_y)

            return (within_x or close_to_x) and (within_y or close_to_y)

        def bound_x(p1: Point, p2: Point) -> Point:
            """Return the point at the horizontal edge of the graph_panel bounds"""
            if p1[0] == p2[0]:
                return p1
            slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
            adjusted_x = min(max(position[0], p1[0]), position[0] + self.graph_panel.width)
            y = slope * (adjusted_x - p2[0]) + p2[1]

            return Point(adjusted_x, y)

        def bound_y(p1: Point, p2: Point) -> Point:
            """Return the point at the vertical edge of the graph_panel bounds"""
            adjusted_y = min(max(position[1], p1[1]), position[1] + self.graph_panel.height)
            if p1[0] == p2[0]:
                return Point(p1[0], adjusted_y)
            slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
            if slope == 0:
                return p1
            x = (adjusted_y - p2[1]) / slope + p2[0]

            return Point(x, adjusted_y)

        for data_set, line_color in graph_points:

            if data_set and line_color != "transparent":
                start_point = data_set[0].increment(position)

                for data_point in data_set[1:]:

                    end_point = data_point.increment(position)

                    if not on_graph(*start_point):
                        start_point = bound_x(start_point, end_point)
                        start_point = bound_y(start_point, end_point)

                    if not on_graph(*end_point):
                        end_point = bound_x(end_point, start_point)
                        end_point = bound_y(end_point, start_point)

                    pygame.draw.line(screen, line_color, tuple(start_point), tuple(end_point))

                    start_point = end_point

    def get_data_bounds(self) -> Dict[str, float]:
        """Get the bounds for all data sets"""
        min_x = min(data.get_min_x() for data in self.data)
        max_x = max(data.get_max_x() for data in self.data)
        min_y = min(data.get_min_y() for data in self.data)
        max_y = max(data.get_max_y() for data in self.data)

        return {
            'min_x': min_x,
            'max_x': max_x,
            'min_y': min_y,
            'max_y': max_y
        }

    def resize_bounds(self) -> None:
        """Resize the bounds to match the dataset
        """
        data_bounds = self.get_data_bounds()
        visible_domain = (data_bounds['min_x'], data_bounds['max_x'])
        visible_range = (data_bounds['min_y'], data_bounds['max_y'])

        self.visible_domain = visible_domain
        self.visible_range = visible_range

    def notify_button_click(self, observable: Any, value: Any) -> None:
        """Toggle auto scale upon button click
        """
        self.auto = not self.auto

    def add_data_set(self, data_set: List[Data.Data_format],
                     marker_color: str = "black", line_color: str = "black") -> Data:
        """Add a dataset to the graph's data
        """

        data = Data(data_set, marker_color, line_color)

        self._data.append(data)

        if self._auto:
            self.resize_bounds()

        return data

    @property
    def data(self) -> List[Data]:
        """Return the data of the graph"""
        return self._data

    @data.setter
    def data(self, value: List[Data.Data_format]) -> None:
        """Set the data set
        """

        self._data = [Data(data_set) for data_set in value]

        if self._auto:
            self.resize_bounds()

    @property
    def margins(self) -> Tuple[float, float, float, float]:
        """Return the margins of the Graph"""
        return self._margins

    @margins.setter
    def margins(self, value: Tuple[float, float, float, float]) -> None:
        self.left, self.right = value[0], value[2]
        self.bottom, self.top = value[1], value[3]
        self._margins = value

    @property
    def auto(self) -> bool:
        """Return whether the graph is on auto scale"""
        return self._auto

    @auto.setter
    def auto(self, value: bool):

        if self._bounds is not None:
            print('Auto: %s' % ('on' if value else 'off'))
            self._auto = value
            self.visible_domain = self._bounds[0]
            self.visible_range = self._bounds[1]


class Slider(Rectangle, Observable):
    """Drawable class that contains a draggable slider

    Also simulates the observer pattern (this object being the observable)
    """

    HORIZONTAL: Final[int] = 0
    VERTICAL: Final[int] = 1

    slider_bar: Rectangle
    orientation: int
    reverse: bool

    slider_range: Tuple[float, float]
    slider_depth: Final[float] = 20.0

    _slider_value: float
    _bar_offset: float

    def __init__(self, color: str, position: Union[Point, Tuple[float, float]] = Point(0, 0),
                 size: Union[Size, Tuple[float, float]] = Size(0, 0),
                 orientation: int = 0,
                 reverse: bool = False,
                 slider_range: Tuple[float, float] = (0, 1),
                 start_value: float = None):
        Rectangle.__init__(self, color, position, size, can_drag=False)
        Observable.__init__(self)

        self.orientation = orientation
        self.reverse = reverse

        self._bar_offset = 0

        self.slider_range = slider_range

        v_offset = (self.height - self.slider_depth) * orientation
        slider_size = (self.slider_depth, size[1]) if orientation == 0 else (size[0], self.slider_depth)
        slider_length = size[0] if orientation == 0 else size[1]
        start_value = slider_range[0] if start_value is None else start_value
        start_offset = (start_value - slider_range[0]) / (slider_range[1] - slider_range[0])
        slider_position = (self.x + slider_length * start_offset, self.y + v_offset)

        self.slider_bar = Rectangle("black", slider_position, slider_size, can_drag=False)
        self.slider_bar.start_drag = self.start_drag
        self.slider_bar.drag = self.drag
        self.slider_bar.can_drag = True

        self.slider_value = slider_position

    def draw(self, screen: pygame.Surface, position: Point = Point(0, 0)) -> None:
        """Draws the slider

        """

        super().draw(screen, position)
        self.slider_bar.draw(screen, position)

    def start_drag(self, event: pygame.event.Event) -> Optional[List[CustomMouseEvent]]:
        """Start the drag event"""
        events = Rectangle.start_drag(self.slider_bar, event)
        self._bar_offset = (self.slider_bar.position[self.orientation] - event.pos[self.orientation])

        return events

    def drag(self, event: pygame.event.Event) -> Optional[List[CustomMouseEvent]]:
        """Drag the self with the mouse

        Implementation note:
            - mouse position may not be over self
            - mouse button may be right click
        """

        slider = self.slider_bar

        if slider.drag_point is not None:

            dx = event.pos[0] - slider.drag_point.x
            dy = event.pos[1] - slider.drag_point.y
            inc = slider.position.increment((dx, dy))

            adjusted_x, adjusted_y = inc
            absolute_x, absolute_y = self.absolute_pos()

            if self.orientation == Slider.HORIZONTAL:
                adjusted_x += self._bar_offset
                adjusted_x = min(max(adjusted_x, absolute_x), absolute_x + self.width - self.slider_depth)
                adjusted_y -= dy

            elif self.orientation == Slider.VERTICAL:
                adjusted_y += self._bar_offset
                adjusted_y = min(max(adjusted_y, absolute_y), absolute_y + self.height - self.slider_depth)
                adjusted_x -= dx

            if Point(adjusted_x, adjusted_y) != slider.drag_point:
                self.slider_value = Point(adjusted_x, adjusted_y)

            slider.drag_point = Point(adjusted_x, adjusted_y)

            return [CustomMouseEvent(slider, self.drag, pygame.MOUSEMOTION)]

        return []

    @property
    def slider_value(self) -> float:
        """Return the value the slider position is currently at
        """
        return self._slider_value

    @slider_value.setter
    def slider_value(self, value: Union[Point, Tuple[float, float]]):

        pos = self.position[self.orientation]
        length = self.size[self.orientation]
        bar_pos = self.slider_bar.position[self.orientation]

        half_width = self.slider_depth / 2

        reverse_multiplier = -1 if self.reverse else 1

        pos += length - self.slider_depth if self.reverse else 0

        pos_1 = pos + half_width
        pos_2 = pos + length - half_width

        slide_width = pos_2 - pos_1

        cur_pos = (bar_pos - pos) * reverse_multiplier

        value_range = self.slider_range[1] - self.slider_range[0]

        self._slider_value = value_range * (cur_pos / slide_width) + self.slider_range[0]
        self.slider_bar.position = Point(*value)

        self.notify_observers(self._slider_value)
