# LiveAPI-mock

An offline mock of Ableton Live's Python API, importable as `Live` exactly like inside Live
(`import Live`, `Live.Song.Song`, `Live.Base.Timer`). Use it to test remote scripts without Live.

## How it is built

* `Live/<Module>.py` is **generated** from the typed stubs in
  [PhotonicVelocity/LiveAPI](https://github.com/PhotonicVelocity/LiveAPI) (Live 12.3.6):
  every class, property, setter, `add_/remove_/..._has_listener` triple, method, enum and nested `View`.
  Regenerate with `scripts/regenerate.sh` (never edit generated files).
* `Live/_runtime.py`, `Live/_impl.py` are the shared base class and the few hand-written types
  (`Vector`, `Timer`, `Text`, `BrowserItemIterator`).
* `Live/_behaviors.py` adds the stateful behaviour: track/scene/clip-slot grid, clips and MIDI notes,
  devices, the browser tree and `load_item`, transport, undo. Anything without behaviour still exists:
  properties hold what you set, methods are logged and return a type-appropriate default.

## Use

```python
import Live

app = Live.Application.get_application()
song = app.get_document()
track = song.create_midi_track()
song.create_scene(-1)
clip = track.clip_slots[0].create_clip(4.0)
clip.add_new_notes([Live.Clip.MidiNoteSpecification(60, 0.0, 1.0)])

item = next(i for i in app.browser.instruments.children if i.name == "Operator")
app.browser.load_item(item)            # loads onto the selected track

song.add_tempo_listener(lambda: print("tempo", song.tempo))
song.tempo = 128.0                     # listeners fire on change, as in Live

Live.call_log                          # [CallRecord(kind, target, name, args, kwargs), ...]
Live._runtime.calls("create_clip")     # filter by member name
Live.reset()                           # clear session, call log, undo history (call between tests)
```

`Live.Base.Timer` never fires on its own: call `timer.tick()` in tests.
Add your own browser content with `Live._behaviors.add_browser_item(browser, "instruments", "My Synth")`.

## Develop

```
pip install -e . pytest
pytest tests                                  # 130 tests
LIVEAPI_STUBS=<stubs>/12.3.6/Live pytest tests/test_api_surface.py   # every stub member exists
docker build -t mantra-liveapi-mock . && docker run --rm mantra-liveapi-mock   # Python 3.7
```

## Limits

* Behaviour is hand-written for the common surface only (see `_behaviors.py`); the rest is generic.
* Undo/redo covers property assignments, not structural edits (creating/deleting tracks, clips, devices).
* Values are not validated (e.g. out-of-range `DeviceParameter.value`, wrong-kind devices), so a passing
  test is necessary but not sufficient for real Live.
* Positional-only parameters (`/` in the stubs) are accepted by keyword too (Python 3.7 has no `/`).
