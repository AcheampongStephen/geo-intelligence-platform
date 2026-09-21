import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from src.api.exceptions import DatasetNotFoundError

logger = logging.getLogger(__name__)


async def dataset_not_found_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handle missing platform datasets.

    The exception parameter uses the base Exception type
    to satisfy Starlette's exception-handler contract.
    """

    if not isinstance(exc, DatasetNotFoundError):
        logger.exception(
            "Unexpected exception routed to dataset handler: request=%s",
            request.url.path,
            exc_info=exc,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected server error occurred.",
            },
        )

    logger.error(
        "Dataset unavailable: path=%s request=%s",
        exc.dataset_path,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "dataset_unavailable",
            "message": "Required platform data is unavailable.",
        },
    )
