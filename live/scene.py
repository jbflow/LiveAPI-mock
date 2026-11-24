from typing import List, Callable, Optional


class Scene:
    """Mock of an Ableton Live scene."""

    def __init__(self, name: str = "Scene", scene_id: int = 0):
        self.name = name
        self._scene_id = scene_id
        self.clip_index: Optional[int] = None
        self._listeners: List[Callable[[], None]] = []

    def add_listener(self, callback: Callable[[], None]) -> None:
        """Register a callback for scene changes."""
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
