import socket
import uuid
import json
import os
import logging
import hmac
import bcrypt  # Direct bcrypt usage for robustness
from pathlib import Path
from core.config import settings
from backend.services.cache_manager import cache_manager

# Configure logger for this module
logger = logging.getLogger(__name__)

# JWT configuration
from jose import jwt, JWTError
from datetime import datetime, timedelta


class SecurityEngine:
    # JWT configuration
    # In production, SECRET_KEY must be set via environment variable.
    # For dev/test, a random key is generated per-process (tokens won't
    # survive restarts — which is the intended security behavior).
    _secret_key = os.getenv("SECRET_KEY")
    if not _secret_key:
        import warnings
        warnings.warn(
            "SECRET_KEY not set. Generating random key for this session. "
            "Tokens will be invalidated on restart. "
            "Set SECRET_KEY env var for production use.",
            RuntimeWarning
        )
        _secret_key = os.urandom(32).hex()

    SECRET_KEY = _secret_key
    ALGORITHM = os.getenv("JWT_ALGORITHM") or "HS256"
    # Reduced from 30 days to 24 hours for better security
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 1440
    )  # 24 Hours default

    # In-memory Token Blocklist (for ASVS V7.4.1 Session Revocation)
    _token_blocklist = set()

    @classmethod
    def revoke_token(cls, jti: str):
        """Adds a JWT ID to the distributed blocklist (Redis) with local fallback."""
        if jti:
            cls._token_blocklist.add(jti)
            try:
                # TTL is token expiration time in seconds to automatically clean up Redis
                cache_manager.set(f"revoked_jti:{jti}", "1", ex=cls.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
            except Exception as e:
                logger.error(f"Redis fallback: failed to add token {jti} to blocklist: {e}")

    # ASVS V6.1.1 & V6.3.1: Brute Force & Credential Stuffing Protection
    _failed_logins = (
        {}
    )  # Format: {"ip_or_user": {"count": int, "lockout_until": datetime}}
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15

    @classmethod
    def check_rate_limit(cls, identifier: str):
        """Checks if a user/IP is currently locked out."""
        record = cls._failed_logins.get(identifier)
        if not record:
            return

        if record["count"] >= cls.MAX_FAILED_ATTEMPTS:
            if datetime.utcnow() < record["lockout_until"]:
                mins_left = int(
                    (record["lockout_until"] - datetime.utcnow()).total_seconds() / 60
                )
                raise Exception(
                    f"Account locked due to multiple failed attempts. Try again in {max(1, mins_left)} minutes."
                )
            else:
                # Lockout expired, reset
                cls.clear_login_attempts(identifier)

    @classmethod
    def record_failed_login(cls, identifier: str):
        """Records a failed login attempt for an identifier."""
        record = cls._failed_logins.get(
            identifier, {"count": 0, "lockout_until": datetime.utcnow()}
        )
        record["count"] += 1
        if record["count"] >= cls.MAX_FAILED_ATTEMPTS:
            record["lockout_until"] = datetime.utcnow() + timedelta(
                minutes=cls.LOCKOUT_DURATION_MINUTES
            )
        cls._failed_logins[identifier] = record

    @classmethod
    def clear_login_attempts(cls, identifier: str):
        """Clears failed login attempts after a successful login."""
        if identifier in cls._failed_logins:
            del cls._failed_logins[identifier]

    @staticmethod
    def find_free_port():
        """Binds to port 0 to let the OS assign a free dynamic port."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((settings.network.host, 0))
            return s.getsockname()[1]

    @staticmethod
    def generate_token():
        """Generates a high-entropy UUID4 session token."""
        return str(uuid.uuid4())

    # ---------------------
    # Password helpers (Direct Bcrypt)
    # ---------------------
    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """Hash a password using bcrypt."""
        # bcrypt expects bytes
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @classmethod
    def verify_password(cls, plain: str, hashed: str) -> bool:
        """Verify a plain password against its hash."""
        try:
            # bcrypt.checkpw expects (password_bytes, hashed_bytes)
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    # ---------------------
    # JWT helpers
    # ---------------------
    @classmethod
    def create_access_token(cls, data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        # SAAS-006 & V7.4.1: Inject a unique `jti` for revocation
        to_encode.update(
            {"exp": expire, "iat": datetime.utcnow(), "jti": str(uuid.uuid4())}
        )
        encoded = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded

    @classmethod
    def decode_token(cls, token: str) -> dict:
        """Decodes JWT and validates core SaaS claims."""
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])

            # V7.4.1: Verify token is not revoked (Distributed check)
            jti = payload.get("jti")
            if jti:
                redis_revoked = False
                try:
                    redis_revoked = bool(cache_manager.get(f"revoked_jti:{jti}"))
                except Exception as e:
                    logger.warning(f"Redis blocklist check failed, falling back to memory: {e}")
                
                if redis_revoked or jti in cls._token_blocklist:
                    raise JWTError("Token has been revoked")

            # SAAS-006: Strict validation of tenant isolation claims
            if "sub" not in payload or "instance_name" not in payload:
                logger.error(f"Token missing claims: {payload.keys()}")
                raise JWTError("Invalid token: Missing tenant identification")

            return payload
        except JWTError:
            raise

    @classmethod
    def create_session_lock(cls):
        """Creates the secure_session.json file with current port and token."""
        # Use PORT from env if provided, else fallback to settings or 8000
        port_env = os.getenv("PORT")
        if port_env:
            port = int(port_env)
        else:
            # Fallback to fixed port if no env is set, to ensure agreement with main.py
            port = settings.network.default_port or 8000

        token = cls.generate_token()

        # Ensure temp directory exists
        path = Path(settings.security.temp_dir)
        path.mkdir(parents=True, exist_ok=True)

        session_data = {"port": port, "token": token, "pid": os.getpid()}

        lock_file = path / settings.security.session_file
        with open(lock_file, "w") as f:
            json.dump(session_data, f)

        logger.info(f"Session file created at: {lock_file.absolute()}")
        logger.info(f"Session established on port {port}")
        return session_data

    @classmethod
    def cleanup_session(cls):
        """Removes the session lock file on shutdown."""
        lock_file = Path(settings.security.temp_dir) / settings.security.session_file
        if lock_file.exists():
            lock_file.unlink()
            logger.info("Session lock cleaned up.")

    @staticmethod
    def get_current_session():
        """Reads the current active session data."""
        lock_file = Path(settings.security.temp_dir) / settings.security.session_file
        if lock_file.exists():
            with open(lock_file, "r") as f:
                return json.load(f)
        return None
