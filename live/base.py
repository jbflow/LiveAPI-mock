"""Base classes and types for Live Object Model mock"""

from typing import Generic, TypeVar, List, Any, Callable, Optional


T = TypeVar('T')


class LomObject:
    """Base class for all Live Object Model objects"""

    def __init__(self):
        self._listeners: dict[str, List[Callable[[], None]]] = {}
        self._live_ptr = id(self)

    @property
    def canonical_parent(self) -> Optional['LomObject']:
        """Get the canonical parent of this object"""
        return None

    def _add_listener(self, property_name: str, callback: Callable[[], None]) -> None:
        """Add a listener to a property"""
        if property_name not in self._listeners:
            self._listeners[property_name] = []
        if callback not in self._listeners[property_name]:
            self._listeners[property_name].append(callback)

    def _remove_listener(self, property_name: str, callback: Callable[[], None]) -> None:
        """Remove a listener from a property"""
        if property_name in self._listeners:
            if callback in self._listeners[property_name]:
                self._listeners[property_name].remove(callback)

    def _has_listener(self, property_name: str, callback: Callable[[], None]) -> bool:
        """Check if a listener is registered"""
        return property_name in self._listeners and callback in self._listeners[property_name]

    def _notify_listeners(self, property_name: str) -> None:
        """Notify all listeners of a property change"""
        if property_name in self._listeners:
            for callback in self._listeners[property_name][:]:  # Copy list to avoid modification during iteration
                try:
                    callback()
                except Exception:
                    pass


class Vector(LomObject, Generic[T]):
    """Mock of Live.Base.Vector for collections"""

    def __init__(self, items: Optional[List[T]] = None):
        super().__init__()
        self._items = items or []

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def __iter__(self):
        return iter(self._items)

    def append(self, item: T) -> None:
        self._items.append(item)
        self._notify_listeners("content")

    def remove(self, item: T) -> None:
        if item in self._items:
            self._items.remove(item)
            self._notify_listeners("content")

    def clear(self) -> None:
        self._items.clear()
        self._notify_listeners("content")

    def copy(self) -> List[T]:
        return self._items.copy()


class StringVector(Vector[str]):
    """Mock of Live.Base.StringVector"""
    pass


class IntVector(Vector[int]):
    """Mock of Live.Base.IntVector"""
    pass


class IntU64Vector(Vector[int]):
    """Mock of Live.Base.IntU64Vector"""
    pass
