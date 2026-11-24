"""Mock of Live.Scene"""

from typing import TYPE_CHECKING, Callable, Optional
from .base import LomObject, Vector

if TYPE_CHECKING:
    from .clip_slot import ClipSlot
    from .song import Song


class Scene(LomObject):
    """Mock of Live.Scene"""

    def __init__(self, name: str = "Scene", parent: Optional['Song'] = None, index: int = 0):
        super().__init__()
        self._name = name
        self._parent = parent
        self._index = index
        self._clip_slots: Vector['ClipSlot'] = Vector()
        self._is_triggered = False
        self._tempo = 120.0
        self._tempo_enabled = False

    @property
    def canonical_parent(self) -> Optional['Song']:
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
    def clip_slots(self) -> Vector['ClipSlot']:
        return self._clip_slots

    def add_clip_slots_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("clip_slots", callback)

    def remove_clip_slots_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("clip_slots", callback)

    def clip_slots_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("clip_slots", callback)

    @property
    def is_triggered(self) -> bool:
        return self._is_triggered

    @is_triggered.setter
    def is_triggered(self, val: bool) -> None:
        self._is_triggered = val
        self._notify_listeners("is_triggered")

    def add_is_triggered_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("is_triggered", callback)

    def remove_is_triggered_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("is_triggered", callback)

    def is_triggered_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("is_triggered", callback)

    @property
    def tempo(self) -> float:
        return self._tempo

    @tempo.setter
    def tempo(self, val: float) -> None:
        self._tempo = val
        self._notify_listeners("tempo")

    def add_tempo_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("tempo", callback)

    def remove_tempo_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("tempo", callback)

    def tempo_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("tempo", callback)

    @property
    def tempo_enabled(self) -> bool:
        return self._tempo_enabled

    @tempo_enabled.setter
    def tempo_enabled(self, val: bool) -> None:
        self._tempo_enabled = val
        self._notify_listeners("tempo_enabled")

    def add_tempo_enabled_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("tempo_enabled", callback)

    def remove_tempo_enabled_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("tempo_enabled", callback)

    def tempo_enabled_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("tempo_enabled", callback)

    def fire(self, force_legato: bool = False) -> None:
        """Fire/play this scene"""
        self._is_triggered = True
        self._notify_listeners("is_triggered")
