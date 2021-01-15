"""Drawable shapes built for Pygame

"""

from __future__ import annotations
import pygame
import datetime
from extra_objects import Observer, Observable
from dataclasses import dataclass
from typing import Callable, Union, List, Tuple, Dict, Any, Optional, Final


@dataclass
class Point:
    """Class that contains information about a singular point on an x-y plane

    The point is not necessarily a point on the visual screen, hence may be negative.

    Instance Attributes:
        - x: the x position (increasing from the left to right)
        - y: the y position (increasing from the top to bottom)

    Representation Invariants:
        - self.x == self.x  # check if float is NaN
        - self.y == self.y  # check if float is NaN

    >>> a = Point(1.5, 2.75)
    >>> a.x
    1.5
    >>> a.y
    2.75
    """

    x: float
    y: float

    def increment(self, offset: Optional[Point, Tuple[float, float]]) -> Point:
        """Return a new point that is the sum of the two points

        >>> a = Point(1, 2)
        >>> b = Point(3, 4)
        >>> c = a.increment(b)
        >>> c.x
        4
        >>> d = Point.increment(c, a)
        >>> d.y
        8
        """

        return Point(self[0] + offset[0], self[1] + offset[1])

    def __getitem__(self, item: Any) -> float:
        """Special method override to emulate list/tuple-like behavior

        >>> a = Point(1, 2)
        >>> a[0]
        1
        >>> a[1]
        2
        """

        if type(item) != int:
            raise ValueError(f'indices must be int, not {type(item).__name__}')

        if item == 0 or item == -2:
            return self.x
        elif item == 1 or item == -1:
            return self.y
        else:
            raise IndexError("point index out of range")

    def clone(self) -> Point:
        """Return a Point with the same coordinates as self

        >>> a = Point(1, 2)
        >>> b = a.clone()
        >>> a.x == b.x and a.y == b.y
        True
        """
        return Point(*self)


@dataclass
class Size:
    """Class that contains information about the size of an object

    Instance Attributes:
        - width: the width of the object
        - height: the height of the object

    Representation Invariants:
        - 0 <= self.width
        - 0 <= self.height
        - self.width == self.width  # check if float is NaN
        - self.height == self.height  # check if float is NaN

    >>> a = Size(1, 2)
    >>> a.width
    1
    >>> a.height
    2
    """

    width: float
    height: float

    def __getitem__(self, item: Any) -> float:
        """Special method override to emulate list/tuple-like behavior

        >>> a = Size(1, 2)
        >>> a[0]
        1
        >>> a[1]
        2
        """

        if type(item) != int:
            raise ValueError(f'indices must be int, not {type(item).__name__}')

        if item == 0 or item == -2:
            return self.width
        elif item == 1 or item == -1:
            return self.height
        else:
            raise IndexError("point index out of range")

    def clone(self) -> Size:
        """Return a Size with the same dimensions as self

        >>> a = Size(1, 2)
        >>> b = a.clone()
        >>> a.width == b.width and a.height == b.height
        True
        """
        return Size(*self)


class Data:
    """Drawable class that plots points

    The points used for the data should not be confused with the (x, y) points on the screen.
    These points represent (x, y) that figuratively exist within the panel the data is being drawn on.

    Furthermore, x and y do not need to be floats.
    The current requirement is that the value can be scaled into a float
        (the division of two differences is a float)
    e.g. timedelta / timedelta is a float, which is equivalent to
        (datetime - datetime) / (datetime - datetime)

    Instance Attributes:
        - data: a collection of discrete points
        - marker_color: the color of the marker when plotted onto a graph
        - line_color: the color of the line between points when plotted onto a graph

    Static Attributes:
        - SUPPORTED_X: final constant custom Typing for supported x types
        - SUPPORTED_Y: final constant custom Typing for supported y types
        - Data_format: final constant custom Typing for the domain and co-domain types

    >>> data_a = [(0, 10), (1, 30), (2, 20)]
    >>> a = Data(data_a)
    >>> datetime_1 = datetime.datetime(year=2001, month=11, day=6, hour=1)
    >>> datetime_2 = datetime.datetime(year=1998, month=10, day=29, hour=6)
    >>> b = Data([(datetime_1, 10), (datetime_2, 11)])
    >>> date_1 = datetime.date(year=2020, month=12, day=25)
    >>> date_2 = datetime.date(year=2021, month=1, day=1)
    >>> c = Data([(date_1, 3), (date_2, 4)])
    """

    SUPPORTED_X = Union[datetime.date, datetime.datetime, float]
    SUPPORTED_Y = Union[float]

    Data_format = Final[Tuple[SUPPORTED_X, SUPPORTED_Y]]

    data: List[Data_format]

    marker_color: str
    line_color: str

    def __init__(self, data: List[Data_format],
                 marker_color: str = "black", line_color: str = "black",
                 start_x: SUPPORTED_X = 0, start_y: SUPPORTED_Y = 0):
        self.data = data
        self.start_x = start_x
        self.start_y = start_y

        self.marker_color = marker_color
        self.line_color = line_color

    def get_domain_and_range(self) -> Dict[str, float]:
        """Return the domain and range of the dataset"""

        return {
            'min_x': self.get_min_x(),
            'max_x': self.get_max_x(),
            'min_y': self.get_min_y(),
            'max_y': self.get_max_y()
        }

    def get_domain(self) -> Tuple[SUPPORTED_X, SUPPORTED_X]:
        """Return the domain of the dataset"""
        return (self.get_min_x(), self.get_max_x())

    def get_range(self) -> Tuple[SUPPORTED_Y, SUPPORTED_Y]:
        """Return the range of the dataset"""
        return (self.get_min_y(), self.get_max_y())

    def get_min_x(self) -> SUPPORTED_X:
        """Return the minimum x value of the dataset"""
        return min(data_point[0] for data_point in self.data)

    def get_max_x(self) -> SUPPORTED_X:
        """Return the maximum x value of the dataset"""
        return max(data_point[0] for data_point in self.data)

    def get_min_y(self) -> SUPPORTED_Y:
        """Return the minimum y value of the dataset"""
        return min(data_point[1] for data_point in self.data)

    def get_max_y(self) -> SUPPORTED_Y:
        """Return the maximum y value of the dataset"""
        return max(data_point[1] for data_point in self.data)

    def __iter__(self) -> Data:
        """Special method override to start iterative process

        >>> a = Data([(0, 10), (1, 30), (2, 20)])
        >>> data_point = (-1, -1)  # to remove linter bug
        >>> xs = [data_point[0] for data_point in a]
        >>> xs
        [0, 1, 2]
        """
        self._iter = 0
        return self

    def __next__(self) -> Data_format:
        """Special method override to iterate through self.data"""
        if self._iter < len(self.data):
            self._iter += 1
            return self.data[self._iter - 1]
        else:
            raise StopIteration


class PygameObject:
    """Base class for any pygame object

    Instance Attributes
        - parent: object that contains this one (used for absolute coordinates)
        - position: position of the object relative to its parent's (0, 0)
    """

    position: Point

    parent: PygameObject

    def __init__(self, position: Union[Point, Tuple[float, float]]):
        self.position = Point(*position)
        self.parent = self

    def absolute_pos(self) -> Point:
        """Return the absolute position of the Drawable

        The absolute position is relative to the (0, 0) of the screen.
        """

        if self.parent is self:
            return self.position

        return Point.increment(self.position, self.parent.absolute_pos())

    @property
    def x(self) -> float:
        """Return the x value of position

        Read-only property for the x position of this object

        >>> a = PygameObject((10, 20))
        >>> a.x
        10
        """
        return self.position.x

    @property
    def y(self) -> float:
        """Return the y value of position

        Read-only property for the y position of this object
        >>> a = PygameObject((10, 20))
        >>> a.y
        20
        """
        return self.position.y


class Drawable(PygameObject):
    """Interface to implement the .draw function
    """

    def draw(self, screen: pygame.Surface, position: Point = Point(0, 0)) -> None:
        """Abstract method.

        This function is called to draw the visual features of the object

        Implement this function to draw the object"""

        raise NotImplementedError


class CustomMouseEvent:
    """Custom event handler outside of pygame

    Instance Attributes:
        - event_object: the object that should be triggered by the event
        - event_type: the pygame.CONSTANTS event type
        - handle_event: the function to be called when the event is triggered

    Static Attributes
        - event_map: mapping of each event handler to its respective events
        - event_handlers: list of all

    """

    event_map: Dict[PygameObject, List[CustomMouseEvent]] = {}

    event_handlers: List[PygameObject] = []

    event_object: PygameObject
    event_type: int  # Union[pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]

    handle_event: Callable[[pygame.event.Event], Optional[List[CustomMouseEvent]]]

    def __init__(self, event_object: PygameObject,
                 event_action: Callable[[pygame.event.Event], Optional[List[CustomMouseEvent]]],
                 event_type: int):

        self.event_object = event_object
        self.event_type = event_type
        self._event_action = event_action

        def handle_event(event: pygame.event.Event) -> Optional[List[CustomMouseEvent]]:
            """Wrapper function of the event_action

            Implemented for wrapper functionality in the future.
            """
            output = event_action(event)

            return output

        self.handle_event = handle_event

    def __eq__(self, other: CustomMouseEvent):
        """Equality override"""

        a = self.event_object == other.event_object
        b = self.event_type == other.event_type
        c = self._event_action == other._event_action

        return a and b and c

    @staticmethod
    def play_events(event: pygame.event.Event) -> None:
        """Run through all the MouseEvents"""

        for handler in CustomMouseEvent.event_handlers[::-1]:
            mouse_events = CustomMouseEvent.event_map[handler]
            new_events = []
            for mouse_event in mouse_events:
                if event.type == mouse_event.event_type:
                    new_events.extend(mouse_event.handle_event(event))
                else:
                    new_events.append(mouse_event)

            if CustomMouseEvent.event_map[handler] != new_events:
                CustomMouseEvent.event_map[handler] = new_events
                return
            CustomMouseEvent.event_map[handler] = new_events

    @staticmethod
    def add_event(event_handler: PygameObject,
                  event_action: Callable[[pygame.event], Optional[List[CustomMouseEvent]]],
                  event_type: int):
        """Adds an MouseDown event to the CustomMouseEvent
        """

        new_event = CustomMouseEvent(event_handler, event_action, event_type)
        new_event.event_type = pygame.MOUSEBUTTONDOWN

        if event_handler not in CustomMouseEvent.event_map:
            CustomMouseEvent.event_handlers.append(event_handler)
            CustomMouseEvent.event_map[event_handler] = []

        CustomMouseEvent.event_map[event_handler].append(new_event)


class Draggable(PygameObject):
    """Abstract base class that implements behavior for dragging

    """

    _can_drag: bool

    drag_point: Optional[Point] = None

    mouse_down_event: CustomMouseEvent
    mouse_drag_event: CustomMouseEvent
    mouse_up_event: CustomMouseEvent

    def __init__(self, position: Union[Point, Tuple[float, float]],
                 can_drag: bool = False) -> None:
        super().__init__(position)

        self._can_drag = can_drag

        Draggable.designer(self)

    def designer(self) -> None:
        """Section for designing the functionality of the Draggable
        """
        if self._can_drag:
            CustomMouseEvent.add_event(self, self.start_drag, pygame.MOUSEBUTTONDOWN)

    def start_drag(self, event: pygame.event.Event) -> Optional[List[CustomMouseEvent]]:
        """Begin the dragging process

        Implementation note:
            - mouse position may not be over self
            - mouse button may be right click
        """

        if not self._can_drag:
            return [CustomMouseEvent(self, self.start_drag, pygame.MOUSEBUTTONDOWN)]

        self.drag_point = Point(*event.pos)

        return [CustomMouseEvent(self, self.drag, pygame.MOUSEMOTION),
                CustomMouseEvent(self, self.end_drag, pygame.MOUSEBUTTONUP)]

    def drag(self, event: pygame.event.Event) -> Optional[List[CustomMouseEvent]]:
        """Drag the self with the mouse

        Implementation note:
            - mouse position may not be over self
            - mouse button may be right click
        """

        if self.drag_point is not None:

            dx = event.pos[0] - self.drag_point.x
            dy = event.pos[1] - self.drag_point.y

            self.position = self.position.increment((dx, dy))

            self.drag_point = Point(*event.pos)

            return [CustomMouseEvent(self, self.drag, pygame.MOUSEMOTION)]

        return []

    def end_drag(self, event: pygame.event.Event) -> Optional[List[CustomMouseEvent]]:
        """End the dragging process

        Implementation note:
            - mouse position may not be over self
            - mouse button may be right click
        """

        self.drag_point = None
        return [CustomMouseEvent(self, self.start_drag, pygame.MOUSEBUTTONDOWN)]

    @property
    def can_drag(self) -> bool:
        """Return whether this item is draggable
        """
        return self._can_drag

    @can_drag.setter
    def can_drag(self, value: bool):
        self._can_drag = value
        CustomMouseEvent.add_event(self, self.start_drag, pygame.MOUSEBUTTONDOWN)


class Rectangle(Drawable, Draggable):
    """Drawable class that contains information about a rectangle on an (x, y) plane

    """

    _size: Size

    width: float
    height: float

    color: str

    def __init__(self, color: str, position: Union[Point, Tuple[float, float]] = Point(0, 0),
                 size: Union[Size, Tuple[float, float]] = Size(0, 0),
                 can_drag: bool = False):
        Draggable.__init__(self, position, can_drag)

        self._size = self.size = Size(*size)

        self.color = color

    def draw(self, screen: pygame.Surface, position: Point = Point(0, 0)) -> None:
        """Draws the rectangle"""

        absolute_position = Point.increment(self.position, position)
        rectangle = (tuple(absolute_position), tuple(self._size))

        pygame.draw.rect(screen, self.color, rectangle)

    def start_drag(self, event: pygame.event.Event) -> Optional[List[CustomMouseEvent]]:
        """Override Draggable start_drag
        """
        if self.is_mouse_over(event) and event.button == 1:
            return super().start_drag(event)

        return [CustomMouseEvent(self, self.start_drag, pygame.MOUSEBUTTONDOWN)]

    def end_drag(self, event: pygame.event.Event) -> Optional[List[CustomMouseEvent]]:
        """Override Draggable end_drag
        """
        if event.button == 1:
            return super().end_drag(event)

        return [CustomMouseEvent(self, self.end_drag, pygame.MOUSEBUTTONUP)]

    def is_mouse_over(self, event: pygame.event.Event) -> bool:
        """Return whether or not the mouse is over the Rectangle
        """

        absolute_position = self.absolute_pos()
        within_x = absolute_position.x < event.pos[0] < absolute_position.x + self.width
        within_y = absolute_position.y < event.pos[1] < absolute_position.y + self.height
        return within_x and within_y

    @property
    def size(self) -> Size:
        """Return the size of the Rectangle"""
        return self._size

    @size.setter
    def size(self, value: Size):
        self.width = value[0]  # Size.width
        self.height = value[1]  # Size.height

        self._size.width = self.width
        self._size.height = self.height


class Line(Drawable):
    """Drawable class that contains information about a line (two coordinates on an (x, y) plane
    """

    # start point is the position from the Drawable class
    end_point: Point

    color: str

    def __init__(self, color: str,
                 start_point: Union[Point, Tuple[float, float]] = (0, 0),
                 end_point: Union[Point, Tuple[float, float]] = (0, 0)):
        super().__init__(start_point)

        self.color = color
        self.end_point = Point(*end_point)

    def draw(self, screen: pygame.Surface, position: Point = Point(0, 0)) -> None:
        """Draws a line between the start_point and end_point"""
        absolute_start = Point.increment(self.position, position)
        absolute_end = Point.increment(self.end_point, position)

        pygame.draw.line(screen, self.color, tuple(absolute_start), tuple(absolute_end))


pygame.font.init()  # initialize fonts (must do this to create any fonts)


class TextBox(Rectangle):
    """Drawable class that can contain text

    """

    _text: str
    _text_surface: pygame.Surface

    font: pygame.font

    observer: Observer

    def __init__(self, text: str = '', text_color: Tuple[int, int, int] = (0, 0, 0),
                 position: Union[Point, Tuple[float, float]] = Point(0, 0),
                 font_name: str = "Arial", font_size: int = 24,
                 horizontal_alignment: int = 0, vertical_alignment: int = 0,
                 background_color: str = "white"):
        super().__init__(background_color, position=position)

        self.text_color = text_color
        self.font = pygame.font.SysFont(font_name, font_size)

        self._text = self.text = text

        self.horizontal_alignment = horizontal_alignment
        self.vertical_alignment = vertical_alignment

        half_width = 0
        half_height = 0

        if self.horizontal_alignment == 1:
            half_width = self.width / 2
        elif self.horizontal_alignment == 2:
            half_width = self.width

        if self.vertical_alignment == 1:
            half_height = self.height / 2
        elif self.vertical_alignment == 2:
            half_height = self.height

        self.position = self.position.increment((-half_width, -half_height))

        self.observer = Observer(self.notify_update)

    def draw(self, screen: pygame.Surface, position: Point = Point(0, 0)) -> None:
        """Draw the text onto the screen
        """

        if self.color != "transparent":
            super().draw(screen, position)

        absolute_position = Point.increment(self.position, position)

        screen.blit(self._text_surface, tuple(absolute_position))

    @property
    def text(self) -> str:
        """Return the text displayed by the text box"""
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value
        self._text_surface = self.font.render(self.text, True, self.text_color)
        self.size = (self._text_surface.get_width(), self._text_surface.get_height())

    def notify_update(self, observable: Any, value: Any) -> None:
        """Receive notice of update
        """
        self.text = str(value)


class Panel(Drawable):
    """Drawable class that can contain multiple drawables.

    Instance Attributes:
        - elements: list of drawable elements to be drawn at the same time
        - position: top left point of the panel

    Representation Invariants:
        -

    """

    _size: Union[Size, Tuple[float, float]]

    width: float
    height: float

    _elements: List[Drawable]
    _element_map: Dict[str, Drawable]

    background_color: str = "yellow"
    line_color: str = "black"
    text_color: str = "black"

    def __init__(self, position: Union[Point, Tuple[float, float]] = Point(0, 0),
                 size: Union[Size, Tuple[float, float]] = Size(0, 0)):

        super().__init__(position)

        self._size = self.size = Size(*size)
        self._elements = []
        self._element_map = {}

        Panel.designer(self)

    def draw(self, screen: pygame.Surface, position: Point = Point(0, 0)) -> None:
        """Draw all children elements
        The first element in elements is drawn first, meaning that it will be on the bottom.
        """

        for element in self._elements:
            element.draw(screen, Point.increment(position, self.position))

    def designer(self) -> None:
        """Section for designing the visual aesthetic of the Panel
        """
        background = Rectangle(self.background_color, Point(0, 0), self.size)
        self.add_component(background, "background")

    def add_component(self, element: Drawable, name: str, index: int = -1) -> Optional[Drawable]:
        """Adds a drawable component to the panel

        index is where to append the Drawable element.
            - negatives are preferred as they start from the top
            - index = 0 is drawn on the bottom
            - index = -1 is drawn on the top
        """
        if name in self._element_map:
            index = self._elements.index(self._element_map[name])
            removed_element = self._elements.pop(index)
            self._elements.insert(index, element)
        else:
            self._elements.append(None)
            self._elements.insert(index, element)
            removed_element = self._elements.pop()

        element.parent = self
        self._element_map[name] = element

        return removed_element

    def get_component(self, element_name: str) -> Optional[Drawable]:
        """Return the element associated with the given element_name
        Return None if the associated element_name is not in the mapping
        """
        if element_name in self._element_map:
            return self._element_map[element_name]
        return None

    @property
    def size(self) -> Size:
        """Return the size of the Rectangle"""
        return self._size

    @size.setter
    def size(self, value: Union[Size, Tuple[float, float]]):
        self.width = value[0]  # Size.width
        self.height = value[1]  # Size.height

        self._size.width = self.width
        self._size.height = self.height


class Button(Rectangle, Observable):
    """Drawable class that can be clicked"""

    value: bool

    primary_color: str = "green"
    secondary_color: str = "red"

    def __init__(self,
                 position: Union[Point, Tuple[float, float]],
                 size: Union[Size, Tuple[float, float]],
                 initial_value: bool = True):
        Rectangle.__init__(self, self.primary_color, position, size)
        Observable.__init__(self)

        self.value = initial_value

        Button.designer(self)

    def draw(self, screen: pygame.Surface, position: Point = Point(0, 0)) -> None:
        """Draws the button
        """
        super().draw(screen, position)

    def designer(self) -> None:
        """Adds the features to the button"""

        CustomMouseEvent.add_event(self, self.click, pygame.MOUSEBUTTONDOWN)

    def click(self, event: pygame.event.Event) -> Optional[List[CustomMouseEvent]]:
        """Click event
        """

        if self.is_mouse_over(event) and event.button == 1:

            self.value = not self.value

            if self.value:
                self.color = self.primary_color
            else:
                self.color = self.secondary_color

            self.notify_observers(self.value)

        return [CustomMouseEvent(self, self.click, pygame.MOUSEBUTTONDOWN)]
