"""Mock of Live.Clip"""

from typing import TYPE_CHECKING, Callable, Optional
from .base import LomObject, Vector, IntVector

if TYPE_CHECKING:
    from .clip_slot import ClipSlot


class Clip(LomObject):
    """Mock of Live.Clip"""

    class View(LomObject):
        """Clip view"""

        def __init__(self, clip: 'Clip'):
            super().__init__()
            self._clip = clip

        @property
        def canonical_parent(self) -> 'Clip':
            return self._clip

        def show_loop(self) -> None:
            """Show loop in detail view"""
            pass

    def __init__(self, name: str = "Clip", parent: Optional['ClipSlot'] = None):
        super().__init__()
        self._name = name
        self._parent = parent
        self._is_audio_clip = False
        self._is_midi_clip = True
        self._start_marker = 0.0
        self._end_marker = 4.0
        self._loop_start = 0.0
        self._loop_end = 4.0
        self._loop_length = 4.0
        self._midi_notes: Vector[tuple] = Vector()  # (pitch, start, duration, velocity)
        self.view = self.View(self)

    @property
    def canonical_parent(self) -> Optional['ClipSlot']:
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str) -> None:
        self._name = val
        self._notify_listeners("name")

    def add_name_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("name", callback)

    def remove_name_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("name", callback)

    def name_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("name", callback)

    @property
    def is_audio_clip(self) -> bool:
        return self._is_audio_clip

    @property
    def is_midi_clip(self) -> bool:
        return self._is_midi_clip

    @property
    def start_marker(self) -> float:
        return self._start_marker

    @start_marker.setter
    def start_marker(self, val: float) -> None:
        self._start_marker = val
        self._notify_listeners("start_marker")

    def add_start_marker_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("start_marker", callback)

    def remove_start_marker_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("start_marker", callback)

    def start_marker_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("start_marker", callback)

    @property
    def end_marker(self) -> float:
        return self._end_marker

    @end_marker.setter
    def end_marker(self, val: float) -> None:
        self._end_marker = val
        self._notify_listeners("end_marker")

    def add_end_marker_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("end_marker", callback)

    def remove_end_marker_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("end_marker", callback)

    def end_marker_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("end_marker", callback)

    @property
    def loop_start(self) -> float:
        return self._loop_start

    @loop_start.setter
    def loop_start(self, val: float) -> None:
        self._loop_start = val
        self._notify_listeners("loop_start")

    def add_loop_start_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("loop_start", callback)

    def remove_loop_start_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("loop_start", callback)

    def loop_start_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("loop_start", callback)

    @property
    def loop_end(self) -> float:
        return self._loop_end

    @loop_end.setter
    def loop_end(self, val: float) -> None:
        self._loop_end = val
        self._notify_listeners("loop_end")

    def add_loop_end_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("loop_end", callback)

    def remove_loop_end_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("loop_end", callback)

    def loop_end_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("loop_end", callback)

    @property
    def loop_length(self) -> float:
        return self._loop_length

    def set_notes(self, notes: IntVector) -> None:
        """Set notes (pitch, startTime, duration, velocity)"""
        pass

    def get_notes(self) -> Vector[tuple]:
        """Get all notes in clip"""
        return self._midi_notes
