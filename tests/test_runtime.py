import Live
from Live import _runtime


def test_property_set_fires_listener_only_on_change(song):
    calls = []
    song.add_tempo_listener(lambda: calls.append(song.tempo))
    song.tempo = 140.0
    song.tempo = 140.0
    assert calls == [140.0]


def test_listener_triple(song):
    def cb():
        pass
    assert not song.tempo_has_listener(cb)
    song.add_tempo_listener(cb)
    assert song.tempo_has_listener(cb)
    song.remove_tempo_listener(cb)
    assert not song.tempo_has_listener(cb)


def test_listener_errors_are_captured_not_raised(song):
    def boom():
        raise ValueError("x")
    song.add_tempo_listener(boom)
    song.tempo = 90.0
    assert isinstance(_runtime.listener_errors[0], ValueError)


def test_read_only_property_rejects_assignment(song):
    try:
        song.master_track = None
    except AttributeError:
        return
    raise AssertionError("master_track should be read-only")


def test_call_log_records_sets_calls_and_functions(song):
    song.tempo = 100.0
    song.create_midi_track()
    Live.Application.get_application()
    kinds = [(r.kind, r.name) for r in Live.call_log]
    assert ("set", "tempo") in kinds
    assert ("call", "create_midi_track") in kinds
    assert ("function", "get_application") in kinds
    assert [r.args for r in _runtime.calls("tempo")] == [(100.0,)]


def test_reset_clears_state_log_and_singletons(app, song):
    song.create_midi_track()
    Live.reset()
    assert Live.call_log == []
    fresh = Live.Application.get_application().get_document()
    assert fresh is not song
    assert len(fresh.tracks) == 0


def test_undo_redo_property_changes(song):
    assert not song.can_undo
    song.tempo = 150.0
    assert song.can_undo
    song.undo()
    assert song.tempo == 120.0
    assert song.can_redo
    song.redo()
    assert song.tempo == 150.0


def test_canonical_parent_chain(song):
    track = song.create_midi_track()
    assert track.canonical_parent is song
    assert track.view.canonical_parent is track
    assert track.mixer_device.canonical_parent is track
    assert track.mixer_device.volume.canonical_parent is track.mixer_device


def test_timer_is_driven_manually():
    ticks = []
    timer = Live.Base.Timer(callback=lambda: ticks.append(1), interval=20, repeat=True)
    timer.tick()
    assert ticks == []
    timer.start()
    timer.tick()
    timer.tick()
    assert ticks == [1, 1] and timer.running
    timer.stop()
    timer.tick()
    assert ticks == [1, 1]
