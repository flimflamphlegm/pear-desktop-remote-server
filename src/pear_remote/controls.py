"""Dispatch control actions to Pear Desktop."""


from __future__ import annotations


import logging


LOGGER = logging.getLogger(__name__)


_CONTROLS = frozenset(["playpause", "next", "prev", "vol_up", "vol_down"])


def dispatch(action: str) -> bool:
    """Send a control command to Pear Desktop. Return True if recognized."""
    LOGGER.debug("Dispatch action: %s", action)
    if action not in _CONTROLS:
        LOGGER.debug("Unrecognized control action: %s", action)
        return False
    # This is kept for backward compatibility but not used in minimal mode
    return True
