import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(
    log_level: str = "INFO",
) -> None:
    """
    Configure application-wide logging.

    Logs are written to stdout so they can later be
    collected by Docker, CI/CD systems, and AWS CloudWatch.
    """
    logging.basicConfig(
        level=getattr(
            logging,
            log_level.upper(),
            logging.INFO,
        ),
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )
