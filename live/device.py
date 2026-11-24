"""Mock of Live.Device"""

from typing import TYPE_CHECKING, Callable, Optional
from .base import LomObject, Vector

if TYPE_CHECKING:
    from .track import Track
    from .device_parameter import DeviceParameter


class Device(LomObject):
    """Mock of Live.Device"""

    class View(LomObject):
        """Device view"""

        def __init__(self, device: 'Device'):
            super().__init__()
            self._device = device
            self._is_collapsed = False

        @property
        def canonical_parent(self) -> 'Device':
            return self._device

        @property
        def is_collapsed(self) -> bool:
            return self._is_collapsed

        @is_collapsed.setter
        def is_collapsed(self, val: bool) -> None:
            self._is_collapsed = val
            self._notify_listeners("is_collapsed")

        def add_is_collapsed_listener(self, callback: Callable[[], None]) -> None:
            self._add_listener("is_collapsed", callback)

        def remove_is_collapsed_listener(self, callback: Callable[[], None]) -> None:
            self._remove_listener("is_collapsed", callback)

        def is_collapsed_has_listener(self, callback: Callable[[], None]) -> bool:
            return self._has_listener("is_collapsed", callback)

    def __init__(self, name: str = "Device", parent: Optional['Track'] = None):
        super().__init__()
        self._name = name
        self._parent = parent
        self._parameters: Vector[DeviceParameter] = Vector()
        self._is_active = True
        self.view = self.View(self)

    @property
    def canonical_parent(self) -> Optional['Track']:
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
    def parameters(self) -> Vector['DeviceParameter']:
        """Get device parameters"""
        return self._parameters

    def add_parameters_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("parameters", callback)

    def remove_parameters_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("parameters", callback)

    def parameters_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("parameters", callback)

    @property
    def is_active(self) -> bool:
        return self._is_active

    @is_active.setter
    def is_active(self, val: bool) -> None:
        self._is_active = val
        self._notify_listeners("is_active")

    def add_is_active_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("is_active", callback)

    def remove_is_active_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("is_active", callback)

    def is_active_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("is_active", callback)

    @property
    def can_compare_ab(self) -> bool:
        return False

    @property
    def can_have_chains(self) -> bool:
        return False

    @property
    def can_have_drum_pads(self) -> bool:
        return False
