"""Guards that the generated package and the hand-written behaviour layer stay consistent."""
import ast
import importlib
import os
from pathlib import Path

import pytest

import Live
from Live import _runtime


def _member(module, qualname, member):
    obj = getattr(importlib.import_module("Live." + module), qualname.split(".")[0])
    for part in qualname.split(".")[1:]:
        obj = getattr(obj, part)
    return getattr(obj, member, None)


def _keys():
    keys = set(_runtime.BEHAVIORS) | set(_runtime.GETTERS) | set(_runtime.DEFAULTS)
    return sorted(keys)


@pytest.mark.parametrize("key", _keys())
def test_behavior_keys_name_real_members(key):
    parts = key.split(".")
    module = parts[0]
    mod = importlib.import_module("Live." + module)
    if len(parts) == 2:  # module-level function
        assert hasattr(mod, parts[1]), key
        return
    assert _member(module, ".".join(parts[1:-1]), parts[-1]) is not None, key


def test_all_stub_modules_present():
    expected = {"Application", "Base", "Browser", "Clip", "ClipSlot", "Device", "DeviceParameter",
                "LomObject", "Scene", "Song", "Track", "MixerDevice", "Chain", "RackDevice"}
    assert expected <= set(Live.__all__)


def test_enums_behave_like_ints():
    assert Live.Browser.FilterType.disabled == -1
    assert Live.Browser.Relation.none == 3
    assert Live.Device.DeviceType.midi_effect == 4


def test_listener_triple_exists_for_every_listenable_property():
    for cls in (Live.Song.Song, Live.Track.Track, Live.Clip.Clip, Live.Device.Device, Live.Scene.Scene):
        for name in dir(cls):
            if name.startswith("add_") and name.endswith("_listener"):
                prop = name[4:-9]
                assert hasattr(cls, "remove_%s_listener" % prop), (cls, prop)
                assert hasattr(cls, "%s_has_listener" % prop), (cls, prop)


STUBS = os.environ.get("LIVEAPI_STUBS")


@pytest.mark.skipif(not STUBS, reason="set LIVEAPI_STUBS to <stubs>/<version>/Live to check parity")
def test_every_stub_member_is_generated():
    missing = []
    for path in sorted(Path(STUBS).glob("*.pyi")):
        if path.stem == "__init__":
            continue
        module = importlib.import_module("Live." + path.stem)
        tree = ast.parse(path.read_text())

        def check(prefix, node):
            owner = module
            for part in prefix:
                owner = getattr(owner, part, None)
                if owner is None:
                    missing.append("%s.%s" % (path.stem, ".".join(prefix)))
                    return
            for item in node.body:
                if isinstance(item, ast.ClassDef):
                    check(prefix + [item.name], item)
                elif isinstance(item, ast.FunctionDef) and not item.name.startswith("__"):
                    if not hasattr(owner, item.name):
                        missing.append("%s.%s.%s" % (path.stem, ".".join(prefix), item.name))

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                check([node.name], node)
            elif isinstance(node, ast.FunctionDef) and not hasattr(module, node.name):
                missing.append("%s.%s" % (path.stem, node.name))
    assert not missing, missing[:20]
