import socket
from typing import Optional

from statsd.defaults import Config

from .base import PipelineBase, StatsClientBase


class StreamPipeline(PipelineBase):
    def _send(self, _: Optional[str] = None) -> None:
        self._client._after("\n".join(self._stats))
        self._stats.clear()


class StreamClientBase(StatsClientBase):
    def __init__(self, sock: Optional[socket.socket], prefix: Optional[str] = None) -> None:
        self._sock: Optional[socket.socket] = sock
        super().__init__(prefix=prefix)

    def connect(self) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        if self._sock and hasattr(self._sock, "close"):
            self._sock.close()
        self._sock = None

    def reconnect(self) -> None:
        self.close()
        self.connect()

    def pipeline(self) -> StreamPipeline:
        return StreamPipeline(self)

    def _send(self, data) -> None:
        """Send data to statsd."""
        if not self._sock:
            self.connect()
        self._do_send(data)

    def _do_send(self, data: str) -> None:
        assert self._sock is not None
        self._sock.sendall(data.encode("ascii") + b"\n")


class TCPStatsClient(StreamClientBase):
    """TCP version of StatsClient."""

    def __init__(
        self,
        host: str = Config.HOST,
        port: int = Config.PORT,
        prefix: Optional[str] = Config.PREFIX,
        timeout: Optional[float] = None,
        ipv6: bool = Config.IPV6,
    ):
        """Create a new client."""
        self._host = host
        self._port = port
        self._ipv6 = ipv6
        self._timeout = timeout
        super().__init__(sock=None, prefix=prefix)

    def connect(self) -> None:
        fam = socket.AF_INET6 if self._ipv6 else socket.AF_INET
        family, _, _, _, addr = socket.getaddrinfo(self._host, self._port, fam, socket.SOCK_STREAM)[0]
        self._sock = socket.socket(family, socket.SOCK_STREAM)
        self._sock.settimeout(self._timeout)
        self._sock.connect(addr)


class UnixSocketStatsClient(StreamClientBase):
    """Unix domain socket version of StatsClient."""

    def __init__(
        self,
        socket_path: str,
        prefix: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        """Create a new client."""
        self._socket_path = socket_path
        self._timeout = timeout
        super().__init__(sock=None, prefix=prefix)

    def connect(self) -> None:
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.settimeout(self._timeout)
        self._sock.connect(self._socket_path)
