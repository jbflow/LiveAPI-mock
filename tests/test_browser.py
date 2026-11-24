"""
Tests for the live.Browser class.
"""

import pytest
from live import Browser


@pytest.fixture
def browser():
    """Create a fresh browser instance for each test."""
    return Browser()


def test_browser_creation(browser):
    """Test that a browser is created with default values."""
    assert browser.get_current_location() == []


def test_browser_navigate(browser):
    """Test navigating the browser."""
    browser.navigate(["Instruments", "Wavetable"])
    assert browser.get_current_location() == ["Instruments", "Wavetable"]

    browser.navigate(["Instruments", "Operator"])
    assert browser.get_current_location() == ["Instruments", "Operator"]


def test_browser_load_device(browser):
    """Test loading a device from the browser."""
    device = browser.load_device("Operator")

    assert device is not None
    assert device.name == "Operator"
    assert len(device.parameters) > 0


def test_browser_load_device_into_track(browser):
    """Test loading a device into a track."""
    from live import Track

    track = Track("Test Track")
    device = browser.load_device("Wavetable", track)

    assert device is not None
    assert device.name == "Wavetable"
    assert device in track.devices
    assert len(track.devices) == 1


def test_browser_listener(browser):
    """Test that browser listeners are notified."""
    callback_calls = []

    def callback():
        callback_calls.append(True)

    browser.add_listener(callback)
    browser.navigate(["Instruments", "Operator"])
    assert len(callback_calls) == 1

    browser.remove_listener(callback)
    browser.navigate(["Instruments", "Wavetable"])
    assert len(callback_calls) == 1
