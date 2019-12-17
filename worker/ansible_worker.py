import logging
import logging.config
import os
import socket

from trollius import SSLContext
import app as app
from worker import ansible_queue

# from workers.ansible_worker.ansible_server import AnsibleServer
from ansible_server import AnsibleServer

from util.log import logfile_path
from raven.handlers.logging import SentryHandler
from raven.conf import setup_logging

logger = logging.getLogger(__name__)

DEFAULT_WEBSOCKET_PORT = 8788
DEFAULT_CONTROLLER_PORT = 8688


def run_ansible_manager():
    websocket_port = int(
        os.environ.get(
            "ANSIBLE_WEBSOCKET_PORT",
            app.app.config.get("ANSIBLE_WEBSOCKET_PORT", DEFAULT_WEBSOCKET_PORT),
        )
    )
    controller_port = int(
        os.environ.get(
            "ANSIBLE_CONTROLLER_PORT",
            app.app.config.get("ANSIBLE_CONTROLLER_PORT", DEFAULT_CONTROLLER_PORT),
        )
    )

    ssl_context = None
    if os.environ.get("SSL_CONFIG"):
        logger.debug("Loading SSL cert and key")
        ssl_context = SSLContext()
        ssl_context.load_cert_chain(
            os.path.join(os.environ.get("SSL_CONFIG"), "ssl.cert"),
            os.path.join(os.environ.get("SSL_CONFIG"), "ssl.key"),
        )

    server = AnsibleServer(app.app.config["SERVER_HOSTNAME"], ansible_queue)
    server.run("0.0.0.0", websocket_port, controller_port, ssl=ssl_context)


if __name__ == "__main__":
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "DEBUG",  #'INFO',
                "formatter": "standard",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "": {"handlers": ["default"], "level": "DEBUG", "propagate": True}  #'INFO',
        },
    }
    logging.config.dictConfig(logging_config)

    run_ansible_manager()
