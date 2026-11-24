"""Mock of Live.Track"""

from typing import TYPE_CHECKING, Callable, Optional
from .base import LomObject, Vector
from .clip_slot import ClipSlot
from .device import Device

if TYPE_CHECKING:
    from .song import Song


class DeviceContainer(LomObject):
    """Base class for objects that can contain devices"""
    pass


class Track(DeviceContainer):
    """Mock of Live.Track"""

    class View(LomObject):
        """Track view"""

        def __init__(self, track: 'Track'):
            super().__init__()
            self._track = track
            self._is_collapsed = False
            self._selected_device: Optional[Device] = None

        @property
        def canonical_parent(self) -> 'Track':
            return self._track

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

        @property
        def selected_device(self) -> Optional[Device]:
            return self._selected_device

        @selected_device.setter
        def selected_device(self, device: Optional[Device]) -> None:
            self._selected_device = device
            self._notify_listeners("selected_device")

        def add_selected_device_listener(self, callback: Callable[[], None]) -> None:
            self._add_listener("selected_device", callback)

        def remove_selected_device_listener(self, callback: Callable[[], None]) -> None:
            self._remove_listener("selected_device", callback)

        def selected_device_has_listener(self, callback: Callable[[], None]) -> bool:
            return self._has_listener("selected_device", callback)

    def __init__(self, name: str = "Track", parent: Optional['Song'] = None, index: int = 0):
        super().__init__()
        self._name = name
        self._parent = parent
        self._index = index
        self._mute = False
        self._solo = False
        self._arm = False
        self._devices: Vector[Device] = Vector()
        self._clip_slots: Vector[ClipSlot] = Vector()
        self.view = self.View(self)

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
    def mute(self) -> bool:
        return self._mute

    @mute.setter
    def mute(self, val: bool) -> None:
        self._mute = val
        self._notify_listeners("mute")

    def add_mute_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("mute", callback)

    def remove_mute_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("mute", callback)

    def mute_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("mute", callback)

    @property
    def solo(self) -> bool:
        return self._solo

    @solo.setter
    def solo(self, val: bool) -> None:
        self._solo = val
        self._notify_listeners("solo")

    def add_solo_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("solo", callback)

    def remove_solo_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("solo", callback)

    def solo_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("solo", callback)

    @property
    def arm(self) -> bool:
        return self._arm

    @arm.setter
    def arm(self, val: bool) -> None:
        self._arm = val
        self._notify_listeners("arm")

    def add_arm_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("arm", callback)

    def remove_arm_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("arm", callback)

    def arm_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("arm", callback)

    @property
    def devices(self) -> Vector[Device]:
        return self._devices

    def add_devices_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("devices", callback)

    def remove_devices_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("devices", callback)

    def devices_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("devices", callback)

    def insert_device(self, device: Device, index: int = -1) -> None:
        """Insert a device at the specified index"""
        if index < 0 or index >= len(self._devices):
            self._devices.append(device)
        else:
            self._devices._items.insert(index, device)
        self._notify_listeners("devices")

    @property
    def clip_slots(self) -> Vector[ClipSlot]:
        return self._clip_slots

    def add_clip_slots_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("clip_slots", callback)

    def remove_clip_slots_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("clip_slots", callback)

    def clip_slots_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("clip_slots", callback)
