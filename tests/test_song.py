import pytest

import Live


def test_application_and_document_are_singletons(app, song):
    assert Live.Application.get_application() is app
    assert app.get_document() is song
    assert app.get_major_version() == 12


def test_song_defaults_and_transport(song):
    assert song.tempo == 120.0 and song.signature_numerator == 4
    assert not song.is_playing
    song.start_playing()
    assert song.is_playing
    song.stop_playing()
    assert not song.is_playing
    song.current_song_time = 8.0
    song.stop_playing()
    assert song.current_song_time == 0.0


def test_is_playing_listener(song):
    seen = []
    song.add_is_playing_listener(lambda: seen.append(song.is_playing))
    song.start_playing()
    song.stop_playing()
    assert seen == [True, False]


def test_create_tracks_scenes_and_clip_slot_grid(song):
    midi = song.create_midi_track()
    audio = song.create_audio_track()
    song.create_scene(-1)
    song.create_scene(-1)
    assert [t.name for t in song.tracks] == ["1 MIDI", "2 Audio"]
    assert midi.has_midi_input and not audio.has_midi_input
    assert len(song.scenes) == 2
    assert all(len(t.clip_slots) == 2 for t in song.tracks)
    # scenes and tracks share the same ClipSlot objects
    assert song.scenes[1].clip_slots[0] is midi.clip_slots[1]
    assert song.scenes[0].clip_slots[1] is audio.clip_slots[0]


def test_new_track_after_scenes_gets_slots(song):
    song.create_scene(-1)
    track = song.create_midi_track()
    assert len(track.clip_slots) == 1
    assert song.scenes[0].clip_slots[0] is track.clip_slots[0]


def test_insert_track_in_middle_keeps_grid_aligned(song):
    a = song.create_midi_track()
    c = song.create_midi_track()
    song.create_scene(-1)
    b = song.create_midi_track(1)
    assert list(song.tracks) == [a, b, c]
    assert list(song.scenes[0].clip_slots) == [t.clip_slots[0] for t in (a, b, c)]


def test_tracks_listener_and_visible_tracks(song):
    seen = []
    song.add_tracks_listener(lambda: seen.append(len(song.tracks)))
    song.create_midi_track()
    song.create_audio_track()
    assert seen == [1, 2]
    assert list(song.visible_tracks) == list(song.tracks)


def test_delete_track_and_scene_keep_grid_consistent(song):
    a = song.create_midi_track()
    b = song.create_midi_track()
    song.create_scene(-1)
    song.create_scene(-1)
    song.delete_track(0)
    assert list(song.tracks) == [b]
    assert all(len(s.clip_slots) == 1 for s in song.scenes)
    song.delete_scene(0)
    assert len(song.scenes) == 1 and len(b.clip_slots) == 1
    assert song.view.selected_track is b
    assert a not in list(song.tracks)


def test_selection_defaults_to_first_created(song):
    first = song.create_midi_track()
    song.create_midi_track()
    scene = song.create_scene(-1)
    assert song.view.selected_track is first
    assert song.view.selected_scene is scene


def test_return_tracks_have_no_clip_slots(song):
    song.create_scene(-1)
    ret = song.create_return_track()
    assert ret.name == "A-Return"
    assert len(ret.clip_slots) == 0
    assert len(song.scenes[0].clip_slots) == 0
    assert list(song.return_tracks) == [ret]


def test_track_state_and_listeners(song):
    track = song.create_midi_track()
    seen = []
    track.add_mute_listener(lambda: seen.append(track.mute))
    track.mute = True
    track.solo = True
    track.arm = True
    track.name = "Bass"
    assert (track.mute, track.solo, track.arm, track.name) == (True, True, True, "Bass")
    assert seen == [True]


def test_duplicate_track_copies_clips_and_devices(song):
    track = song.create_midi_track()
    song.create_scene(-1)
    clip = track.clip_slots[0].create_clip(4.0)
    clip.add_new_notes([Live.Clip.MidiNoteSpecification(60, 0.0, 1.0)])
    track.insert_device("Operator")
    song.duplicate_track(0)
    copy = song.tracks[1]
    assert copy.clip_slots[0].has_clip and copy.clip_slots[0].clip is not clip
    assert len(copy.clip_slots[0].clip.get_all_notes_extended()) == 1
    assert [d.name for d in copy.devices] == ["Operator"]


def test_duplicate_scene_copies_clips(song):
    track = song.create_midi_track()
    song.create_scene(-1)
    track.clip_slots[0].create_clip(2.0)
    song.duplicate_scene(0)
    assert len(song.scenes) == 2 and track.clip_slots[1].has_clip


def test_fire_scene_plays_its_clips_and_the_transport(song):
    t1, t2 = song.create_midi_track(), song.create_midi_track()
    song.create_scene(-1)
    song.create_scene(-1)
    t1.clip_slots[0].create_clip(4.0)
    t1.clip_slots[1].create_clip(4.0)
    t2.clip_slots[1].create_clip(4.0)
    song.scenes[0].fire()
    assert t1.clip_slots[0].is_playing and song.is_playing
    song.scenes[1].fire()
    assert not t1.clip_slots[0].is_playing
    assert t1.clip_slots[1].is_playing and t2.clip_slots[1].is_playing
    song.stop_all_clips()
    assert not t1.clip_slots[1].is_playing


def test_master_track(song):
    assert song.master_track.name == "Master"
    assert song.master_track.canonical_parent is song


def test_mixer_device_parameters(song):
    mixer = song.create_midi_track().mixer_device
    assert mixer.volume.name == "Volume" and mixer.volume.value == 0.85
    assert mixer.panning.min == -1.0 and mixer.panning.max == 1.0
    mixer.volume.value = 0.5
    assert mixer.volume.value == 0.5
