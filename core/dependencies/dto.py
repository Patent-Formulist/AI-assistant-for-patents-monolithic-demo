"""Ids from the request, checked against the user (PatentAccess).

Every route that takes a patent, analog or job id gets it through these
dependencies, so no route can forget the ownership check: a foreign or
missing id answers 404 before the route runs.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Path

from app.http.request_models.patent import PatentIdRequest
from app.service.access import PatentAccess
from core.dependencies.access import get_patent_access
from core.dependencies.auth import CurrentUserId
from core.domain.user_analog import UserAnalogIDPair
from core.domain.user_patent import UserPatentIDPair

PatentAccessDep = Annotated[PatentAccess, Depends(get_patent_access)]


def _id(value: str) -> int:
    try:
        return int(value)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid format: {str(e)}") from e


async def get_user_patent_id_pair_header(
    user_id: CurrentUserId,
    patent_uuid: Annotated[str, Path()],
    access: PatentAccessDep,
) -> UserPatentIDPair:
    patent_id = _id(patent_uuid)
    await access.patent(user_id, patent_id)
    return UserPatentIDPair(user_id=user_id, patent_id=patent_id)


async def get_user_patent_id_pair_body(
    user_id: CurrentUserId,
    patent_uuid: PatentIdRequest,
    access: PatentAccessDep,
) -> UserPatentIDPair:
    patent_id = _id(patent_uuid.patent_id)
    await access.patent(user_id, patent_id)
    return UserPatentIDPair(user_id=user_id, patent_id=patent_id)


async def get_user_analog_id_pair(
    user_id: CurrentUserId,
    analog_uuid: Annotated[str, Path()],
    access: PatentAccessDep,
) -> UserAnalogIDPair:
    analog_id = _id(analog_uuid)
    await access.analog(user_id, analog_id)
    return UserAnalogIDPair(user_id=user_id, analog_id=analog_id)


async def get_user_job_id(
    user_id: CurrentUserId,
    job_id: Annotated[int, Path()],
    access: PatentAccessDep,
) -> int:
    await access.job(user_id, job_id)
    return job_id


async def get_patent_analog_id(
    user_patent: Annotated[UserPatentIDPair, Depends(get_user_patent_id_pair_header)],
    analog_uuid: Annotated[int, Path()],
    access: PatentAccessDep,
) -> int:
    """An analog id from the path that must belong to the (checked) patent in the path."""
    await access.analog_of_patent(user_patent.patent_id, analog_uuid)
    return analog_uuid
