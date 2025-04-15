import functools
from inspect import iscoroutinefunction
from time import perf_counter as time_now
from typing import TYPE_CHECKING, Any, Callable, Optional


def safe_wraps(wrapper: Callable, *args: Any, **kwargs: Any) -> Callable:
    """Safely wraps partial functions."""
    while isinstance(wrapper, functools.partial):
        wrapper = wrapper.func
    return functools.wraps(wrapper, *args, **kwargs)


class Timer:
    """A context manager/decorator for statsd.timing()."""

    def __init__(self, client, stat: str, rate: float = 1.0) -> None:
        if TYPE_CHECKING:
            from statsd.client.base import StatsClientBase

            assert isinstance(client, StatsClientBase)

        self.client = client
        self.stat = stat
        self.rate: float = rate
        self.ms: Optional[float] = None
        self._sent: bool = False
        self._start_time: float = None  # type: ignore

    def __call__(self, f) -> Callable:
        """Thread-safe timing function decorator."""
        if iscoroutinefunction(f):

            @safe_wraps(f)
            async def _async_wrapped(*args, **kwargs):
                start_time = time_now()
                try:
                    return await f(*args, **kwargs)
                finally:
                    elapsed_time_ms = 1000.0 * (time_now() - start_time)
                    self.client.timing(self.stat, elapsed_time_ms, self.rate)

            return _async_wrapped

        @safe_wraps(f)
        def _wrapped(*args, **kwargs):
            start_time = time_now()
            try:
                return f(*args, **kwargs)
            finally:
                elapsed_time_ms = 1000.0 * (time_now() - start_time)
                self.client.timing(self.stat, elapsed_time_ms, self.rate)

        return _wrapped

    def __enter__(self) -> "Timer":
        return self.start()

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> None:
        self.stop()

    def start(self) -> "Timer":
        self.ms = None
        self._sent = False
        self._start_time = time_now()
        return self

    def stop(self, send=True) -> "Timer":
        if self._start_time is None:
            raise RuntimeError("Timer has not started.")
        dt = time_now() - self._start_time
        self.ms = 1000.0 * dt  # Convert to milliseconds.
        if send:
            self.send()
        return self

    def send(self) -> None:
        if self.ms is None:
            raise RuntimeError("No data recorded.")
        if self._sent:
            raise RuntimeError("Already sent data.")
        self._sent = True
        self.client.timing(self.stat, self.ms, self.rate)
