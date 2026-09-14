import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from pear_remote import controls


class ControlsTestCase(unittest.TestCase):
    def test_unknown_action_is_rejected(self):
        self.assertFalse(controls.dispatch("invalid"))

    def test_playpause_dispatches_to_api(self):
        with patch("pear_remote.controls.pear_client.send_command") as send_command:
            self.assertTrue(controls.dispatch("playpause"))
            send_command.assert_called_once_with("toggle-play")


if __name__ == "__main__":
    unittest.main()
