"""
Tests for the live.Clip class.
"""

import pytest
from live import Clip, Note


@pytest.fixture
def clip():
    """Create a fresh clip instance for each test."""
    return Clip("Test Clip")


def test_clip_creation(clip):
    """Test that a clip is created with default values."""
    assert clip.name == "Test Clip"
    assert clip.is_midi_clip is True
    assert clip.is_audio_clip is False
    assert clip.loop_start == 0.0
    assert clip.loop_end == 4.0
    assert clip.start_marker == 0.0
    assert clip.end_marker == 4.0
    assert len(clip.notes) == 0


def test_add_note(clip):
    """Test adding notes to a MIDI clip."""
    clip.add_note(60, 0.0, 0.5, 100)
    assert len(clip.notes) == 1

    clip.add_note(64, 0.5, 0.5, 100)
    assert len(clip.notes) == 2

    notes = clip.get_notes()
    assert notes[0].pitch == 60
    assert notes[1].pitch == 64


def test_remove_note(clip):
    """Test removing notes from a clip."""
    note = Note(60, 0.0, 0.5, 100)
    clip.notes.append(note)
    assert len(clip.notes) == 1

    clip.remove_note(note)
    assert len(clip.notes) == 0


def test_clip_loop_markers(clip):
    """Test setting clip loop and markers."""
    clip.loop_start = 1.0
    clip.loop_end = 5.0
    assert clip.loop_start == 1.0
    assert clip.loop_end == 5.0

    clip.start_marker = 0.5
    clip.end_marker = 4.5
    assert clip.start_marker == 0.5
    assert clip.end_marker == 4.5


def test_clip_listener(clip):
    """Test that listeners are notified of changes."""
    callback_calls = []

    def callback():
        callback_calls.append(True)

    clip.add_listener(callback)
    clip._notify_listeners()
    assert len(callback_calls) == 1

    clip.remove_listener(callback)
    clip._notify_listeners()
    assert len(callback_calls) == 1


def test_note_creation():
    """Test Note creation with various parameters."""
    note = Note(72, 1.0, 1.0, 80)
    assert note.pitch == 72
    assert note.start_time == 1.0
    assert note.duration == 1.0
    assert note.velocity == 80
