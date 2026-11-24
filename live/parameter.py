from typing import List, Optional, Callable, Any


class Parameter:
    """Mock of an Ableton Live device parameter."""

    def __init__(
        self,
        name: str,
        min_value: float = 0.0,
        max_value: float = 1.0,
        default_value: float = 0.5,
        param_id: int = 0,
    ):
        self.name = name
        self.min = min_value
        self.max = max_value
        self.value = default_value
        self._parameter_id = param_id
        self._on_change_callbacks: List[Callable[[float], None]] = []

    def add_value_listener(self, callback: Callable[[float], None]) -> None:
        """Register a callback for when parameter value changes."""
        self._on_change_callbacks.append(callback)

    def remove_value_listener(self, callback: Callable[[float], None]) -> None:
        """Unregister a callback."""
        if callback in self._on_change_callbacks:
            self._on_change_callbacks.remove(callback)

    def _notify_listeners(self, value: float) -> None:
        """Notify all listeners of value change."""
        for callback in self._on_change_callbacks:
            try:
                callback(value)
            except Exception:
                pass


class Device:
    """Mock of an Ableton Live device."""

    def __init__(self, name: str, device_id: int = 0):
        self.name = name
        self._device_id = device_id
        self.parameters: List[Parameter] = []
        self.chains: List[Any] = []

    def add_parameter(self, parameter: Parameter) -> None:
        """Add a parameter to this device."""
        self.parameters.append(parameter)

    def get_parameter(self, index: int) -> Optional[Parameter]:
        """Get parameter by index."""
        if 0 <= index < len(self.parameters):
            return self.parameters[index]
        return None
