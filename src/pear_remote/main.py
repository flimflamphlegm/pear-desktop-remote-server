"""Application entry point."""

import logging
import time
from http.server import HTTPServer, ThreadingHTTPServer

from . import config, net_utils
from .pear_remote_handler import PearRemoteHandler

_RESTART_DELAY_SECONDS = 5


def run_forever() -> None:
    HTTPServer.allow_reuse_address = True
    while True:
        server = None
        try:
            server = ThreadingHTTPServer((config.HOST, config.PORT), PearRemoteHandler)
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
