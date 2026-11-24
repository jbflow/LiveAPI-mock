# LiveAPI-mock

A mock implementation of the Ableton Live API for offline testing and development.

## Overview

LiveAPI-mock provides Python implementations of core Ableton Live classes without requiring a running Ableton Live instance. This enables:

- **Offline testing** of mantra-remote-script functionality
- **CI/CD integration** without Live dependencies
- **Rapid prototyping** of Live control logic
- **Education** about the Live API structure

## Project Structure

```
LiveAPI-mock/
├── live/                  # Core mock classes
│   ├── __init__.py       # Public API
│   ├── song.py           # Song class
│   ├── track.py          # Track class
│   ├── clip.py           # Clip and Note classes
│   ├── parameter.py      # Parameter and Device classes
│   ├── scene.py          # Scene class
│   ├── browser.py        # Browser class
│   └── session.py        # Session management
├── tests/                 # Test suite
│   ├── conftest.py       # Pytest fixtures
│   ├── test_song.py
│   ├── test_track.py
│   ├── test_clip.py
│   ├── test_device.py
│   └── test_browser.py
├── Dockerfile            # Container configuration
├── requirements.txt      # Python dependencies
└── setup.py             # Package configuration
```

## Installation

### Local Development

```bash
pip install -e .
pip install -r requirements.txt
```

### Docker

```bash
docker build -t mantra-liveapi-mock .
docker run mantra-liveapi-mock
```

## Usage

### Basic API Usage

```python
from live import Song, Track, Clip

# Create a song
song = Song()

# Create tracks
track = song.create_track("Bass")
song.create_track("Drums")

# Add clips
clip = Clip("My Clip")
track.add_clip(clip)

# Add notes (MIDI)
clip.add_note(pitch=60, start_time=0.0, duration=0.5, velocity=100)

# Control playback
song.play()
song.set_tempo(140.0)

# Inspect state
print(f"Playing: {song.is_playing}")
print(f"Tempo: {song.tempo} BPM")
print(f"Tracks: {len(song.tracks)}")
```

### Using Session Management

```python
from live.session import get_song, reset_session

# Get the global song instance
song = get_song()

# After tests, reset state
reset_session()
```

### Call Logging for Test Assertions

```python
from live import Song

song = Song()
song.create_track("Track 1")
song.play()

# Inspect what API calls were made
calls = song.get_call_log()
assert calls[0] == ("create_track", ("Track 1",), {})
assert calls[1] == ("play", (), {})
```

### Using with pytest

```python
import pytest
from live import Song

def test_my_feature(mock_live_session):
    """Test that uses the mock Live API."""
    mock_live_session.create_track("Test Track")
    assert len(mock_live_session.tracks) == 1
```

## Supported Classes

### Song
Main entry point representing an Ableton Live set.

**Methods:**
- `play()` - Start playback
- `stop()` - Stop playback
- `set_tempo(bpm: float)` - Set tempo
- `create_track(name: str) -> Track` - Create a new track
- `create_scene(name: str) -> Scene` - Create a new scene
- `undo()` - Undo the last action
- `redo()` - Redo the last undone action
- `get_call_log() -> List` - Get all logged API calls
- `reset()` - Reset to initial state

**Properties:**
- `is_playing: bool`
- `tempo: float`
- `tracks: List[Track]`
- `scenes: List[Scene]`

### Track
Represents an Ableton Live track.

**Methods:**
- `add_device(device: Device)`
- `add_clip(clip: Clip)`
- `get_device(index: int) -> Optional[Device]`
- `get_clip(index: int) -> Optional[Clip]`

**Properties:**
- `name: str`
- `mute: bool`
- `solo: bool`
- `arm: bool`
- `devices: List[Device]`
- `clips: List[Clip]`

### Clip
Represents an Ableton Live clip.

**Methods:**
- `add_note(pitch, start_time, duration, velocity)`
- `remove_note(note: Note)`
- `get_notes() -> List[Note]`

**Properties:**
- `name: str`
- `notes: List[Note]`
- `loop_start: float`
- `loop_end: float`
- `start_marker: float`
- `end_marker: float`

### Device
Represents an Ableton Live device.

**Methods:**
- `add_parameter(parameter: Parameter)`
- `get_parameter(index: int) -> Optional[Parameter]`

**Properties:**
- `name: str`
- `parameters: List[Parameter]`
- `chains: List[Any]`

### Parameter
Represents a device parameter.

**Properties:**
- `name: str`
- `value: float`
- `min: float`
- `max: float`

**Methods:**
- `add_value_listener(callback)`
- `remove_value_listener(callback)`

### Browser
Device browser for loading devices.

**Methods:**
- `load_device(device_name: str, track=None) -> Device`
- `navigate(path: List[str])`
- `get_current_location() -> List[str]`

### Scene
Represents an Ableton Live scene.

**Properties:**
- `name: str`
- `clip_index: Optional[int]`

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=live --cov-report=html
```

## Integration with mantra-remote-script

LiveAPI-mock is designed to work seamlessly with mantra-remote-script testing:

```python
# In mantra-remote-script/tests/conftest.py
from live import Song

@pytest.fixture
def mock_live_session():
    song = Song()
    yield song
    song.reset()

# In mantra-remote-script/tests/test_something.py
def test_remote_script_feature(mock_live_session):
    # Use mock_live_session just like the real Live API
    track = mock_live_session.create_track("Test")
    assert track.name == "Test"
```

## Limitations

This is a mock implementation with the following limitations:

- **No real audio** - audio playback is not simulated
- **No MIDI routing** - MIDI connections are not modeled
- **Simplified state** - some internal state is simplified vs. real Live
- **No serialization** - songs cannot be saved/loaded (for now)
- **Limited device models** - devices are generic, not modeled after specific Live devices

For integration with real Live, use the official Ableton Live Control Surface API.

## Contributing

To extend LiveAPI-mock:

1. Add new methods/properties to the relevant mock class
2. Add type hints (Python 3.7+ compatible)
3. Add comprehensive tests
4. Update the README
5. Ensure call logging works for new methods

## License

Part of the Mantra project.
