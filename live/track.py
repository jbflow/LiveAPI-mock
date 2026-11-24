from typing import List, Optional, Callable

from .parameter import Device, Parameter
from .clip import Clip


class Track:
    """Mock of an Ableton Live track."""

    def __init__(self, name: str = "Track", track_id: int = 0):
        self.name = name
        self._track_id = track_id
        self.mute: bool = False
        self.solo: bool = False
        self.arm: bool = False
        self.devices: List[Device] = []
        self.clips: List[Clip] = []
        self.current_clip_index: int = 0
        self._listeners: List[Callable[[], None]] = []
        self._parameter_listeners: List[Callable[[str, float], None]] = []

    def add_device(self, device: Device) -> None:
        """Add a device to this track."""
        self.devices.append(device)

    def remove_device(self, device: Device) -> None:
        """Remove a device from this track."""
        if device in self.devices:
            self.devices.remove(device)

    def get_device(self, index: int) -> Optional[Device]:
        """Get device by index."""
        if 0 <= index < len(self.devices):
            return self.devices[index]
        return None

    def add_clip(self, clip: Clip) -> None:
        """Add a clip to this track."""
        self.clips.append(clip)

    def remove_clip(self, clip: Clip) -> None:
        """Remove a clip from this track."""
        if clip in self.clips:
            self.clips.remove(clip)

    def get_clip(self, index: int) -> Optional[Clip]:
        """Get clip by index."""
        if 0 <= index < len(self.clips):
            return self.clips[index]
        return None

    def get_parameter(self, name: str) -> Optional[Parameter]:
        """Get a parameter by name from this track's mixer device."""
        # In Ableton, tracks have volume, pan, etc. as mixer parameters
        # This is a simplified version
        return None

    def add_listener(self, callback: Callable[[], None]) -> None:
        """Register a callback for track changes."""
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[], None]) -> None:
        """Unregister a callback."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self) -> None:
        """Notify all listeners of changes."""
        for callback in self._listeners:
            try:
                callback()
            except Exception:
                pass
