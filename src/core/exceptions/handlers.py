import uuid
from typing import cast

from fastapi import Request
from fastapi.responses import JSONResponse

from schemas.errors import ErrorResponse, ErrorContent
from core.exceptions.api_exceptions import BaseAPIException


def get_trace_id(request: Request) -> str:
    #TODO: move generation request id to Middleware
    return request.headers.get("X-Request-ID", str(uuid.uuid4()))


async def base_api_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    exc = cast(BaseAPIException, exc) # need only for mypy

    trace_id = get_trace_id(request)
    content = ErrorResponse(
        error=ErrorContent(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            trace_id=trace_id
        )
    ).model_dump()

    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    trace_id = get_trace_id(request)
    
    #TODO: change to logger
    print(f"ERROR [trace_id={trace_id}]: {exc}")

    content = ErrorResponse(
        error=ErrorContent(
            code="INTERNAL_SERVER_ERROR",
            message="An error has occurred on the server. Please contact support.",
            trace_id=trace_id
        )
    ).model_dump()

    return JSONResponse(status_code=500, content=content)