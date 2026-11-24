import pytest

import Live
from Live.Clip import MidiNoteSpecification as Note


@pytest.fixture
def clip(song):
    song.create_midi_track()
    song.create_audio_track()
    song.create_scene(-1)
    return song.tracks[0].clip_slots[0].create_clip(4.0)


def test_new_clip_defaults(clip):
    assert clip.is_midi_clip and not clip.is_audio_clip
    assert (clip.loop_start, clip.loop_end, clip.length) == (0.0, 4.0, 4.0)
    assert (clip.start_marker, clip.end_marker) == (0.0, 4.0)
    assert clip.looping and clip.name == ""
    assert clip.canonical_parent.canonical_parent is not None


def test_clip_slot_lifecycle(song):
    track = song.create_midi_track()
    song.create_scene(-1)
    slot = track.clip_slots[0]
    seen = []
    slot.add_has_clip_listener(lambda: seen.append(slot.has_clip))
    assert not slot.has_clip and slot.clip is None
    clip = slot.create_clip(2.0)
    assert slot.clip is clip and slot.has_clip
    with pytest.raises(RuntimeError):
        slot.create_clip(2.0)
    slot.delete_clip()
    assert slot.clip is None and seen == [True, False]


def test_clip_properties_and_listeners(clip):
    seen = []
    clip.add_loop_end_listener(lambda: seen.append(clip.loop_end))
    clip.loop_end = 8.0
    clip.name = "Hook"
    clip.start_marker = 1.0
    assert clip.length == 8.0 and clip.name == "Hook" and clip.start_marker == 1.0
    assert seen == [8.0]


def test_fire_and_stop_clip(song, clip):
    clip.fire()
    assert clip.is_playing and song.is_playing
    clip.stop()
    assert not clip.is_playing


def test_add_and_read_notes(clip):
    ids = clip.add_new_notes([Note(60, 0.0, 1.0), Note(64, 1.0, 0.5, velocity=80.0), Note(67, 2.0, 1.0)])
    assert len(ids) == 3 and len(set(ids)) == 3
    notes = clip.get_all_notes_extended()
    assert [n.pitch for n in notes] == [60, 64, 67]
    assert notes[1].velocity == 80.0 and notes[0].velocity == 100.0
    assert notes[0].note_id == ids[0] and notes[0].probability == 1.0 and not notes[0].mute


def test_notes_listener(clip):
    seen = []
    clip.add_notes_listener(lambda: seen.append(1))
    clip.add_new_notes([Note(60, 0.0, 1.0)])
    clip.remove_notes_extended(0, 128, 0.0, 4.0)
    assert seen == [1, 1]


def test_get_notes_extended_filters_by_start_and_pitch(clip):
    clip.add_new_notes([Note(60, 0.0, 1.0), Note(72, 0.5, 1.0), Note(60, 3.0, 1.0)])
    assert [n.pitch for n in clip.get_notes_extended(60, 1, 0.0, 4.0)] == [60, 60]
    assert [n.start_time for n in clip.get_notes_extended(0, 128, 0.0, 1.0)] == [0.0, 0.5]


def test_returned_notes_are_snapshots_until_applied(clip):
    clip.add_new_notes([Note(60, 0.0, 1.0)])
    note = clip.get_all_notes_extended()[0]
    note.pitch = 62
    assert clip.get_all_notes_extended()[0].pitch == 60
    clip.apply_note_modifications(Live.Clip.MidiNoteVector())
    batch = Live.Clip.MidiNoteVector()
    batch.append(note)
    clip.apply_note_modifications(batch)
    assert clip.get_all_notes_extended()[0].pitch == 62


def test_remove_notes(clip):
    ids = clip.add_new_notes([Note(60, 0.0, 1.0), Note(62, 1.0, 1.0), Note(64, 2.0, 1.0)])
    clip.remove_notes_by_id([ids[0]])
    clip.remove_notes_extended(64, 1, 0.0, 4.0)
    assert [n.pitch for n in clip.get_all_notes_extended()] == [62]


def test_selected_notes(clip):
    clip.add_new_notes([Note(60, 0.0, 1.0)])
    assert len(clip.get_selected_notes_extended()) == 0
    clip.select_all_notes()
    assert len(clip.get_selected_notes_extended()) == 1
    clip.deselect_all_notes()
    assert len(clip.get_selected_notes_extended()) == 0


def test_legacy_note_api(clip):
    clip.set_notes(((60, 0.0, 1.0, 100.0, False), (64, 1.0, 1.0, 90.0, True)))
    assert clip.get_notes(0.0, 0, 4.0, 128) == ((60, 0.0, 1.0, 100.0, False), (64, 1.0, 1.0, 90.0, True))


def test_audio_clip_rejects_notes(song):
    song.create_audio_track()
    song.create_scene(-1)
    audio = song.tracks[0].clip_slots[0].create_clip(4.0)
    assert audio.is_audio_clip
    with pytest.raises(RuntimeError):
        audio.add_new_notes([Note(60, 0.0, 1.0)])
