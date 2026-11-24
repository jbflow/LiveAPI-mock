from typing import List, Optional, Callable, Any


class Note:
    """Mock of an Ableton Live note."""

    def __init__(
        self, pitch: int = 60, start_time: float = 0.0, duration: float = 0.5, velocity: int = 100
    ):
        self.pitch = pitch
        self.start_time = start_time
        self.duration = duration
        self.velocity = velocity


class Clip:
    """Mock of an Ableton Live clip."""

    def __init__(self, name: str = "Clip", clip_id: int = 0):
        self.name = name
        self._clip_id = clip_id
        self.notes: List[Note] = []
        self.loop_start: float = 0.0
        self.loop_end: float = 4.0
        self.start_marker: float = 0.0
        self.end_marker: float = 4.0
        self.is_audio_clip: bool = False
        self.is_midi_clip: bool = True
        self._listeners: List[Callable[[], None]] = []

    def add_note(
        self, pitch: int, start_time: float, duration: float, velocity: int = 100
    ) -> None:
        """Add a note to this MIDI clip."""
        if self.is_midi_clip:
            self.notes.append(Note(pitch, start_time, duration, velocity))

    def remove_note(self, note: Note) -> None:
        """Remove a note from this clip."""
        if note in self.notes:
            self.notes.remove(note)

    def get_notes(self) -> List[Note]:
        """Get all notes in this clip."""
        return self.notes.copy()

    def add_listener(self, callback: Callable[[], None]) -> None:
        """Register a callback for clip changes."""
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
