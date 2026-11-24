"""Stateful behaviour for the generated Live mock.

Everything here is registered against real Live member names (``"<Module>.<Class>.<member>"``).
Members without an entry behave generically: properties hold what you set, methods are
logged in ``Live.call_log`` and return a type-appropriate default.
"""
from __future__ import annotations

from . import (
    Application as application_mod,
    Base,
    Browser as browser_mod,
    Clip as clip_mod,
    ClipSlot as clip_slot_mod,
    Device as device_mod,
    DeviceParameter as parameter_mod,
    MixerDevice as mixer_mod,
    Scene as scene_mod,
    Song as song_mod,
    Track as track_mod,
)
from . import _runtime
from ._runtime import DEFAULTS, behavior, getter, on_reset

_session = {}
_note_ids = [0]


@on_reset
def _reset_session():
    _session.clear()
    _note_ids[0] = 0


def _vector(items=()):
    return Base.Vector(items)


# ---------------------------------------------------------------- application

@behavior("Application.get_application")
def get_application():
    if "app" not in _session:
        _session["app"] = application_mod.Application()
    return _session["app"]


@behavior("Application.Application.get_document")
def get_document(app):
    if "song" not in _session:
        _session["song"] = song_mod.Song()
    return _session["song"]


behavior("Application.Application.get_major_version")(lambda app: 12)
behavior("Application.Application.get_minor_version")(lambda app: 3)
behavior("Application.Application.get_bugfix_version")(lambda app: 6)


# ------------------------------------------------------------------ parameters

def make_parameter(name, minimum=0.0, maximum=1.0, value=None, quantized=False, parent=None):
    param = parameter_mod.DeviceParameter(
        name=name, original_name=name, min=minimum, max=maximum,
        default_value=minimum if value is None else value,
        value=minimum if value is None else value,
        is_quantized=quantized, is_enabled=True,
    )
    param._parent = parent
    return param


DEFAULTS["DeviceParameter.DeviceParameter.max"] = 1.0
DEFAULTS["DeviceParameter.DeviceParameter.is_enabled"] = True
DEFAULTS["MixerDevice.MixerDevice.volume"] = lambda m: make_parameter("Volume", 0.0, 1.0, 0.85, parent=m)
DEFAULTS["MixerDevice.MixerDevice.panning"] = lambda m: make_parameter("Pan", -1.0, 1.0, 0.0, parent=m)
DEFAULTS["MixerDevice.MixerDevice.track_activator"] = lambda m: make_parameter(
    "Track Activator", 0.0, 1.0, 1.0, quantized=True, parent=m)


# --------------------------------------------------------------------- devices

_DEVICE_TYPES = {"instrument": 1, "audio_effect": 2, "midi_effect": 4}


def make_device(name, kind="instrument"):
    device = device_mod.Device(
        name=name,
        class_name=name.replace(" ", ""),
        class_display_name=name,
        type=device_mod.DeviceType(_DEVICE_TYPES.get(kind, 0)),
        is_active=True,
    )
    device._update("parameters", device_mod.ATimeableValueVector([make_parameter("Device On", 0.0, 1.0, 1.0, quantized=True, parent=device)]))
    return device


def _insert_device(track, device, index):
    devices = track.devices
    if index is None or index < 0 or index > len(devices):
        devices._append(device)
    else:
        devices._insert(index, device)
    device._parent = track
    track._notify("devices")
    return device


@behavior("Track.Track.insert_device")
def insert_device(track, device_name, device_index=-1):
    return _insert_device(track, make_device(device_name), device_index)


@behavior("Track.Track.delete_device")
def delete_device(track, index):
    track.devices._items.pop(index)
    track._notify("devices")


@behavior("Track.Track.duplicate_device")
def duplicate_device(track, index):
    original = track.devices[index]
    clone = make_device(original.name)
    _insert_device(track, clone, index + 1)


# ----------------------------------------------------------------- clips/slots

def _new_clip(slot, length, midi):
    clip = clip_mod.Clip(
        name="", is_midi_clip=midi, is_audio_clip=not midi, looping=True,
        loop_start=0.0, loop_end=float(length), start_marker=0.0, end_marker=float(length),
        start_time=0.0, end_time=float(length), is_playing=False, is_triggered=False,
    )
    clip._update("notes_store", [])
    clip._parent = slot
    return clip


@getter("Clip.Clip.length")
def clip_length(clip):
    return clip.loop_end - clip.loop_start


@getter("ClipSlot.ClipSlot.has_clip")
def slot_has_clip(slot):
    return slot._state.get("clip") is not None


@getter("ClipSlot.ClipSlot.is_playing")
def slot_is_playing(slot):
    clip = slot._state.get("clip")
    return bool(clip is not None and clip._state.get("is_playing"))


DEFAULTS["ClipSlot.ClipSlot.clip"] = None
DEFAULTS["Clip.Clip.looping"] = True
DEFAULTS["Clip.Clip.is_midi_clip"] = True


def _set_clip(slot, clip):
    slot._state["clip"] = clip
    slot._notify("clip")
    slot._notify("has_clip")


@behavior("ClipSlot.ClipSlot.create_clip")
def create_clip(slot, length):
    if slot.has_clip:
        raise RuntimeError("Clip slot already has a clip")
    track = slot.canonical_parent
    midi = bool(track is None or track._state.get("has_midi_input", True))
    clip = _new_clip(slot, length, midi)
    _set_clip(slot, clip)
    return clip


@behavior("ClipSlot.ClipSlot.delete_clip")
def delete_clip_from_slot(slot):
    if slot.has_clip:
        _set_clip(slot, None)


def _song_of(track):
    return track.canonical_parent if track is not None else None


@behavior("ClipSlot.ClipSlot.fire")
def fire_slot(slot, *args, **kwargs):
    if not slot.has_clip:
        return
    track = slot.canonical_parent
    for other in track.clip_slots:
        clip = other._state.get("clip")
        if clip is not None and other is not slot:
            clip._update("is_playing", False)
    slot.clip._update("is_playing", True)
    song = _song_of(track)
    if song is not None:
        song._update("is_playing", True)


@behavior("ClipSlot.ClipSlot.stop")
def stop_slot(slot):
    if slot.has_clip:
        slot.clip._update("is_playing", False)


@behavior("Clip.Clip.fire")
def fire_clip(clip):
    fire_slot(clip.canonical_parent)


@behavior("Clip.Clip.stop")
def stop_clip(clip):
    stop_slot(clip.canonical_parent)


@behavior("Track.Track.stop_all_clips")
def stop_all_track_clips(track, *args, **kwargs):
    for slot in track.clip_slots:
        stop_slot(slot)


# ----------------------------------------------------------------------- notes

_NOTE_FIELDS = ("pitch", "start_time", "duration", "velocity", "mute", "probability",
                "velocity_deviation", "release_velocity")


def _notes(clip):
    return clip._state.setdefault("notes_store", [])


def _snapshot(note):
    return clip_mod.MidiNote(**note._state)


def _in_range(note, from_pitch, pitch_span, from_time, time_span):
    st = note._state
    return (from_pitch <= st["pitch"] < from_pitch + pitch_span
            and from_time <= st["start_time"] < from_time + time_span)


def _note_vector(notes):
    vector = clip_mod.MidiNoteVector()
    vector._extend(_snapshot(n) for n in sorted(notes, key=lambda n: (n._state["start_time"], n._state["pitch"])))
    return vector


@behavior("Clip.Clip.add_new_notes")
def add_new_notes(clip, specifications):
    if not clip.is_midi_clip:
        raise RuntimeError("Can't add notes to an audio clip")
    ids = Base.IntU64Vector()
    for spec in specifications:
        _note_ids[0] += 1
        state = {f: spec._state[f] for f in _NOTE_FIELDS}
        note = clip_mod.MidiNote(note_id=_note_ids[0], **state)
        _notes(clip).append(note)
        ids._append(_note_ids[0])
    clip._notify("notes")
    return ids


@behavior("Clip.Clip.get_all_notes_extended")
def get_all_notes_extended(clip):
    return _note_vector(_notes(clip))


@behavior("Clip.Clip.get_notes_extended")
def get_notes_extended(clip, from_pitch, pitch_span, from_time, time_span):
    return _note_vector([n for n in _notes(clip) if _in_range(n, from_pitch, pitch_span, from_time, time_span)])


@behavior("Clip.Clip.get_selected_notes_extended")
def get_selected_notes_extended(clip):
    selected = clip._state.get("selected_ids", set())
    return _note_vector([n for n in _notes(clip) if n._state["note_id"] in selected])


@behavior("Clip.Clip.select_all_notes")
def select_all_notes(clip):
    clip._state["selected_ids"] = {n._state["note_id"] for n in _notes(clip)}


@behavior("Clip.Clip.deselect_all_notes")
def deselect_all_notes(clip):
    clip._state["selected_ids"] = set()


@behavior("Clip.Clip.remove_notes_extended")
def remove_notes_extended(clip, from_pitch, pitch_span, from_time, time_span):
    keep = [n for n in _notes(clip) if not _in_range(n, from_pitch, pitch_span, from_time, time_span)]
    if len(keep) != len(_notes(clip)):
        clip._state["notes_store"] = keep
        clip._notify("notes")


@behavior("Clip.Clip.remove_notes_by_id")
def remove_notes_by_id(clip, note_ids):
    ids = set(note_ids)
    keep = [n for n in _notes(clip) if n._state["note_id"] not in ids]
    if len(keep) != len(_notes(clip)):
        clip._state["notes_store"] = keep
        clip._notify("notes")


@behavior("Clip.Clip.apply_note_modifications")
def apply_note_modifications(clip, notes):
    by_id = {n._state["note_id"]: n for n in _notes(clip)}
    for modified in notes:
        target = by_id.get(modified._state.get("note_id"))
        if target is not None:
            for field in _NOTE_FIELDS:
                target._state[field] = modified._state[field]
    clip._notify("notes")


@behavior("Clip.Clip.get_notes")
def get_notes(clip, from_time, from_pitch, time_span, pitch_span):
    found = [n for n in _notes(clip) if _in_range(n, from_pitch, pitch_span, from_time, time_span)]
    found.sort(key=lambda n: (n._state["start_time"], n._state["pitch"]))
    return tuple((n._state["pitch"], n._state["start_time"], n._state["duration"],
                  n._state["velocity"], n._state["mute"]) for n in found)


@behavior("Clip.Clip.set_notes")
def set_notes(clip, notes):
    specs = [clip_mod.MidiNoteSpecification(pitch, start, duration, velocity, mute)
             for pitch, start, duration, velocity, mute in notes]
    add_new_notes(clip, specs)


# ------------------------------------------------------------ song/track/scene

def _new_clip_slot(track):
    slot = clip_slot_mod.ClipSlot()
    slot._parent = track
    return slot


def _build_track(song, kind, with_slots=True):
    midi = kind == "midi"
    count = len(song.tracks) + len(song.return_tracks)
    track = track_mod.Track(
        name="%d %s" % (count + 1, "MIDI" if midi else "Audio"),
        has_midi_input=midi, has_audio_input=not midi,
        has_midi_output=midi, has_audio_output=not midi,
        can_be_armed=True,
    )
    track._parent = song
    if with_slots:
        track._update("clip_slots", _vector(_new_clip_slot(track) for _ in song.scenes))
        for scene, slot in zip(song.scenes, track.clip_slots):
            scene.clip_slots._append(slot)
    return track


def _select_if_empty(song, track):
    view = song.view
    if view._state.get("selected_track") is None:
        view._update("selected_track", track)


def _add_track(song, kind, index):
    track = _build_track(song, kind)
    if index is None or index < 0 or index >= len(song.tracks):
        song.tracks._append(track)
        position = len(song.tracks) - 1
    else:
        song.tracks._insert(index, track)
        position = index
        for scene in song.scenes:
            slots = scene.clip_slots._items
            slots.insert(position, slots.pop())
    _select_if_empty(song, track)
    song._notify("tracks")
    song._notify("visible_tracks")
    return track


@getter("Song.Song.visible_tracks")
def visible_tracks(song):
    return _vector(song.tracks)


@behavior("Song.Song.create_midi_track")
def create_midi_track(song, index=None):
    return _add_track(song, "midi", index)


@behavior("Song.Song.create_audio_track")
def create_audio_track(song, index=None):
    return _add_track(song, "audio", index)


@behavior("Song.Song.create_return_track")
def create_return_track(song):
    track = _build_track(song, "audio", with_slots=False)
    track._update("name", chr(ord("A") + len(song.return_tracks)) + "-Return")
    song.return_tracks._append(track)
    song._notify("return_tracks")
    return track


@behavior("Song.Song.delete_track")
def delete_track(song, index):
    track = song.tracks[index]
    song.tracks._items.pop(index)
    for scene in song.scenes:
        scene.clip_slots._items.pop(index)
    view = song.view
    if view._state.get("selected_track") is track:
        remaining = list(song.tracks)
        view._update("selected_track", remaining[min(index, len(remaining) - 1)] if remaining else None)
    song._notify("tracks")
    song._notify("visible_tracks")


@behavior("Song.Song.delete_return_track")
def delete_return_track(song, index):
    song.return_tracks._items.pop(index)
    song._notify("return_tracks")


def _copy_clip(clip, slot):
    clone = clip_mod.Clip(**{k: v for k, v in clip._state.items() if k not in ("notes_store", "selected_ids")})
    clone._update("is_playing", False)
    clone._parent = slot
    clone._state["notes_store"] = []
    for note in _notes(clip):
        _note_ids[0] += 1
        copied = clip_mod.MidiNote(**note._state)
        copied._state["note_id"] = _note_ids[0]
        clone._state["notes_store"].append(copied)
    return clone


@behavior("Song.Song.duplicate_track")
def duplicate_track(song, index):
    source = song.tracks[index]
    kind = "midi" if source._state.get("has_midi_input") else "audio"
    clone = _add_track(song, kind, index + 1)
    clone._update("name", source.name)
    for src_slot, dst_slot in zip(source.clip_slots, clone.clip_slots):
        if src_slot.has_clip:
            _set_clip(dst_slot, _copy_clip(src_slot.clip, dst_slot))
    for device in source.devices:
        _insert_device(clone, make_device(device.name, _kind_name(device)), -1)


def _kind_name(device):
    return {1: "instrument", 2: "audio_effect", 4: "midi_effect"}.get(int(device.type), "instrument")


def _build_scene(song):
    scene = scene_mod.Scene(name="", is_triggered=False)
    scene._parent = song
    scene._update("clip_slots", _vector())
    return scene


@behavior("Song.Song.create_scene")
def create_scene(song, index=-1):
    scene = _build_scene(song)
    position = len(song.scenes) if index is None or index < 0 or index > len(song.scenes) else index
    for track in song.tracks:
        slot = _new_clip_slot(track)
        track.clip_slots._insert(position, slot)
        scene.clip_slots._append(slot)
    song.scenes._insert(position, scene)
    if song.view._state.get("selected_scene") is None:
        song.view._update("selected_scene", scene)
    song._notify("scenes")
    return scene


@behavior("Song.Song.delete_scene")
def delete_scene(song, index):
    scene = song.scenes[index]
    song.scenes._items.pop(index)
    for track in song.tracks:
        track.clip_slots._items.pop(index)
    if song.view._state.get("selected_scene") is scene:
        remaining = list(song.scenes)
        song.view._update("selected_scene", remaining[min(index, len(remaining) - 1)] if remaining else None)
    song._notify("scenes")


@behavior("Song.Song.duplicate_scene")
def duplicate_scene(song, index):
    source = song.scenes[index]
    clone = create_scene(song, index + 1)
    clone._update("name", source.name)
    for src_slot, dst_slot in zip(source.clip_slots, clone.clip_slots):
        if src_slot.has_clip:
            _set_clip(dst_slot, _copy_clip(src_slot.clip, dst_slot))


@behavior("Scene.Scene.fire")
def fire_scene(scene, *args, **kwargs):
    for slot in scene.clip_slots:
        if slot.has_clip:
            fire_slot(slot)
        else:
            stop_slot_in_track(slot)
    scene.canonical_parent._update("is_playing", True)


def stop_slot_in_track(slot):
    for other in slot.canonical_parent.clip_slots:
        stop_slot(other)


@behavior("Song.Song.start_playing")
def start_playing(song):
    song._update("is_playing", True)


@behavior("Song.Song.continue_playing")
def continue_playing(song):
    song._update("is_playing", True)


@behavior("Song.Song.stop_playing")
def stop_playing(song):
    if song.is_playing:
        song._update("is_playing", False)
    else:
        song._update("current_song_time", 0.0)


@behavior("Song.Song.jump_by")
def jump_by(song, beats):
    song._update("current_song_time", max(0.0, song.current_song_time + beats))


@behavior("Song.Song.stop_all_clips")
def stop_all_clips(song, *args, **kwargs):
    for track in song.tracks:
        stop_all_track_clips(track)


@behavior("Song.Song.undo")
def undo(song):
    _runtime.undo()
    return ""


@behavior("Song.Song.redo")
def redo(song):
    _runtime.redo()
    return ""


getter("Song.Song.can_undo")(lambda song: _runtime.can_undo())
getter("Song.Song.can_redo")(lambda song: _runtime.can_redo())

DEFAULTS["Song.Song.tempo"] = 120.0
DEFAULTS["Song.Song.signature_numerator"] = 4
DEFAULTS["Song.Song.signature_denominator"] = 4
DEFAULTS["Song.Song.master_track"] = lambda song: _master(song)


def _master(song):
    master = track_mod.Track(name="Master", has_audio_input=False, has_audio_output=True)
    master._parent = song
    return master


# --------------------------------------------------------------------- browser

# category -> (kind of device, device names). Extend with ``add_browser_item``.
CATALOG = {
    "instruments": ("instrument", [
        "Analog", "Collision", "Drift", "Drum Rack", "Electric", "Instrument Rack", "Meld", "Operator",
        "Sampler", "Simpler", "Tension", "Wavetable"]),
    "audio_effects": ("audio_effect", [
        "Amp", "Audio Effect Rack", "Auto Filter", "Beat Repeat", "Chorus-Ensemble", "Compressor",
        "Delay", "EQ Eight", "Echo", "Erosion", "Gate", "Glue Compressor", "Limiter", "Phaser-Flanger",
        "Reverb", "Saturator", "Utility"]),
    "midi_effects": ("midi_effect", [
        "Arpeggiator", "Chord", "MIDI Effect Rack", "Note Length", "Pitch", "Random", "Scale", "Velocity"]),
}
_FOLDER_ONLY = ("drums", "sounds", "samples", "clips", "packs", "plugins", "max_for_live",
                "user_library", "current_project")
_LABELS = {"instruments": "Instruments", "audio_effects": "Audio Effects", "midi_effects": "MIDI Effects",
           "drums": "Drums", "sounds": "Sounds", "samples": "Samples", "clips": "Clips", "packs": "Packs",
           "plugins": "Plug-ins", "max_for_live": "Max for Live", "user_library": "User Library",
           "current_project": "Current Project"}


def make_browser_item(name, uri=None, folder=False, loadable=False, device=False, children=()):
    item = browser_mod.BrowserItem(
        name=name, uri=uri or "query:%s" % name.replace(" ", "%20"), source="",
        is_folder=folder or bool(children), is_loadable=loadable, is_device=device, is_selected=False,
    )
    item._update("children", browser_mod.BrowserItemVector(children))
    return item


def _category(attr):
    label = _LABELS[attr]
    kind_names = CATALOG.get(attr)
    if kind_names is None:
        return make_browser_item(label, "query:%s" % label.replace(" ", "%20"), folder=True)
    devices = [
        make_browser_item(name, "query:%s#%s" % (label.replace(" ", "%20"), name.replace(" ", "%20")),
                          loadable=True, device=True)
        for name in kind_names[1]
    ]
    return make_browser_item(label, "query:%s" % label.replace(" ", "%20"), folder=True, children=devices)


def _category_default(attr):
    return lambda browser: _category(attr)


for _attr in list(CATALOG) + list(_FOLDER_ONLY):
    DEFAULTS["Browser.Browser.%s" % _attr] = _category_default(_attr)

@getter("Browser.BrowserItem.iter_children")
def iter_children(item):
    return browser_mod.BrowserItemIterator(item.children)


def add_browser_item(browser, category, name, kind=None, loadable=True, device=True):
    """Append a device/preset to a browser category (e.g. ``"instruments"``) for tests."""
    folder = getattr(browser, category)
    item = make_browser_item(name, "query:%s#%s" % (folder.name.replace(" ", "%20"), name.replace(" ", "%20")),
                             loadable=loadable, device=device)
    if kind is not None:
        item._state["device_kind"] = kind
    folder.children._append(item)
    return item


def _device_kind(item):
    explicit = item._state.get("device_kind")
    if explicit:
        return explicit
    for kind, names in CATALOG.values():
        if item.name in names:
            return kind
    return "instrument"


loaded_items = []


@behavior("Browser.Browser.load_item")
def load_item(browser, item):
    loaded_items.append(item)
    if not (item.is_loadable and item.is_device):
        return
    song = get_document(None)
    target = browser.hotswap_target
    track = song.view._state.get("selected_track")
    if target is not None and target.canonical_parent is not None:
        track = target.canonical_parent
        position = list(track.devices).index(target)
        track.devices._items.pop(position)
        _insert_device(track, make_device(item.name, _device_kind(item)), position)
        return
    if track is None:
        raise RuntimeError("No track selected to load %r onto" % item.name)
    device = _insert_device(track, make_device(item.name, _device_kind(item)), -1)
    track.view._update("selected_device", device)


@on_reset
def _clear_loaded():
    del loaded_items[:]


@behavior("Browser.Browser.preview_item")
def preview_item(browser, item):
    browser._state["previewing"] = item


@behavior("Browser.Browser.stop_preview")
def stop_preview(browser):
    browser._state["previewing"] = None


@behavior("Browser.Browser.relation_to_hotswap_target")
def relation_to_hotswap_target(browser, item):
    return browser_mod.Relation.none
