"""
Ableton Live API Mock

Provides mock implementations of core Ableton Live classes for offline testing
and development without requiring an actual Ableton Live instance.
"""

from .parameter import Parameter, Device
from .clip import Clip, Note
from .track import Track
from .scene import Scene
from .song import Song
from .browser import Browser

__all__ = [
    "Parameter",
    "Device",
    "Clip",
    "Note",
    "Track",
    "Scene",
    "Song",
    "Browser",
]

__version__ = "0.1.0"
