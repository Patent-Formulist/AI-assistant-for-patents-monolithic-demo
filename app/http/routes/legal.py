from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.http.request_models.legal import ConsentRequest
from app.http.response_models.legal import (
    ConsentResponse,
    ConsentStatusResponse,
    LegalDocumentResponse,
    LegalDocumentSummaryResponse,
)
from app.service.legal.legal import LegalService
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.auth import CurrentUserId
from core.dependencies.client import ClientInfo, get_client_info
from core.dependencies.legal import get_legal_service

router = APIRouter(prefix="/api/v2/legal", tags=["Legal"])
LegalServiceDep = Annotated[LegalService, Depends(get_legal_service)]


@router.get(
    "/documents",
    summary="Current versions of the published documents",
    response_model=list[LegalDocumentSummaryResponse],
)
@handle_exceptions
async def list_documents(legal: LegalServiceDep) -> list[LegalDocumentSummaryResponse]:
    return [
        LegalDocumentSummaryResponse(
            document=d.document,
            version=d.version,
            title=d.title,
            requires_consent=d.requires_consent,
        )
        for d in legal.current()
    ]


@router.get(
    "/documents/{document}",
    summary="Current version of a document (Markdown)",
    response_model=LegalDocumentResponse,
)
@handle_exceptions
async def get_document(
    legal: LegalServiceDep, document: Annotated[str, Path()]
) -> LegalDocumentResponse:
    return LegalDocumentResponse.of(legal.document(document))


@router.get(
    "/documents/{document}/{version}",
    summary="A published version of a document",
    response_model=LegalDocumentResponse,
)
@handle_exceptions
async def get_document_version(
    legal: LegalServiceDep,
    document: Annotated[str, Path()],
    version: Annotated[str, Path()],
) -> LegalDocumentResponse:
    return LegalDocumentResponse.of(legal.document(document, version))


@auth_doc
@router.get(
    "/consents",
    summary="The user's consents: which current versions are accepted",
    response_model=list[ConsentResponse],
)
@handle_exceptions
async def get_consents(user_id: CurrentUserId, legal: LegalServiceDep) -> list[ConsentResponse]:
    return [ConsentResponse.of(s) for s in await legal.consents(user_id)]


@auth_doc
@router.post(
    "/consents",
    summary="Accept the current version of a document",
    status_code=201,
    response_model=ConsentResponse,
)
@handle_exceptions
async def accept(
    user_id: CurrentUserId,
    request: ConsentRequest,
    client: Annotated[ClientInfo, Depends(get_client_info)],
    legal: LegalServiceDep,
) -> ConsentResponse:
    return ConsentResponse.of(
        await legal.accept(
            user_id,
            request.document,
            request.version,
            request.choices,
            client.ip_address,
            client.user_agent,
        )
    )


@auth_doc
@router.get(
    "/consents/status",
    summary="Has the user accepted the current editions of all required documents",
    response_model=ConsentStatusResponse,
)
@handle_exceptions
async def consent_status(user_id: CurrentUserId, legal: LegalServiceDep) -> ConsentStatusResponse:
    missing = await legal.missing(user_id)
    return ConsentStatusResponse(
        all_accepted=not missing, missing=[ConsentResponse.of(s) for s in missing]
    )
