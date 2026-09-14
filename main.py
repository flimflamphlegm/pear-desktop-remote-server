#!/usr/bin/env python3
"""Root entry point for the Pear Desktop Remote server."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).with_name("src")))

from pear_remote.main import main


if __name__ == "__main__":
    main()
