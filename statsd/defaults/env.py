import os

from statsd.client import StatsClient
from statsd.defaults import Config

statsd = None

if statsd is None:
    config = Config.create_with(os.environ)
    statsd = StatsClient(
        host=config.host,
        port=config.port,
        prefix=config.prefix,
        maxudpsize=config.maxudpsize,
        ipv6=config.ipv6,
    )
