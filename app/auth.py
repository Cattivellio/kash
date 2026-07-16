from __future__ import annotations

from typing import Optional

from fastapi import Cookie, HTTPException, Request
from itsdangerous import BadSignature, Signer

from .config import SESSION_MAX_AGE, SESSION_SECRET
from .database import get_user_by_id

_signer: Optional[Signer] = None


def _get_signer() -> Signer:
    global _signer
    if _signer is None:
        _signer = Signer(SESSION_SECRET)
    return _signer


def sign_user_id(user_id: int) -> str:
    return _get_signer().sign(str(user_id))


def unsign_user_id(token: str) -> Optional[int]:
    try:
        raw = _get_signer().unsign(token)
        return int(raw)
    except (BadSignature, ValueError):
        return None


def set_session_cookie(response, user_id: int) -> None:
    signed = sign_user_id(user_id)
    response.set_cookie(
        key="session",
        value=signed,
        max_age=SESSION_MAX_AGE,
        path="/",
        httponly=True,
        samesite="lax",
        secure=False,  # set True behind TLS proxy
    )


def clear_session_cookie(response) -> None:
    response.delete_cookie(key="session", path="/")


async def current_user(request: Request):
    from fastapi.responses import RedirectResponse

    session_cookie: Optional[str] = request.cookies.get("session")
    if not session_cookie:
        return RedirectResponse(url="/onboarding", status_code=303)

    user_id = unsign_user_id(session_cookie)
    if user_id is None:
        return RedirectResponse(url="/onboarding", status_code=303)

    user = get_user_by_id(user_id)
    if user is None:
        return RedirectResponse(url="/onboarding", status_code=303)

    return user
