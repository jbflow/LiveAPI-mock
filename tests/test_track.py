"""
Tests for the live.Track class.
"""

import pytest
from live import Track, Clip, Device, Parameter


@pytest.fixture
def track():
    """Create a fresh track instance for each test."""
    return Track("Test Track")


def test_track_creation(track):
    """Test that a track is created with default values."""
    assert track.name == "Test Track"
    assert track.mute is False
    assert track.solo is False
    assert track.arm is False
    assert len(track.devices) == 0
    assert len(track.clips) == 0


def test_track_mute_solo_arm(track):
    """Test muting, soloing, and arming."""
    track.mute = True
    assert track.mute is True

    track.solo = True
    assert track.solo is True

    track.arm = True
    assert track.arm is True


def test_add_device(track):
    """Test adding devices to a track."""
    device1 = Device("Operator")
    track.add_device(device1)
    assert len(track.devices) == 1
    assert track.get_device(0) == device1

    device2 = Device("EQ-Eight")
    track.add_device(device2)
    assert len(track.devices) == 2
    assert track.get_device(1) == device2


def test_remove_device(track):
    """Test removing devices from a track."""
    device = Device("Operator")
    track.add_device(device)
    assert len(track.devices) == 1

    track.remove_device(device)
    assert len(track.devices) == 0


def test_add_clip(track):
    """Test adding clips to a track."""
    clip1 = Clip("Clip 1")
    track.add_clip(clip1)
    assert len(track.clips) == 1
    assert track.get_clip(0) == clip1

    clip2 = Clip("Clip 2")
    track.add_clip(clip2)
    assert len(track.clips) == 2
    assert track.get_clip(1) == clip2


def test_remove_clip(track):
    """Test removing clips from a track."""
    clip = Clip("Clip 1")
    track.add_clip(clip)
    assert len(track.clips) == 1

    track.remove_clip(clip)
    assert len(track.clips) == 0


def test_track_listener(track):
    """Test that listeners are notified of changes."""
    callback_calls = []

    def callback():
        callback_calls.append(True)

    track.add_listener(callback)

    track.mute = True
    track._notify_listeners()
    assert len(callback_calls) == 1

    track.remove_listener(callback)
    track.solo = True
    track._notify_listeners()
    assert len(callback_calls) == 1
