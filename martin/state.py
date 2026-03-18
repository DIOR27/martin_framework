"""
Martin reactive state primitives.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List


class Signal:
    """Reactive value container."""

    def __init__(self, value: Any = None):
        self._value = value
        self._subscribers: List[Callable[[Any], None]] = []

    def get(self) -> Any:
        return self._value

    def set(self, value: Any) -> None:
        if value == self._value:
            return
        self._value = value
        for fn in list(self._subscribers):
            fn(value)

    def subscribe(self, fn: Callable[[Any], None], emit: bool = False) -> Callable[[], None]:
        self._subscribers.append(fn)
        if emit:
            fn(self._value)

        def _off():
            self.unsubscribe(fn)

        return _off

    def unsubscribe(self, fn: Callable[[Any], None]) -> None:
        try:
            self._subscribers.remove(fn)
        except ValueError:
            pass

    value = property(get, set)


class Computed(Signal):
    """Read-only computed value derived from other signals."""

    def __init__(self, compute: Callable[[], Any], *deps: Signal):
        self._compute = compute
        self._deps = deps
        super().__init__(compute())
        for dep in deps:
            dep.subscribe(lambda _v, self=self: self._recompute())

    def _recompute(self) -> None:
        super().set(self._compute())

    def set(self, value: Any) -> None:  # pragma: no cover
        raise RuntimeError("Computed values are read-only.")


class Store:
    """Global key/value reactive store."""

    def __init__(self, initial: Dict[str, Any] | None = None):
        self._signals: Dict[str, Signal] = {}
        for k, v in (initial or {}).items():
            self._signals[str(k)] = Signal(v)

    def signal(self, key: str, default: Any = None) -> Signal:
        k = str(key)
        if k not in self._signals:
            self._signals[k] = Signal(default)
        return self._signals[k]

    def get(self, key: str, default: Any = None) -> Any:
        return self.signal(key, default).get()

    def set(self, key: str, value: Any) -> None:
        self.signal(key).set(value)

    def update(self, values: Dict[str, Any]) -> None:
        for k, v in (values or {}).items():
            self.set(k, v)

    def subscribe(self, key: str, fn: Callable[[Any], None], emit: bool = False):
        return self.signal(key).subscribe(fn, emit=emit)

    def snapshot(self) -> Dict[str, Any]:
        return {k: sig.get() for k, sig in self._signals.items()}

