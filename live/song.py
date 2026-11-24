from typing import List, Optional, Callable, Tuple

from .track import Track
from .scene import Scene


class Song:
    """Mock of an Ableton Live song (set)."""

    def __init__(self):
        self.is_playing: bool = False
        self.tempo: float = 120.0
        self.current_song_time: float = 0.0
        self.tracks: List[Track] = []
        self.scenes: List[Scene] = []
        self._undo_stack: List[str] = []
        self._redo_stack: List[str] = []
        self._listeners: List[Callable[[], None]] = []
        self._call_log: List[Tuple[str, tuple, dict]] = []

    def create_track(self, name: str = "Track") -> Track:
        """Create and add a new track to the song."""
        track_id = len(self.tracks)
        track = Track(name, track_id)
        self.tracks.append(track)
        self._log_call("create_track", (name,), {})
        return track

    def add_track(self, track: Track) -> None:
        """Add a track to the song."""
        self.tracks.append(track)
        self._log_call("add_track", (track.name,), {})

    def remove_track(self, track: Track) -> None:
        """Remove a track from the song."""
        if track in self.tracks:
            self.tracks.remove(track)
            self._log_call("remove_track", (track.name,), {})

    def get_track(self, index: int) -> Optional[Track]:
        """Get track by index."""
        if 0 <= index < len(self.tracks):
            return self.tracks[index]
        return None

    def create_scene(self, name: str = "Scene") -> Scene:
        """Create and add a new scene to the song."""
        scene_id = len(self.scenes)
        scene = Scene(name, scene_id)
        self.scenes.append(scene)
        self._log_call("create_scene", (name,), {})
        return scene

    def add_scene(self, scene: Scene) -> None:
        """Add a scene to the song."""
        self.scenes.append(scene)
        self._log_call("add_scene", (scene.name,), {})

    def get_scene(self, index: int) -> Optional[Scene]:
        """Get scene by index."""
        if 0 <= index < len(self.scenes):
            return self.scenes[index]
        return None

    def play(self) -> None:
        """Start playing the song."""
        self.is_playing = True
        self._undo_stack.append("play")
        self._redo_stack.clear()
        self._log_call("play", (), {})
        self._notify_listeners()

    def stop(self) -> None:
        """Stop playing the song."""
        self.is_playing = False
        self._undo_stack.append("stop")
        self._redo_stack.clear()
        self._log_call("stop", (), {})
        self._notify_listeners()

    def set_tempo(self, tempo: float) -> None:
        """Set the song tempo in BPM."""
        self.tempo = tempo
        self._undo_stack.append(f"set_tempo:{tempo}")
        self._redo_stack.clear()
        self._log_call("set_tempo", (tempo,), {})
        self._notify_listeners()

    def undo(self) -> None:
        """Undo the last action."""
        if self._undo_stack:
            action = self._undo_stack.pop()
            self._redo_stack.append(action)
            self._log_call("undo", (), {})
            self._notify_listeners()

    def redo(self) -> None:
        """Redo the last undone action."""
        if self._redo_stack:
            action = self._redo_stack.pop()
            self._undo_stack.append(action)
            self._log_call("redo", (), {})
            self._notify_listeners()

    def add_listener(self, callback: Callable[[], None]) -> None:
        """Register a callback for song changes."""
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

    def _log_call(self, method_name: str, args: tuple, kwargs: dict) -> None:
        """Log an API call for testing."""
        self._call_log.append((method_name, args, kwargs))

    def get_call_log(self) -> List[Tuple[str, tuple, dict]]:
        """Get the call log for test assertions."""
        return self._call_log.copy()

    def clear_call_log(self) -> None:
        """Clear the call log."""
        self._call_log.clear()

    def reset(self) -> None:
        """Reset the song to initial state."""
        self.is_playing = False
        self.tempo = 120.0
        self.current_song_time = 0.0
        self.tracks.clear()
        self.scenes.clear()
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._call_log.clear()
