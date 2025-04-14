from dataclasses import dataclass
from typing import Any, Optional, Union


NOTSET = object()


@dataclass
class Config:
    HOST = "localhost"
    PORT = 8125
    IPV6 = False
    PREFIX = None
    MAXUDPSIZE = 512

    host: str = HOST
    port: int = PORT
    ipv6: bool = IPV6
    prefix: Optional[str] = PREFIX
    maxudpsize: int = MAXUDPSIZE

    @staticmethod
    def create_with(settings: Union[dict, Any]) -> "Config":
        result = Config()

        if not isinstance(settings, dict):
            settings = settings.__dict__

        for key in ("host", "port", "ipv6", "prefix", "maxudpsize"):
            value = settings.get(f"STATSD_{key.upper()}", NOTSET)
            if value is NOTSET:
                continue
            setattr(result, key, value)
        return result
