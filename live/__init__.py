"""Ableton Live API Mock - Based on actual Live Object Model

A comprehensive mock of the Ableton Live Python API for offline testing
and development without requiring a running Live instance.

This mock follows the actual Ableton Live Object Model structure with:
- Proper @property decorators and setters
- Full listener pattern on all properties
- Nested View classes where applicable
- Type hints matching the real API

Usage:
    from live import Song, Track, Clip, Device

    song = Song()
    track = song.create_track()
    track.mute = True

    clip = Clip("My Clip")
    track.clip_slots[0].clip = clip
"""

from .base import LomObject, Vector, StringVector, IntVector, IntU64Vector
from .device_parameter import DeviceParameter, AutomationState
from .device import Device
from .clip import Clip
from .clip_slot import ClipSlot
from .scene import Scene
from .track import Track, DeviceContainer
from .song import Song

__all__ = [
    "LomObject",
    "Vector",
    "StringVector",
    "IntVector",
    "IntU64Vector",
    "DeviceParameter",
    "AutomationState",
    "Device",
    "Clip",
    "ClipSlot",
    "Scene",
    "Track",
    "DeviceContainer",
    "Song",
]

__version__ = "0.2.0"
