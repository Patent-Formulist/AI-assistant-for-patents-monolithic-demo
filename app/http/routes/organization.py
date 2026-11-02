from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response

from app.http.request_models.organization import (
    InvitationRequest,
    MonthlyLimitRequest,
    OrganizationRequest,
    OwnerRequest,
    RoleRequest,
)
from app.http.response_models.organization import (
    InvitationResponse,
    MemberResponse,
    OrganizationResponse,
)
from app.service.organization.organization import OrganizationService
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.auth import CurrentUserId
from core.dependencies.organization import get_organization_service

router = APIRouter(prefix="/api/v2/organizations", tags=["Organizations"])
OrganizationServiceDep = Annotated[OrganizationService, Depends(get_organization_service)]
OrganizationId = Annotated[int, Path()]


# ---------- Invitations of the user (before /{organization_id} routes) ----------


@auth_doc
@router.get(
    "/invitations",
    summary="Pending invitations to the user's email",
    response_model=list[InvitationResponse],
)
@handle_exceptions
async def my_invitations(
    user_id: CurrentUserId, organizations: OrganizationServiceDep
) -> list[InvitationResponse]:
    return [InvitationResponse.of(i) for i in await organizations.my_invitations(user_id)]


@auth_doc
@router.post(
    "/invitations/{invitation_id}/accept",
    summary="Accept an invitation: join the organization",
    response_model=OrganizationResponse,
)
@handle_exceptions
async def accept_invitation(
    user_id: CurrentUserId,
    organizations: OrganizationServiceDep,
    invitation_id: Annotated[int, Path()],
) -> OrganizationResponse:
    return OrganizationResponse.of(await organizations.answer(user_id, invitation_id, accept=True))


@auth_doc
@router.post(
    "/invitations/{invitation_id}/decline", summary="Decline an invitation", status_code=204
)
@handle_exceptions
async def decline_invitation(
    user_id: CurrentUserId,
    organizations: OrganizationServiceDep,
    invitation_id: Annotated[int, Path()],
) -> Response:
    await organizations.answer(user_id, invitation_id, accept=False)
    return Response(status_code=204)


# ---------- Organizations ----------


@auth_doc
@router.post(
    "",
    summary="Create an organization; the user becomes its owner",
    status_code=201,
    response_model=OrganizationResponse,
)
@handle_exceptions
async def create_organization(
    user_id: CurrentUserId, request: OrganizationRequest, organizations: OrganizationServiceDep
) -> OrganizationResponse:
    return OrganizationResponse.of(await organizations.create(user_id, request.name))


@auth_doc
@router.get("", summary="Organizations of the user", response_model=list[OrganizationResponse])
@handle_exceptions
async def list_organizations(
    user_id: CurrentUserId, organizations: OrganizationServiceDep
) -> list[OrganizationResponse]:
    return [OrganizationResponse.of(o) for o in await organizations.for_user(user_id)]


@auth_doc
@router.get(
    "/{organization_id}", summary="Organization of the user", response_model=OrganizationResponse
)
@handle_exceptions
async def get_organization(
    user_id: CurrentUserId, organizations: OrganizationServiceDep, organization_id: OrganizationId
) -> OrganizationResponse:
    return OrganizationResponse.of(await organizations.get(user_id, organization_id))


@auth_doc
@router.patch(
    "/{organization_id}", summary="Rename (owner, admins)", response_model=OrganizationResponse
)
@handle_exceptions
async def rename_organization(
    user_id: CurrentUserId,
    request: OrganizationRequest,
    organizations: OrganizationServiceDep,
    organization_id: OrganizationId,
) -> OrganizationResponse:
    return OrganizationResponse.of(
        await organizations.rename(user_id, organization_id, request.name)
    )


@auth_doc
@router.delete("/{organization_id}", summary="Delete (owner)", status_code=204)
@handle_exceptions
async def delete_organization(
    user_id: CurrentUserId, organizations: OrganizationServiceDep, organization_id: OrganizationId
) -> Response:
    await organizations.delete(user_id, organization_id)
    return Response(status_code=204)


# ---------- Members ----------


@auth_doc
@router.get("/{organization_id}/members", summary="Members", response_model=list[MemberResponse])
@handle_exceptions
async def list_members(
    user_id: CurrentUserId, organizations: OrganizationServiceDep, organization_id: OrganizationId
) -> list[MemberResponse]:
    return [MemberResponse.of(m) for m in await organizations.members(user_id, organization_id)]


@auth_doc
@router.patch(
    "/{organization_id}/members/{member_id}",
    summary="Change a member's role (owner)",
    response_model=MemberResponse,
)
@handle_exceptions
async def change_role(
    user_id: CurrentUserId,
    request: RoleRequest,
    organizations: OrganizationServiceDep,
    organization_id: OrganizationId,
    member_id: Annotated[int, Path()],
) -> MemberResponse:
    return MemberResponse.of(
        await organizations.change_role(user_id, organization_id, member_id, request.role)
    )


@auth_doc
@router.put(
    "/{organization_id}/members/{member_id}/limit",
    summary="Monthly spending limit of a member (owner; admins for members)",
    response_model=MemberResponse,
)
@handle_exceptions
async def set_monthly_limit(
    user_id: CurrentUserId,
    request: MonthlyLimitRequest,
    organizations: OrganizationServiceDep,
    organization_id: OrganizationId,
    member_id: Annotated[int, Path()],
) -> MemberResponse:
    return MemberResponse.of(
        await organizations.set_monthly_limit(
            user_id, organization_id, member_id, request.monthly_limit
        )
    )


@auth_doc
@router.put(
    "/{organization_id}/owner",
    summary="Hand the organization to a member (owner); the old owner stays as an admin",
    response_model=list[MemberResponse],
)
@handle_exceptions
async def transfer_ownership(
    user_id: CurrentUserId,
    request: OwnerRequest,
    organizations: OrganizationServiceDep,
    organization_id: OrganizationId,
) -> list[MemberResponse]:
    return [
        MemberResponse.of(m)
        for m in await organizations.transfer_ownership(user_id, organization_id, request.user_id)
    ]


@auth_doc
@router.delete(
    "/{organization_id}/members/{member_id}",
    summary="Remove a member, or leave with your own id",
    status_code=204,
)
@handle_exceptions
async def remove_member(
    user_id: CurrentUserId,
    organizations: OrganizationServiceDep,
    organization_id: OrganizationId,
    member_id: Annotated[int, Path()],
) -> Response:
    await organizations.remove(user_id, organization_id, member_id)
    return Response(status_code=204)


# ---------- Invitations of an organization ----------


@auth_doc
@router.post(
    "/{organization_id}/invitations",
    summary="Invite by email (owner, admins; admins only invite members)",
    status_code=201,
    response_model=InvitationResponse,
)
@handle_exceptions
async def invite(
    user_id: CurrentUserId,
    request: InvitationRequest,
    organizations: OrganizationServiceDep,
    organization_id: OrganizationId,
) -> InvitationResponse:
    return InvitationResponse.of(
        await organizations.invite(user_id, organization_id, str(request.email), request.role)
    )


@auth_doc
@router.get(
    "/{organization_id}/invitations",
    summary="Pending invitations (owner, admins)",
    response_model=list[InvitationResponse],
)
@handle_exceptions
async def organization_invitations(
    user_id: CurrentUserId, organizations: OrganizationServiceDep, organization_id: OrganizationId
) -> list[InvitationResponse]:
    return [
        InvitationResponse.of(i)
        for i in await organizations.organization_invitations(user_id, organization_id)
    ]


@auth_doc
@router.delete(
    "/{organization_id}/invitations/{invitation_id}",
    summary="Revoke an invitation (owner, admins)",
    status_code=204,
)
@handle_exceptions
async def revoke_invitation(
    user_id: CurrentUserId,
    organizations: OrganizationServiceDep,
    organization_id: OrganizationId,
    invitation_id: Annotated[int, Path()],
) -> Response:
    await organizations.revoke(user_id, organization_id, invitation_id)
    return Response(status_code=204)
