"""Mock of Live.Song"""

from typing import Callable, Optional
from .base import LomObject, Vector
from .track import Track
from .scene import Scene
from .clip import Clip
from .clip_slot import ClipSlot


class Song(LomObject):
    """Mock of Live.Song"""

    class View(LomObject):
        """Song view"""

        def __init__(self, song: 'Song'):
            super().__init__()
            self._song = song
            self._detail_clip: Optional[Clip] = None
            self._follow_song = True
            self._draw_mode = False

        @property
        def canonical_parent(self) -> 'Song':
            return self._song

        @property
        def detail_clip(self) -> Optional[Clip]:
            return self._detail_clip

        @detail_clip.setter
        def detail_clip(self, clip: Optional[Clip]) -> None:
            self._detail_clip = clip
            self._notify_listeners("detail_clip")

        def add_detail_clip_listener(self, callback: Callable[[], None]) -> None:
            self._add_listener("detail_clip", callback)

        def remove_detail_clip_listener(self, callback: Callable[[], None]) -> None:
            self._remove_listener("detail_clip", callback)

        def detail_clip_has_listener(self, callback: Callable[[], None]) -> bool:
            return self._has_listener("detail_clip", callback)

        @property
        def follow_song(self) -> bool:
            return self._follow_song

        @follow_song.setter
        def follow_song(self, val: bool) -> None:
            self._follow_song = val
            self._notify_listeners("follow_song")

        def add_follow_song_listener(self, callback: Callable[[], None]) -> None:
            self._add_listener("follow_song", callback)

        def remove_follow_song_listener(self, callback: Callable[[], None]) -> None:
            self._remove_listener("follow_song", callback)

        def follow_song_has_listener(self, callback: Callable[[], None]) -> bool:
            return self._has_listener("follow_song", callback)

        @property
        def draw_mode(self) -> bool:
            return self._draw_mode

        @draw_mode.setter
        def draw_mode(self, val: bool) -> None:
            self._draw_mode = val
            self._notify_listeners("draw_mode")

        def add_draw_mode_listener(self, callback: Callable[[], None]) -> None:
            self._add_listener("draw_mode", callback)

        def remove_draw_mode_listener(self, callback: Callable[[], None]) -> None:
            self._remove_listener("draw_mode", callback)

        def draw_mode_has_listener(self, callback: Callable[[], None]) -> bool:
            return self._has_listener("draw_mode", callback)

    def __init__(self):
        super().__init__()
        self._is_playing = False
        self._tempo = 120.0
        self._current_song_time = 0.0
        self._tracks: Vector[Track] = Vector()
        self._scenes: Vector[Scene] = Vector()
        self.view = self.View(self)

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    @is_playing.setter
    def is_playing(self, val: bool) -> None:
        self._is_playing = val
        self._notify_listeners("is_playing")

    def add_is_playing_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("is_playing", callback)

    def remove_is_playing_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("is_playing", callback)

    def is_playing_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("is_playing", callback)

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
    def current_song_time(self) -> float:
        return self._current_song_time

    @property
    def tracks(self) -> Vector[Track]:
        return self._tracks

    def add_tracks_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("tracks", callback)

    def remove_tracks_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("tracks", callback)

    def tracks_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("tracks", callback)

    def create_track(self, index: int = -1) -> Track:
        """Create a new track"""
        track = Track(f"Track {len(self._tracks)}", parent=self, index=len(self._tracks))
        # Add clip slots for each scene
        for _ in self._scenes:
            track.clip_slots.append(ClipSlot(track, len(track.clip_slots)))
        if index < 0 or index >= len(self._tracks):
            self._tracks.append(track)
        else:
            self._tracks._items.insert(index, track)
        self._notify_listeners("tracks")
        return track

    @property
    def scenes(self) -> Vector[Scene]:
        return self._scenes

    def add_scenes_listener(self, callback: Callable[[], None]) -> None:
        self._add_listener("scenes", callback)

    def remove_scenes_listener(self, callback: Callable[[], None]) -> None:
        self._remove_listener("scenes", callback)

    def scenes_has_listener(self, callback: Callable[[], None]) -> bool:
        return self._has_listener("scenes", callback)

    def create_scene(self, index: int = -1) -> Scene:
        """Create a new scene"""
        scene = Scene(f"Scene {len(self._scenes)}", parent=self, index=len(self._scenes))
        # Add a clip slot for each track
        for track in self._tracks:
            track.clip_slots.append(ClipSlot(track, len(track.clip_slots)))
            scene.clip_slots.append(track.clip_slots[-1])
        if index < 0 or index >= len(self._scenes):
            self._scenes.append(scene)
        else:
            self._scenes._items.insert(index, scene)
        self._notify_listeners("scenes")
        return scene

    def play(self) -> None:
        """Start playback"""
        self.is_playing = True

    def stop(self) -> None:
        """Stop playback"""
        self.is_playing = False

    def undo(self) -> None:
        """Undo last action"""
        pass

    def redo(self) -> None:
        """Redo last undone action"""
        pass

    def reset(self) -> None:
        """Reset song to initial state"""
        self._is_playing = False
        self._tempo = 120.0
        self._current_song_time = 0.0
        self._tracks.clear()
        self._scenes.clear()
        self._listeners.clear()
