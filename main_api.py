import os
import time
import logging
import asyncio
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings
from core.security import SecurityEngine
from backend.database_manager import db_manager
from typing import Optional, Dict, Any
from fastapi import status
from backend.core.security_sanitizer import SecuritySanitizer
from backend.core.event_broker import event_broker  # Added by instruction


# Initialize FastAPI
# --- Unified Logging Bridge (Gap 2 Compliance) ---
class BroadcastLoggingHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            level = record.levelname
            # We use a background task to not block the logging call
            asyncio.create_task(event_broker.publish_log(msg, level=level))
        except:
            pass


# Setup broadcasting logger
logging.getLogger("g777").addHandler(BroadcastLoggingHandler())
logging.getLogger("uvicorn.error").addHandler(BroadcastLoggingHandler())

app = FastAPI(title=settings.system.app_name, version=settings.system.version)

# --- ROUTERS ---
from api.router_registry import register_all_routers

# Register all modular routers (Group Sender, Members, SaaS components, etc.)
register_all_routers(app)

# --- AUTH DEPENDENCY ---
from core.dependencies import get_current_user, _bearer_scheme


from backend.core.security_middleware import SecurityHeadersMiddleware

# Register ASVS V3/V16 Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.network.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# MIDDLEWARE: The Secure Handshake Validator
# -----------------------------------------------------------------------------
@app.middleware("http")
async def security_barrier(request: Request, call_next):
    # Allow OPTIONS and specific unauthenticated paths
    if request.method == "OPTIONS":
        return await call_next(request)

    path = request.url.path
    if path in settings.system.exempt_paths:
        return await call_next(request)

    # 1. Direct Access Mode (No Login)
    if not settings.security.auth_required:
        # Inject default admin user
        request.state.user = {
            "sub": "00000000-0000-0000-0000-000000000000",
            "user_id": "00000000-0000-0000-0000-000000000000",
            "username": "admin",
            "role": "admin",
            "instance_name": "G777_Master",
        }
        return await call_next(request)

    # 2. Strict Auth Mode
    # Expect Authorization: Bearer <token>
    auth_header: Optional[str] = request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Missing authorization header"},
        )

    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = SecurityEngine.decode_token(token)
        # make payload available to handlers
        request.state.user = payload
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or expired token"},
        )

    response = await call_next(request)
    return response


# -----------------------------------------------------------------------------
# LIFECYCLE EVENTS
# -----------------------------------------------------------------------------
from backend.core.telemetry import start_telemetry_monitoring


@app.on_event("startup")
async def startup_event():
    # Session is actually created by the launcher, but we verify here
    print(f"[*] Starting {settings.system.app_name} Backend...")

    # Clean up update leftovers
    update_root = os.path.join(os.getcwd(), ".temp_update")
    if os.path.exists(update_root):
        try:
            import shutil

            shutil.rmtree(update_root)
        except:
            pass

    # Run DB migrations (create users table) if DB manager available
    try:
        if db_manager is not None:
            db_manager.check_migrations()
    except Exception as e:
        print(f"[WARN] Could not run DB migrations on startup: {e}")

    # Start Unified Telemetry Pipeline (Gap 2)
    asyncio.create_task(start_telemetry_monitoring(interval_seconds=10))


@app.on_event("shutdown")
async def shutdown_event():
    SecurityEngine.cleanup_session()


# -----------------------------------------------------------------------------
# ENDPOINTS
# -----------------------------------------------------------------------------
@app.get("/health")
async def health_check():
    return {
        "status": "active",
        "timestamp": time.time(),
        "version": settings.system.version,
        "engine": "FASTAPI/Python 3.11",
    }


@app.get("/auth/config")
async def get_auth_config():
    """Returns the current authentication mode."""
    return {"auth_required": settings.security.auth_required}


@app.post("/auth/register")
async def register(request: Request):
    """Register a new SaaS user."""
    body = await request.json()
    username = SecuritySanitizer.sanitize_input(body.get("username"))
    password = body.get("password")  # Don't sanitize passwords to preserve complexity
    email = SecuritySanitizer.sanitize_input(body.get("email"))
    instance_name = (
        SecuritySanitizer.sanitize_input(body.get("instance_name"))
        or f"G777_{username}"
    )

    if not username or not password or not email:
        raise HTTPException(
            status_code=400, detail="Username, password, and email required"
        )

    # Check if existing
    if db_manager.get_user_by_username(username):
        raise HTTPException(status_code=409, detail="User already exists")

    # Hash Password
    pwd_hash = SecurityEngine.get_password_hash(password)

    # Insert user
    conn = db_manager.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, email, role, instance_name)
                VALUES (%s, %s, %s, 'client', %s)
                RETURNING id
                """,
                (username, pwd_hash, email, instance_name),
            )
            user_id = cursor.fetchone()[0]
            conn.commit()
            return {"status": "success", "user_id": str(user_id)}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    finally:
        db_manager.release_connection(conn)


@app.post("/auth/login")
async def login(request: Request):
    body = await request.json()
    username = SecuritySanitizer.sanitize_input(body.get("username"))
    password = body.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="username and password required")

    # V6.1.1 & V6.3.1: Rate Limiting / Anti-Brute Force mechanism
    client_ip = request.client.host if request.client else "unknown_ip"
    identifier = f"{client_ip}_{username}"

    try:
        SecurityEngine.check_rate_limit(identifier)
    except Exception as rate_limit_exc:
        raise HTTPException(status_code=429, detail=str(rate_limit_exc))

    # Lookup user
    user = None
    try:
        user = db_manager.get_user_by_username(username)
    except Exception as e:
        raise HTTPException(status_code=500, detail="user lookup failed")

    if not user:
        SecurityEngine.record_failed_login(identifier)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not SecurityEngine.verify_password(password, user.get("password_hash")):
        SecurityEngine.record_failed_login(identifier)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Security Check Passed! Clear recorded failures
    SecurityEngine.clear_login_attempts(identifier)

    # Build token payload - SAAS-006: include instance_name for WhatsApp isolation
    token_data = {
        "sub": str(user.get("id")),
        "user_id": str(user.get("id")),
        "username": user.get("username"),
        "role": user.get("role", "client"),
        "instance_name": user.get("instance_name") or f"g777_{user.get('username')}",
    }
    access_token = SecurityEngine.create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": token_data["role"],
        "instance_name": token_data["instance_name"],
    }


@app.post("/auth/logout")
async def logout(request: Request):
    """
    ASVS V7.4.1: Revokes the current session by adding token jti to blocklist.
    Requests must be authenticated.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    jti = user.get("jti")
    if jti:
        SecurityEngine.revoke_token(jti)

    return {"status": "success", "detail": "Session revoked successfully"}


@app.post("/auth/guest-login")
async def guest_login():
    """Login as Guest (Local Admin capabilities) if allowed."""
    if not settings.security.allow_guest_access:
        raise HTTPException(status_code=403, detail="Guest access is disabled")

    # Create/Get Guest User
    guest_username = settings.security.guest_username
    conn = db_manager.get_connection()
    user_id = None
    try:
        with conn.cursor() as cursor:
            # Check if exists
            cursor.execute(
                "SELECT id FROM users WHERE username = %s", (guest_username,)
            )
            res = cursor.fetchone()
            if res:
                user_id = res[0]
            else:
                # Create guest user with random high-entropy password (never used)
                pwd_hash = SecurityEngine.get_password_hash(
                    f"GUEST_{time.time()}_{settings.security.guest_secret}"
                )
                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, email, role, instance_name)
                    VALUES (%s, %s, %s, 'admin', %s)
                    RETURNING id
                    """,
                    (
                        guest_username,
                        pwd_hash,
                        settings.security.guest_email,
                        settings.security.guest_instance_name,
                    ),
                )
                user_id = cursor.fetchone()[0]
                conn.commit()

            token_data = {
                "sub": str(user_id),
                "user_id": str(user_id),
                "username": guest_username,
                "role": "admin",
                "instance_name": settings.security.guest_instance_name,
            }
            access_token = SecurityEngine.create_access_token(token_data)

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "role": "admin",
                "instance_name": settings.security.guest_instance_name,
            }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Guest login failed: {str(e)}")
    finally:
        db_manager.release_connection(conn)


if __name__ == "__main__":
    import uvicorn

    # 1. Create session lock first
    session = SecurityEngine.create_session_lock()

    # 2. Start Uvicorn on the dynamic port
    uvicorn.run(
        "main_api:app",
        host=settings.network.host,
        port=session["port"],
        log_level=settings.system.log_level.lower(),
        reload=False,  # Production standard
    )
