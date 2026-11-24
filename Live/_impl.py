"""Hand-written Live classes that cannot be generated from the stubs."""
from __future__ import annotations

from ._runtime import MockObject


class Vector(MockObject):
    """Read-only container Live returns for collections (``Song.tracks`` etc.).

    Mock code fills it through the underscore methods; typed subclasses such as
    ``IntVector`` expose the public ``append``/``extend`` the real stubs declare.
    """

    def __init__(self, items=()):
        super().__init__()
        self._items = list(items)

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __bool__(self):
        return bool(self._items)

    def __contains__(self, value):
        return value in self._items

    def __getitem__(self, index):
        if isinstance(index, slice):
            return type(self)(self._items[index])
        return self._items[index]

    def __eq__(self, other):
        if isinstance(other, Vector):
            return self._items == other._items
        if isinstance(other, (list, tuple)):
            return self._items == list(other)
        return NotImplemented

    __hash__ = object.__hash__

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self._items)

    def _append(self, value):
        self._items.append(value)

    def _extend(self, values):
        self._items.extend(values)

    def _insert(self, index, value):
        self._items.insert(index, value)

    def _remove(self, value):
        self._items.remove(value)

    def _clear(self):
        del self._items[:]


class Text(MockObject):
    """A translatable, immutable string."""

    def __init__(self, text=""):
        super().__init__(text=text)

    @property
    def text(self) -> str:
        return self._state["text"]

    def __str__(self):
        return self.text


class Timer(MockObject):
    """Mock of ``Live.Base.Timer``.

    Live drives timers from its own event loop; the mock never fires on its own.
    Call ``tick()`` from a test to run the callback once.
    """

    def __init__(self, callback, interval, repeat=False, start=False):
        super().__init__(callback=callback, interval=interval, repeat=repeat)
        self._running = False
        if start:
            self.start()

    @property
    def running(self) -> bool:
        return self._running

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def restart(self) -> None:
        self._running = True

    def tick(self) -> None:
        if not self._running:
            return
        if not self._state["repeat"]:
            self._running = False
        self._state["callback"]()


class BrowserItemIterator(MockObject):
    """Iterator over the children of a ``BrowserItem``."""

    def __init__(self, items=()):
        super().__init__()
        self._items = list(items)

    def __iter__(self):
        return iter(self._items)
