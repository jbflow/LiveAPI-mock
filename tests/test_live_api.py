"""Tests for the Live API mock"""

import pytest
from live import Song, Track, Clip, Device, DeviceParameter, Scene, ClipSlot


@pytest.fixture
def song():
    """Provide a fresh Song instance for each test"""
    s = Song()
    yield s
    s.reset()


class TestSongBasics:
    """Test Song class basic functionality"""

    def test_song_creation(self, song):
        """Test Song is created with default state"""
        assert song.is_playing is False
        assert song.tempo == 120.0
        assert len(song.tracks) == 0
        assert len(song.scenes) == 0

    def test_song_play_stop(self, song):
        """Test play/stop functionality"""
        song.play()
        assert song.is_playing is True

        song.stop()
        assert song.is_playing is False

    def test_song_tempo(self, song):
        """Test tempo property"""
        song.tempo = 140.0
        assert song.tempo == 140.0

    def test_song_tempo_listener(self, song):
        """Test tempo listener"""
        calls = []
        def on_tempo():
            calls.append(song.tempo)

        song.add_tempo_listener(on_tempo)
        song.tempo = 140.0
        assert len(calls) == 1
        assert calls[0] == 140.0

    def test_song_view_detail_clip(self, song):
        """Test Song.View.detail_clip property"""
        clip = Clip("Test Clip")
        song.view.detail_clip = clip
        assert song.view.detail_clip == clip

    def test_song_view_follow_song(self, song):
        """Test Song.View.follow_song property"""
        song.view.follow_song = False
        assert song.view.follow_song is False

        song.view.follow_song = True
        assert song.view.follow_song is True


class TestTrackCreation:
    """Test Track creation and management"""

    def test_create_track(self, song):
        """Test creating a track"""
        track = song.create_track()
        assert track.name == "Track 0"
        assert len(song.tracks) == 1
        assert song.tracks[0] == track

    def test_track_listener(self, song):
        """Test track listener"""
        calls = []
        def on_tracks():
            calls.append(len(song.tracks))

        song.add_tracks_listener(on_tracks)
        song.create_track()
        assert len(calls) == 1
        assert calls[0] == 1


class TestTrackProperties:
    """Test Track properties and state"""

    def test_track_mute_solo_arm(self, song):
        """Test track mute, solo, arm"""
        track = song.create_track()

        track.mute = True
        assert track.mute is True

        track.solo = True
        assert track.solo is True

        track.arm = True
        assert track.arm is True

    def test_track_property_listeners(self, song):
        """Test track property listeners"""
        track = song.create_track()

        mute_calls = []
        def on_mute():
            mute_calls.append(track.mute)

        track.add_mute_listener(on_mute)
        track.mute = True
        assert len(mute_calls) == 1
        assert mute_calls[0] is True

    def test_track_view_collapsed(self, song):
        """Test track view is_collapsed property"""
        track = song.create_track()

        track.view.is_collapsed = True
        assert track.view.is_collapsed is True

    def test_track_view_selected_device(self, song):
        """Test track view selected_device"""
        track = song.create_track()
        device = Device("Operator")

        track.view.selected_device = device
        assert track.view.selected_device == device


class TestDeviceManagement:
    """Test device insertion and management"""

    def test_insert_device(self, song):
        """Test inserting device into track"""
        track = song.create_track()
        device = Device("Operator")

        track.insert_device(device)
        assert len(track.devices) == 1
        assert track.devices[0] == device

    def test_device_name_listener(self, song):
        """Test device name listener"""
        track = song.create_track()
        device = Device("Operator")
        track.insert_device(device)

        calls = []
        def on_name():
            calls.append(device.name)

        device.add_name_listener(on_name)
        device.name = "New Name"
        assert len(calls) == 1
        assert calls[0] == "New Name"

    def test_device_is_active(self, song):
        """Test device active state"""
        track = song.create_track()
        device = Device("Operator")
        track.insert_device(device)

        assert device.is_active is True
        device.is_active = False
        assert device.is_active is False

    def test_device_view_collapsed(self, song):
        """Test device view is_collapsed"""
        track = song.create_track()
        device = Device("Operator")
        track.insert_device(device)

        device.view.is_collapsed = True
        assert device.view.is_collapsed is True


class TestDeviceParameters:
    """Test device parameters"""

    def test_device_parameter_creation(self):
        """Test creating a device parameter"""
        param = DeviceParameter("Volume", min_value=0.0, max_value=1.0, default_value=0.5)
        assert param.name == "Volume"
        assert param.value == 0.5
        assert param.min == 0.0
        assert param.max == 1.0

    def test_device_parameter_value_listener(self):
        """Test parameter value listener"""
        param = DeviceParameter("Volume")
        calls = []

        def on_value():
            calls.append(param.value)

        param.add_value_listener(on_value)
        param.value = 0.7
        assert len(calls) == 1
        assert calls[0] == 0.7

    def test_device_parameter_clamping(self):
        """Test parameter value clamping to min/max"""
        param = DeviceParameter("Volume", min_value=0.0, max_value=1.0)

        param.value = 1.5  # Above max
        assert param.value == 1.0

        param.value = -0.5  # Below min
        assert param.value == 0.0


class TestClips:
    """Test Clip functionality"""

    def test_clip_creation(self):
        """Test creating a clip"""
        clip = Clip("Test Clip")
        assert clip.name == "Test Clip"
        assert clip.is_midi_clip is True
        assert clip.is_audio_clip is False

    def test_clip_markers(self):
        """Test clip loop and start/end markers"""
        clip = Clip("Test")

        clip.start_marker = 1.0
        clip.end_marker = 5.0
        assert clip.start_marker == 1.0
        assert clip.end_marker == 5.0

        clip.loop_start = 1.0
        clip.loop_end = 4.0
        assert clip.loop_start == 1.0
        assert clip.loop_end == 4.0

    def test_clip_name_listener(self):
        """Test clip name listener"""
        clip = Clip("Test")
        calls = []

        def on_name():
            calls.append(clip.name)

        clip.add_name_listener(on_name)
        clip.name = "New Name"
        assert len(calls) == 1
        assert calls[0] == "New Name"


class TestScenes:
    """Test Scene functionality"""

    def test_create_scene(self, song):
        """Test creating a scene"""
        scene = song.create_scene()
        assert scene.name == "Scene 0"
        assert len(song.scenes) == 1

    def test_scene_tempo(self, song):
        """Test scene tempo"""
        scene = song.create_scene()

        scene.tempo = 140.0
        scene.tempo_enabled = True
        assert scene.tempo == 140.0
        assert scene.tempo_enabled is True

    def test_scene_listener(self, song):
        """Test scene name listener"""
        scene = song.create_scene()
        calls = []

        def on_name():
            calls.append(scene.name)

        scene.add_name_listener(on_name)
        scene.name = "Verse"
        assert len(calls) == 1
        assert calls[0] == "Verse"


class TestIntegration:
    """Integration tests combining multiple features"""

    def test_track_with_device_and_parameters(self, song):
        """Test track with device containing parameters"""
        track = song.create_track()
        device = Device("Wavetable")
        track.insert_device(device)

        # Add parameter to device
        param = DeviceParameter("Oscillator Volume")
        device.parameters.append(param)

        assert len(device.parameters) == 1
        assert device.parameters[0].name == "Oscillator Volume"

    def test_song_with_multiple_tracks_and_scenes(self, song):
        """Test song with multiple tracks and scenes"""
        for i in range(3):
            song.create_track()

        for i in range(4):
            song.create_scene()

        assert len(song.tracks) == 3
        assert len(song.scenes) == 4

        # Each scene should have clip slots for each track
        assert len(song.scenes[0].clip_slots) == 3

    def test_listener_pattern_comprehensive(self, song):
        """Test comprehensive listener pattern"""
        track = song.create_track()

        # Test add, has, and remove listeners
        def callback():
            pass

        assert track.mute_has_listener(callback) is False
        track.add_mute_listener(callback)
        assert track.mute_has_listener(callback) is True
        track.remove_mute_listener(callback)
        assert track.mute_has_listener(callback) is False
