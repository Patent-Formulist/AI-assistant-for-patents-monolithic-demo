from dataclasses import dataclass

from fastapi import Request


@dataclass(frozen=True)
class ClientInfo:
    ip_address: str | None
    user_agent: str | None


def get_client_info(request: Request) -> ClientInfo:
    # nginx puts the client address into X-Real-IP; the backend is reachable only through it
    ip_address = request.headers.get("x-real-ip") or (
        request.client.host if request.client else None
    )
    return ClientInfo(ip_address=ip_address, user_agent=request.headers.get("user-agent"))
