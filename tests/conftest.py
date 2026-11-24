"""
Pytest configuration for LiveAPI-mock tests.
"""

import pytest
from live import Song


@pytest.fixture(scope="function")
def mock_live_session():
    """
    Pytest fixture that provides a fresh Song instance for testing.

    This fixture is used by mantra-remote-script tests to interact with
    the mock Ableton Live API without requiring an actual Live instance.
    """
    song = Song()
    yield song
    song.reset()


@pytest.fixture(scope="function")
def live_song():
    """Alias for mock_live_session for compatibility."""
    song = Song()
    yield song
    song.reset()
