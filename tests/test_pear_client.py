import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from pear_remote import pear_client


class PearClientTestCase(unittest.TestCase):
    def test_sanitize_progress_clamps_elapsed(self):
        self.assertEqual(pear_client._sanitize_progress(120, 60), (60, 60))
        self.assertEqual(pear_client._sanitize_progress(-1, 60), (0, 60))

    def test_sanitize_progress_rejects_implausible_duration(self):
        self.assertEqual(pear_client._sanitize_progress(10, 4 * 3600), (0, 0))


if __name__ == "__main__":
    unittest.main()
