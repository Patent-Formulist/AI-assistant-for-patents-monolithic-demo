from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import HTTPException, Response

from core import logger

logger = logger.get_logger(__name__)


async def handle_file_request(
    file_type: str,
    default_filename: str,
    patent_id: str,
    func: Callable[..., Awaitable[bytes]],
    func_args: tuple[Any, ...] = (),
    func_kwargs: dict[str, Any] | None = None,
) -> Response:
    """
    Universal file export handler for CSV or XLSX downloads.

    This helper encapsulates the common logic for generating file responses:
    - determines the correct MIME type and file extension based on `file_type`
    - builds a filename using `default_filename` and `patent_id`
    - calls the provided asynchronous `func` with arbitrary arguments
    - returns a FastAPI `Response` with the binary content and appropriate headers

    The function is completely decoupled from the specific generator signature.
    Any callable that returns `Awaitable[bytes]` can be passed, along with its
    positional and keyword arguments via `func_args` and `func_kwargs`.

    Args:
        file_type (str):
            The output format. Must be either ``"csv"`` or ``"xlsx"`` or ``"docx"``.
        default_filename (str):
            Base name of the file (without extension) that will appear in
            the ``Content-Disposition`` header.
        patent_id (str):
            Patent identifier, used to make the filename unique
            (e.g., ``report_123e4567.csv``).
        func (Callable[..., Awaitable[bytes]]):
            An asynchronous callable that generates the file content.
            It may accept any number of positional and keyword arguments,
            which are provided via `func_args` and `func_kwargs`.
            Must return `bytes` (the raw file content) or raise an exception,
            which will be propagated to the caller.
        func_args (Tuple[Any, ...]):
            Positional arguments to pass to `func`.
            Defaults to an empty tuple.
        func_kwargs (Optional[dict[str, Any]]):
            Keyword arguments to pass to `func`.
            Defaults to `None` (treated as an empty dict).

    Returns:
        Response:
            A FastAPI `Response` object with:
            - the file content as the response body
            - the appropriate `media_type` (``text/csv`` or
              ``application/vnd.openxmlformats-officedocument.spreadsheetml.sheet``)
            - a ``Content-Disposition`` header set to ``attachment`` with the generated filename

    Raises:
        HTTPException:
            - 400 if `file_type` is not ``"csv"`` or ``"xlsx"`` or ``"docx"``.
            - Any exception raised by `func` is **not** caught here;
              it will be handled by the caller (e.g., by the `@handle_exceptions` decorator).

    Example:
        >>> @router.get("/export")
        ... async def export_data(
        ...     user_patent: UserPatentIDPairDep,
        ...     generator: SomeGeneratorDep,
        ...     component: SomeComponentDep,
        ...     fmt: TableType = Query(TableType.XLSX),
        ... ):
        ...     return await handle_file_request(
        ...         file_type=fmt.value,
        ...         default_filename="my_report",
        ...         patent_id=str(user_patent.patent_id),
        ...         func=generator.generate_data,
        ...         func_args=(str(user_patent.patent_id), component, fmt),
        ...         # func_kwargs={}  # optional
        ...     )

    Note:
        This function does **not** build a `UserPatentIDPair` or any domain object.
        That responsibility is left to the caller, which can pass the needed values
        directly via `func_args`/`func_kwargs`. This keeps the helper completely
        generic and reusable across different contexts.
    """
    # Determine content type and file extension
    if file_type == "csv":
        content_type = "text/csv"
        extension = "csv"
    elif file_type == "xlsx":
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        extension = "xlsx"
    elif file_type == "docx":
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        extension = "docx"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Execute the provided function with the given arguments
    file_data = await func(*func_args, **(func_kwargs or {}))

    # Build the final filename and return the response
    filename = f"{default_filename}_{patent_id}.{extension}"
    return Response(
        content=file_data,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
