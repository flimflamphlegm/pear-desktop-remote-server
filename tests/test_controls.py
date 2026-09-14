import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from pear_remote import controls


def test_unknown_action_is_rejected():
    assert controls.dispatch("invalid") is False


def test_playpause_dispatches_to_api():
    with patch("pear_remote.controls.pear_client.send_command") as send_command:
        assert controls.dispatch("playpause") is True
        send_command.assert_called_once_with("toggle-play")
