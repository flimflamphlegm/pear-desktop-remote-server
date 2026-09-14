#!/usr/bin/env python3
"""Application entry point."""

import http.server
import logging
import time

import config
import net_utils
from pear_remote_handler import PearRemoteHandler

_RESTART_DELAY_SECONDS = 5


def run_forever() -> None:
    """Run the HTTP server and recover from network/socket interruptions."""
    http.server.HTTPServer.allow_reuse_address = True
    while True:
        server = None
        try:
            server = http.server.ThreadingHTTPServer((config.HOST, config.PORT), PearRemoteHandler)
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("Server stopped manually.")
            break
        except OSError as error:
            logging.error("Server interruption: %s", error)
            time.sleep(_RESTART_DELAY_SECONDS)
        finally:
            if server is not None:
                server.server_close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Pear Remote Server: http://%s:%s", net_utils.get_local_ip(), config.PORT)
    run_forever()


if __name__ == "__main__":
    main()
