"""
Live API session management.

Provides global access to the mock Ableton Live song instance.
"""

from typing import Optional

from .song import Song
from .browser import Browser

_song_instance: Optional[Song] = None
_browser_instance: Optional[Browser] = None


def get_song() -> Song:
    """Get or create the global song instance."""
    global _song_instance
    if _song_instance is None:
        _song_instance = Song()
    return _song_instance


def get_browser() -> Browser:
    """Get or create the global browser instance."""
    global _browser_instance
    if _browser_instance is None:
        _browser_instance = Browser()
    return _browser_instance


def reset_session() -> None:
    """Reset the global song and browser instances."""
    global _song_instance, _browser_instance
    if _song_instance:
        _song_instance.reset()
    if _browser_instance:
        _browser_instance = Browser()


def create_new_session() -> Song:
    """Create a completely new song session, replacing the global one."""
    global _song_instance
    _song_instance = Song()
    return _song_instance
