"""Auth endpoints — /api/v1/auth."""

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.dependencies import get_auth_service, get_current_user, get_user_repository
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
audit_log = __import__("structlog").get_logger("audit")


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticate a user and return JWT tokens."""
    access_token, refresh_token, _user = await auth_service.login(body.username, body.password)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/register", response_model=UserResponse)
@limiter.limit("3/minute")
async def register(
    request: Request,
    body: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
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
):
    """Refresh the access token using a refresh token."""
    from jose import JWTError

    try:
        payload = decode_access_token(
            request.refresh_token, settings.SECRET_KEY, settings.JWT_ALGORITHM
        )
        if payload.get("type") != "refresh":
            raise AuthenticationError("Token de type invalide")
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError) as exc:
        raise AuthenticationError("Refresh token invalide ou expiré") from exc

    access_token, refresh_token = await auth_service.refresh(user_id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return current_user


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """List all users (admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise AuthenticationError("Accès réservé aux administrateurs")

    return await user_repo.get_all_users()
