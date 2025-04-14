import socket
from typing import Optional

from statsd.defaults import Config

from .base import StatsClientBase, PipelineBase


class Pipeline(PipelineBase):
    def __init__(self, client):
        super().__init__(client)
        self._maxudpsize = client._maxudpsize

    def _send(self):
        data = self._stats.popleft()
        while self._stats:
            # Use popleft to preserve the order of the stats.
            stat = self._stats.popleft()
            if len(stat) + len(data) + 1 >= self._maxudpsize:
                self._client._after(data)
                data = stat
            else:
                data += "\n" + stat
        self._client._after(data)


class StatsClient(StatsClientBase):
    """A client for statsd."""

    def __init__(
        self,
        host: str = Config.HOST,
        port: int = Config.PORT,
        prefix: Optional[str] = Config.PREFIX,
        maxudpsize: int = Config.MAXUDPSIZE,
        ipv6: bool = Config.IPV6,
    ) -> None:
        """Create a new client."""
        fam = socket.AF_INET6 if ipv6 else socket.AF_INET
        family, _, _, _, addr = socket.getaddrinfo(host, port, fam, socket.SOCK_DGRAM)[
            0
        ]
        self._addr = addr
        self._sock: Optional[socket.socket] = socket.socket(family, socket.SOCK_DGRAM)
        self._maxudpsize = maxudpsize
        super().__init__(prefix=prefix)

    def _send(self, data) -> None:
        """Send data to statsd."""
        try:
            assert self._sock is not None

            self._sock.sendto(data.encode("ascii"), self._addr)
        except (OSError, RuntimeError):
            # No time for love, Dr. Jones!
            pass

    def close(self) -> None:
        if self._sock and hasattr(self._sock, "close"):
            self._sock.close()
        self._sock = None

    def pipeline(self) -> PipelineBase:
        return Pipeline(self)
