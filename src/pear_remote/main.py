"""Application entry point."""

import http.server
import logging
import time

from . import config, net_utils
from .pear_remote_handler import PearRemoteHandler

_RESTART_DELAY_SECONDS = 5


def run_forever() -> None:
    """Serve continuously and recover from sleep/wake socket failures."""
    http.server.HTTPServer.allow_reuse_address = True

    while True:
        server = None
        try:
            server = http.server.ThreadingHTTPServer(
                (config.HOST, config.PORT),
                PearRemoteHandler,
            )
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("Server stopped manually.")
            break
        except Exception as error:
            logging.error("Server interruption: %s", error)
            if server is not None:
                try:
                    server.server_close()
                except Exception:
                    pass
            time.sleep(_RESTART_DELAY_SECONDS)
        finally:
            if server is not None:
                try:
                    server.server_close()
                except Exception:
                    pass


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Pear Remote Server: http://%s:%s", net_utils.get_local_ip(), config.PORT)
    run_forever()
