"""Mock of Live.DeviceParameter"""

from typing import TYPE_CHECKING, Callable, Optional
from enum import IntEnum

from .base import LomObject

if TYPE_CHECKING:
    from .device import Device


class AutomationState(IntEnum):
    """Automation state enum"""
    None_ = 0
    Overriding = 1
    Playing = 2


class DeviceParameter(LomObject):
    """Mock of Live.DeviceParameter - represents a parameter within a device"""

    def __init__(
        self,
        name: str = "Parameter",
        min_value: float = 0.0,
        max_value: float = 1.0,
        default_value: float = 0.5,
        parent: Optional['Device'] = None,
    ):
        super().__init__()
        self._name = name
        self._min = min_value
        self._max = max_value
        self._value = default_value
        self._default_value = default_value
        self._display_value = default_value
        self._automation_state = AutomationState.None_
        self._parent = parent

    @property
    def canonical_parent(self) -> Optional['Device']:
        return self._parent

    @property
    def name(self) -> str:
        """Parameter name"""
        return self._name

    def add_name_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("name", callback)

    def remove_name_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("name", callback)

    def name_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("name", callback)

    @property
    def value(self) -> float:
        """Parameter value (0-1 normalized)"""
        return self._value

    @value.setter
    def value(self, val: float) -> None:
        self._value = max(self._min, min(self._max, val))
        self._notify_listeners("value")

    def add_value_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("value", callback)

    def remove_value_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("value", callback)

    def value_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("value", callback)

    @property
    def display_value(self) -> float:
        """Parameter display value"""
        return self._display_value

    @display_value.setter
    def display_value(self, val: float) -> None:
        self._display_value = val
        self._notify_listeners("display_value")

    def add_display_value_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("display_value", callback)

    def remove_display_value_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("display_value", callback)

    def display_value_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("display_value", callback)

    @property
    def default_value(self) -> float:
        """Parameter default value"""
        return self._default_value

    @property
    def min(self) -> float:
        """Parameter minimum value"""
        return self._min

    @property
    def max(self) -> float:
        """Parameter maximum value"""
        return self._max

    @property
    def automation_state(self) -> AutomationState:
        """Get/Set automation state"""
        return self._automation_state

    @automation_state.setter
    def automation_state(self, state: AutomationState) -> None:
        self._automation_state = state
        self._notify_listeners("automation_state")

    def add_automation_state_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("automation_state", callback)

    def remove_automation_state_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("automation_state", callback)

    def automation_state_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("automation_state", callback)

    @property
    def state(self) -> str:
        """Parameter state as string"""
        return str(self._value)

    @state.setter
    def state(self, val: str) -> None:
        try:
            self.value = float(val)
        except (ValueError, TypeError):
            pass

    def add_state_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("state", callback)

    def remove_state_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("state", callback)

    def state_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("state", callback)

    def begin_gesture(self) -> None:
        """Begin a modification gesture"""
        pass

    def end_gesture(self) -> None:
        """End a modification gesture"""
        pass
