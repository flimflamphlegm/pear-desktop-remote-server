from unittest.mock import patch

import controls


def test_unknown_action_is_rejected():
    assert controls.dispatch("invalid") is False


def test_playpause_dispatches_to_api():
    with patch("controls.pear_client.send_command") as send_command:
        assert controls.dispatch("playpause") is True
        send_command.assert_called_once_with("toggle-play")
