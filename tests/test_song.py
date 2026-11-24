"""
Tests for the live.Song class.
"""

import pytest
from live import Song, Track, Clip, Scene


@pytest.fixture
def song():
    """Create a fresh song instance for each test."""
    s = Song()
    yield s
    s.reset()


def test_song_creation(song):
    """Test that a song is created with default values."""
    assert song.is_playing is False
    assert song.tempo == 120.0
    assert len(song.tracks) == 0
    assert len(song.scenes) == 0


def test_song_play_stop(song):
    """Test play and stop functionality."""
    song.play()
    assert song.is_playing is True

    song.stop()
    assert song.is_playing is False


def test_song_tempo(song):
    """Test tempo setting."""
    song.set_tempo(140.0)
    assert song.tempo == 140.0

    song.set_tempo(90.0)
    assert song.tempo == 90.0


def test_create_track(song):
    """Test creating tracks."""
    track1 = song.create_track("Track 1")
    assert track1.name == "Track 1"
    assert len(song.tracks) == 1

    track2 = song.create_track("Track 2")
    assert len(song.tracks) == 2
    assert song.get_track(0) == track1
    assert song.get_track(1) == track2


def test_remove_track(song):
    """Test removing tracks."""
    track = song.create_track("Track 1")
    assert len(song.tracks) == 1

    song.remove_track(track)
    assert len(song.tracks) == 0


def test_create_scene(song):
    """Test creating scenes."""
    scene1 = song.create_scene("Scene 1")
    assert scene1.name == "Scene 1"
    assert len(song.scenes) == 1

    scene2 = song.create_scene("Scene 2")
    assert len(song.scenes) == 2
    assert song.get_scene(0) == scene1
    assert song.get_scene(1) == scene2


def test_undo_redo(song):
    """Test undo and redo functionality."""
    song.play()
    assert len(song._undo_stack) == 1

    song.undo()
    assert len(song._undo_stack) == 0
    assert len(song._redo_stack) == 1

    song.redo()
    assert len(song._undo_stack) == 1
    assert len(song._redo_stack) == 0


def test_call_logging(song):
    """Test that API calls are logged."""
    song.create_track("Track 1")
    song.play()
    song.set_tempo(140.0)

    call_log = song.get_call_log()
    assert len(call_log) == 3
    assert call_log[0][0] == "create_track"
    assert call_log[1][0] == "play"
    assert call_log[2][0] == "set_tempo"


def test_clear_call_log(song):
    """Test clearing the call log."""
    song.play()
    assert len(song.get_call_log()) == 1

    song.clear_call_log()
    assert len(song.get_call_log()) == 0


def test_song_reset(song):
    """Test resetting a song to initial state."""
    song.play()
    song.set_tempo(140.0)
    song.create_track("Track 1")

    song.reset()

    assert song.is_playing is False
    assert song.tempo == 120.0
    assert len(song.tracks) == 0
    assert len(song.get_call_log()) == 0


def test_song_listener(song):
    """Test that listeners are notified of changes."""
    callback_calls = []

    def callback():
        callback_calls.append(True)

    song.add_listener(callback)

    song.play()
    assert len(callback_calls) == 1

    song.set_tempo(140.0)
    assert len(callback_calls) == 2

    song.remove_listener(callback)
    song.stop()
    assert len(callback_calls) == 2
