"""Runtime support for the generated Live mock: state, listeners, call log, undo."""
from __future__ import annotations

import importlib
from collections import namedtuple
from typing import Any, Callable, Dict, List

_PKG = __name__.rpartition(".")[0]
_MISSING = object()

CallRecord = namedtuple("CallRecord", "kind target name args kwargs")

# Every method call ("call"), module-level function call ("function") and
# property assignment ("set") made through the mock, in order.
call_log: List[CallRecord] = []
# Exceptions raised by listener callbacks (real Live logs and swallows them).
listener_errors: List[BaseException] = []

# Hand-written behaviour, keyed "<Module>.<Class>[.<Nested>].<member>".
BEHAVIORS: Dict[str, Callable[..., Any]] = {}
GETTERS: Dict[str, Callable[[Any], Any]] = {}
DEFAULTS: Dict[str, Any] = {}

_undo_stack: List[tuple] = []
_redo_stack: List[tuple] = []
_reset_hooks: List[Callable[[], None]] = []


def behavior(key):
    def register(fn):
        BEHAVIORS[key] = fn
        return fn
    return register


def getter(key):
    def register(fn):
        GETTERS[key] = fn
        return fn
    return register


def on_reset(fn):
    _reset_hooks.append(fn)
    return fn


def calls(name=None, target=None):
    """Call-log entries, optionally filtered by member name and/or target class name."""
    return [
        r for r in call_log
        if (name is None or r.name == name) and (target is None or r.target == target)
    ]


def reset():
    """Drop all session state, the call log and the undo history."""
    del call_log[:]
    del listener_errors[:]
    del _undo_stack[:]
    del _redo_stack[:]
    for hook in _reset_hooks:
        hook()


def resolve_class(module, qualname):
    obj = importlib.import_module("%s.%s" % (_PKG, module))
    for part in qualname.split("."):
        obj = getattr(obj, part)
    return obj


def make(spec):
    """Build a default value from a generator spec (see scripts/generate_live.py)."""
    if isinstance(spec, tuple) and len(spec) == 2 and all(isinstance(s, str) for s in spec):
        cls = resolve_class(*spec)
        try:
            return cls()
        except TypeError:
            return None
    if isinstance(spec, tuple) and len(spec) == 3 and isinstance(spec[0], str):
        return resolve_class(spec[0], spec[1])(spec[2])
    return spec


class MockObject:
    """Base of every generated Live class."""

    def __init__(self, **state):
        self._state = dict(state)
        self._listeners: Dict[str, list] = {}
        self._parent = None

    @classmethod
    def _keys(cls):
        keys = cls.__dict__.get("_key_cache")
        if keys is None:
            keys = []
            for klass in cls.__mro__:
                if klass.__module__.startswith(_PKG + ".") and not klass.__module__.endswith("_runtime"):
                    keys.append("%s.%s" % (klass.__module__.rpartition(".")[2], klass.__qualname__))
            cls._key_cache = keys
        return keys

    def _target(self):
        return type(self).__qualname__

    def _lookup(self, table, member):
        for key in self._keys():
            found = table.get(key + "." + member, _MISSING)
            if found is not _MISSING:
                return found
        return _MISSING

    def _get(self, name, spec):
        getter_fn = self._lookup(GETTERS, name)
        if getter_fn is not _MISSING:
            return getter_fn(self)
        if name in self._state:
            return self._state[name]
        if name == "canonical_parent":
            return self._parent
        default = self._lookup(DEFAULTS, name)
        if default is _MISSING:
            value = make(spec)
        else:
            value = default(self) if callable(default) else default
        if isinstance(value, MockObject) and value._parent is None:
            value._parent = self
        self._state[name] = value
        return value

    def _set(self, name, value, spec=None):
        old = self._get(name, spec)
        call_log.append(CallRecord("set", self._target(), name, (value,), {}))
        if old == value:
            return
        _undo_stack.append((self, name, old))
        del _redo_stack[:]
        self._state[name] = value
        self._notify(name)

    def _update(self, name, value):
        """Change state from mock behaviour: notifies listeners, no call-log/undo entry."""
        if self._state.get(name, _MISSING) is value:
            return
        self._state[name] = value
        self._notify(name)

    def _call(self, name, args, kwargs, spec):
        call_log.append(CallRecord("call", self._target(), name, args, kwargs))
        fn = self._lookup(BEHAVIORS, name)
        if fn is not _MISSING:
            return fn(self, *args, **kwargs)
        return make(spec)

    def _add_listener(self, name, callback):
        listeners = self._listeners.setdefault(name, [])
        if callback not in listeners:
            listeners.append(callback)

    def _remove_listener(self, name, callback):
        listeners = self._listeners.get(name, [])
        if callback in listeners:
            listeners.remove(callback)

    def _has_listener(self, name, callback):
        return callback in self._listeners.get(name, [])

    def _notify(self, name):
        for callback in list(self._listeners.get(name, [])):
            try:
                callback()
            except Exception as exc:  # real Live logs listener errors instead of raising
                listener_errors.append(exc)

    def __repr__(self):
        label = self._state.get("name")
        return "<%s%s>" % (type(self).__qualname__, " %r" % label if isinstance(label, str) and label else "")


def call_function(module, name, args, kwargs, spec):
    call_log.append(CallRecord("function", module, name, args, kwargs))
    fn = BEHAVIORS.get("%s.%s" % (module, name))
    if fn is not None:
        return fn(*args, **kwargs)
    return make(spec)


def can_undo():
    return bool(_undo_stack)


def can_redo():
    return bool(_redo_stack)


def undo():
    if _undo_stack:
        obj, name, old = _undo_stack.pop()
        _redo_stack.append((obj, name, obj._state.get(name)))
        obj._state[name] = old
        obj._notify(name)


def redo():
    if _redo_stack:
        obj, name, value = _redo_stack.pop()
        _undo_stack.append((obj, name, obj._state.get(name)))
        obj._state[name] = value
        obj._notify(name)
