"""Explicit trusted-LAN frontend origins; no production defaults are changed."""

import ipaddress
import os
from urllib.parse import urlsplit


def development_frontend_origins():
    origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://[::1]:3000"]
    lan = os.getenv("BTA_DEV_LAN_ORIGIN", "").rstrip("/")
    if lan:
        parsed = urlsplit(lan)
        try:
            address = ipaddress.ip_address(parsed.hostname or "")
            private_lan = any(address in ipaddress.ip_network(network) for network in
                              ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))
            valid = (parsed.scheme in {"http", "https"} and private_lan and parsed.port == 3000
                     and not parsed.username and not parsed.password and not parsed.path
                     and not parsed.query and not parsed.fragment)
        except ValueError:
            valid = False
        if not valid:
            raise ValueError("BTA_DEV_LAN_ORIGIN must be an explicit private LAN frontend origin on port 3000.")
        origins.append(lan)
    return origins
