"""Mock of Live.ClipSlot"""

from typing import TYPE_CHECKING, Callable, Optional
from .base import LomObject
from .clip import Clip

if TYPE_CHECKING:
    from .track import Track


class ClipSlot(LomObject):
    """Mock of Live.ClipSlot"""

    def __init__(self, track: Optional['Track'] = None, index: int = 0):
        super().__init__()
        self._track = track
        self._index = index
        self._clip: Optional[Clip] = None
        self._has_clip = False
        self._is_recording = False

    @property
    def canonical_parent(self) -> Optional['Track']:
        return self._track

    @property
    def clip(self) -> Optional[Clip]:
        return self._clip

    @clip.setter
    def clip(self, clip: Optional[Clip]) -> None:
        self._clip = clip
        self._has_clip = clip is not None
        self._notify_listeners("clip")

    def add_clip_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("clip", callback)

    def remove_clip_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("clip", callback)

    def clip_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("clip", callback)

    @property
    def has_clip(self) -> bool:
        return self._has_clip

    def add_has_clip_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("has_clip", callback)

    def remove_has_clip_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("has_clip", callback)

    def has_clip_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("has_clip", callback)

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def add_is_recording_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("is_recording", callback)

    def remove_is_recording_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("is_recording", callback)

    def is_recording_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("is_recording", callback)

    def create_clip(self, length: int) -> Clip:
        """Create a new clip in this slot"""
        clip = Clip(f"Clip {self._index}", parent=self)
        self.clip = clip
        return clip

    def delete_clip(self) -> None:
        """Delete the clip in this slot"""
        self.clip = None

    def fire(self, force_legato: bool = False) -> None:
        """Fire/play this clip"""
        pass
