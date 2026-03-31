"""Auth endpoints — /api/v1/auth."""

import math
import time
from collections import defaultdict
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from app.core.rate_limit import limiter
from slowapi.util import get_remote_address

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.core.token_blacklist import TokenBlacklist
from app.dependencies import get_auth_service, get_current_user, get_token_blacklist, get_user_repository
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService

router = APIRouter()
audit_log = __import__("structlog").get_logger("audit")

# ── Progressive login throttle (Apple-style) ──
# Delays: 0, 1s, 5s, 15s, 30s, 60s, 120s, 300s, 600s
_login_failures: dict[str, list[float]] = defaultdict(
    lambda: [0, 0.0]
)  # {ip: [count, locked_until]}
_DELAYS = [0, 1, 5, 15, 30, 60, 120, 300, 600]


def _get_delay(failures: int | float) -> int:
    idx = min(int(failures), len(_DELAYS) - 1)
    return _DELAYS[idx]


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse | JSONResponse:
    """Authenticate a user and return JWT tokens."""
    ip = get_remote_address(request)
    state = _login_failures[ip]
    now = time.monotonic()

    # Check if still locked out
    if state[1] > now:
        remaining = math.ceil(state[1] - now)
        return JSONResponse(
            status_code=429,
            content={
                "detail": f"Trop de tentatives. Réessayez dans {remaining}s.",
                "retry_after": remaining,
            },
            headers={"Retry-After": str(remaining)},
        )

    try:
        access_token, refresh_token, _user = await auth_service.login(body.username, body.password)
        # Success — reset failures for this IP
        _login_failures.pop(ip, None)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except AuthenticationError:
        # Increment failure count and set lockout
        state[0] += 1
        delay = _get_delay(state[0])
        state[1] = now + delay
        remaining = delay

        if delay > 0:
            audit_log.warning(
                "login.throttled",
                ip=ip,
                failures=state[0],
                delay=delay,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Identifiants incorrects. Réessayez dans {remaining}s.",
                    "retry_after": remaining,
                    "failures": state[0],
                },
                headers={"Retry-After": str(remaining)},
            )

        raise


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Register a new user (admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise AuthenticationError("Seul un administrateur peut créer des utilisateurs")

    user = await auth_service.register(
        username=body.username,
        email=body.email,
        password=body.password,
        role=body.role,
    )
    audit_log.info(
        "user.created",
        created_by=current_user.username,
        new_user=body.username,
        role=body.role.value,
    )
    return user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_settings),
    blacklist: TokenBlacklist = Depends(get_token_blacklist),
) -> TokenResponse:
    """Refresh tokens with rotation — old refresh token is revoked."""
    from jose import JWTError

    try:
        payload = decode_access_token(
            request.refresh_token,
            settings.get_jwt_verify_key(),
            settings.JWT_ALGORITHM,
            previous_secret_key=(
                settings.PREVIOUS_SECRET_KEY if settings.JWT_ALGORITHM == "HS256" else None
            ),
        )
        if payload.get("type") != "refresh":
            raise AuthenticationError("Token de type invalide")

        jti = payload.get("jti")
        if jti and await blacklist.is_revoked(jti):
            raise AuthenticationError("Refresh token révoqué")

        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError) as exc:
        raise AuthenticationError("Refresh token invalide ou expiré") from exc

    # Revoke old refresh token
    if jti and "exp" in payload:
        await blacklist.revoke(jti, float(payload["exp"]))

    access_token, refresh_token = await auth_service.refresh(user_id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", status_code=204)
async def logout(
    body: LogoutRequest,
    settings: Settings = Depends(get_settings),
    blacklist: TokenBlacklist = Depends(get_token_blacklist),
) -> None:
    """Revoke the refresh token on logout."""
    from jose import JWTError

    try:
        payload = decode_access_token(
            body.refresh_token,
            settings.get_jwt_verify_key(),
            settings.JWT_ALGORITHM,
            previous_secret_key=(
                settings.PREVIOUS_SECRET_KEY if settings.JWT_ALGORITHM == "HS256" else None
            ),
        )
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            await blacklist.revoke(jti, float(exp))
    except JWTError:
        pass  # Token already invalid, no action needed


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> Any:
    """Get the current authenticated user's profile."""
    return current_user


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository),
) -> Any:
    """List all users (admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise AuthenticationError("Accès réservé aux administrateurs")

    return await user_repo.get_all_users()
