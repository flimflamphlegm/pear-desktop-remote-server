"""Dispatch control actions to Pear Desktop."""


from __future__ import annotations


import logging


from . import pear_client


LOGGER = logging.getLogger(__name__)


_CONTROLS = frozenset(["playpause", "next", "prev", "vol_up", "vol_down"])


def dispatch(action: str) -> bool:
    """Send a control command to Pear Desktop. Return True if recognized."""
    if action not in _CONTROLS:
        LOGGER.debug("Unrecognized control action: %s", action)
        return False
    return pear_client.send_command(action)
