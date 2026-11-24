import pytest

import Live


def names(vector):
    return [i.name for i in vector]


def test_browser_categories(app):
    browser = app.browser
    assert browser is app.browser
    for category in ("instruments", "audio_effects", "midi_effects", "drums", "sounds", "samples",
                     "clips", "packs", "plugins", "max_for_live", "user_library", "current_project"):
        item = getattr(browser, category)
        assert item.is_folder
    assert len(browser.user_folders) == 0 and len(browser.legacy_libraries) == 0
    assert browser.filter_type == Live.Browser.FilterType.disabled
    assert browser.hotswap_target is None


def test_browser_items(app):
    instruments = app.browser.instruments
    assert "Operator" in names(instruments.children)
    assert instruments.name == "Instruments"
    operator = next(i for i in instruments.iter_children if i.name == "Operator")
    assert operator.is_device and operator.is_loadable and operator.uri
    assert "Reverb" in names(app.browser.audio_effects.children)
    assert "Arpeggiator" in names(app.browser.midi_effects.children)


def test_load_item_inserts_device_on_selected_track(app, song):
    song.create_midi_track()
    second = song.create_midi_track()
    song.view.selected_track = second
    item = next(i for i in app.browser.instruments.children if i.name == "Wavetable")
    app.browser.load_item(item)
    assert names(second.devices) == ["Wavetable"]
    assert len(song.tracks[0].devices) == 0
    device = second.devices[0]
    assert device.canonical_parent is second
    assert device.class_name == "Wavetable" and device.type == Live.Device.DeviceType.instrument
    assert second.view.selected_device is device
    assert Live._behaviors.loaded_items == [item]


def test_load_effects_appends_to_chain(app, song):
    track = song.create_midi_track()
    for category, name in (("instruments", "Operator"), ("audio_effects", "EQ Eight"), ("midi_effects", "Chord")):
        item = next(i for i in getattr(app.browser, category).children if i.name == name)
        app.browser.load_item(item)
    assert names(track.devices) == ["Operator", "EQ Eight", "Chord"]
    assert [int(d.type) for d in track.devices] == [1, 2, 4]


def test_load_item_without_track_fails(app):
    item = app.browser.instruments.children[0]
    with pytest.raises(RuntimeError):
        app.browser.load_item(item)


def test_load_item_hotswap_replaces_target(app, song):
    track = song.create_midi_track()
    track.insert_device("Operator")
    app.browser.hotswap_target = track.devices[0]
    simpler = next(i for i in app.browser.instruments.children if i.name == "Simpler")
    app.browser.load_item(simpler)
    assert names(track.devices) == ["Simpler"]


def test_add_custom_browser_item(app, song):
    track = song.create_midi_track()
    item = Live._behaviors.add_browser_item(app.browser, "instruments", "My Synth")
    assert "My Synth" in names(app.browser.instruments.children)
    app.browser.load_item(item)
    assert names(track.devices) == ["My Synth"]


def test_preview_item(app):
    item = app.browser.instruments.children[0]
    app.browser.preview_item(item)
    app.browser.stop_preview()
    assert [r.name for r in Live.call_log if r.kind == "call"] == ["preview_item", "stop_preview"]
    assert Live._runtime.calls("preview_item")[0].args == (item,)


def test_relation_to_hotswap_target_defaults_to_none(app):
    item = app.browser.instruments.children[0]
    assert app.browser.relation_to_hotswap_target(item) == Live.Browser.Relation.none


def test_device_chain_editing(song):
    track = song.create_midi_track()
    seen = []
    track.add_devices_listener(lambda: seen.append(len(track.devices)))
    track.insert_device("Operator")
    track.insert_device("Reverb", 0)
    assert names(track.devices) == ["Reverb", "Operator"]
    track.duplicate_device(0)
    assert names(track.devices) == ["Reverb", "Reverb", "Operator"]
    track.delete_device(1)
    assert names(track.devices) == ["Reverb", "Operator"]
    assert seen == [1, 2, 3, 2]


def test_device_parameters_and_view(song):
    device = song.create_midi_track().insert_device("Operator")
    assert device.name == "Operator" and device.is_active
    on = device.parameters[0]
    assert on.name == "Device On" and on.is_quantized and on.value == 1.0
    seen = []
    on.add_value_listener(lambda: seen.append(on.value))
    on.value = 0.0
    assert seen == [0.0]
    device.view.is_collapsed = True
    assert device.view.is_collapsed
    assert device.view.canonical_parent is device


def test_device_parameter_gestures_are_logged(song):
    param = song.create_midi_track().insert_device("Operator").parameters[0]
    param.begin_gesture()
    param.end_gesture()
    assert [r.name for r in Live.call_log if r.kind == "call"][-2:] == ["begin_gesture", "end_gesture"]
