import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from pear_remote import pear_client


def test_sanitize_progress_clamps_elapsed():
    assert pear_client._sanitize_progress(120, 60) == (60, 60)
    assert pear_client._sanitize_progress(-1, 60) == (0, 60)


def test_sanitize_progress_rejects_implausible_duration():
    assert pear_client._sanitize_progress(10, 4 * 3600) == (0, 0)
