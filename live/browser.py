from typing import List, Optional, Callable

from .parameter import Device, Parameter


class Browser:
    """Mock of Ableton Live's device browser."""

    def __init__(self):
        self._device_library: dict = {}
        self._current_location: List[str] = []
        self._listeners: List[Callable[[], None]] = []

    def load_device(self, device_name: str, track=None) -> Optional[Device]:
        """Load a device from the browser into a track."""
        device = Device(device_name)

        # Add some default parameters based on device type
        if device_name.lower() in ["operator", "wavetable", "sampler"]:
            device.add_parameter(Parameter("Volume", 0.0, 1.0, 1.0))
            device.add_parameter(Parameter("Pan", -1.0, 1.0, 0.0))
        elif device_name.lower() in ["eq-eight", "eq-two"]:
            device.add_parameter(Parameter("Gain", -24.0, 24.0, 0.0))
            device.add_parameter(Parameter("Freq", 20.0, 20000.0, 1000.0))
        else:
            device.add_parameter(Parameter("Param1", 0.0, 1.0, 0.5))
            device.add_parameter(Parameter("Param2", 0.0, 1.0, 0.5))

        if track:
            track.add_device(device)

        return device

    def navigate(self, path: List[str]) -> None:
        """Navigate to a location in the device browser."""
        self._current_location = path.copy()
        self._notify_listeners()

    def get_current_location(self) -> List[str]:
        """Get the current browser location."""
        return self._current_location.copy()

    def add_listener(self, callback: Callable[[], None]) -> None:
        """Register a callback for browser changes."""
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
