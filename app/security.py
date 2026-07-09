"""Security layer: API key verification, rate limiting, prompt injection detection."""
import re
import time
from collections import defaultdict
from fastapi import HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import get_settings

settings = get_settings()
limiter = Limiter(key_func=get_remote_address)

# ============================================================
# PROMPT INJECTION DETECTION
# ============================================================
INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"system:\s*",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    r"\[INST\]",
    r"\[/INST\]",
    r"new instruction:",
    r"override",
    r"you are now",
    r"you are a",
    r"act as",
    r"pretend to be",
    r"role:\s*",
    r"system prompt",
    r"developer prompt",
    r"jailbreak",
    r"bypass",
    r"ethical guidelines",
    r"content policy",
    r"filter",
    r"token:",
    r"api_key:",
    r"secret:",
    r"password:",
]

# ============================================================
# API KEY VERIFICATION
# ============================================================
def verify_api_key(api_key: str) -> bool:
    """Verify the API key against settings."""
    if not settings.api_key:
        return True  # No key set = allow all (demo mode)
    return api_key == settings.api_key


# ============================================================
# PROMPT INJECTION DETECTION
# ============================================================
def detect_injection(text: str) -> bool:
    """Detect prompt injection attempts."""
    if not text:
        return False
    
    lowered = text.lower()
    # Check for obvious injection patterns
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered, re.IGNORECASE):
            return True
    
    # Check for excessive length (potential buffer overflow)
    if len(text) > 4000:
        return True
    
    # Check for unusual character sequences
    if re.search(r'(.)\1{50,}', text):  # 50+ repeated characters
        return True
    
    return False


# ============================================================
# API KEY DEPENDENCY (FastAPI)
# ============================================================
async def api_key_dependency(request: Request):
    """Dependency for FastAPI routes requiring API key."""
    # In our implementation, API key is passed in body
    # This is just a placeholder for future middleware
    pass


# ============================================================
# RATE LIMITING (In-Memory)
# ============================================================
_request_log: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_PER_MINUTE = 20
RATE_LIMIT_WINDOW = 60  # seconds


def check_rate_limit(client_ip: str) -> bool:
    """Check if client is rate limited."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    _request_log[client_ip] = [t for t in _request_log[client_ip] if t > window_start]
    
    if len(_request_log[client_ip]) >= RATE_LIMIT_PER_MINUTE:
        return False
    
    _request_log[client_ip].append(now)
    return True


# ============================================================
# REQUEST VALIDATION
# ============================================================
def validate_query(query: str) -> bool:
    """Validate query for security."""
    if not query or len(query.strip()) == 0:
        return False
    if len(query) > 4000:
        return False
    if detect_injection(query):
        return False
    return True


def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ============================================================
# SECURITY MIDDLEWARE (Optional)
# ============================================================
async def security_middleware(request: Request, call_next):
    """Middleware for security checks."""
    # Rate limiting
    client_ip = get_client_ip(request)
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again in a minute."
        )
    
    response = await call_next(request)
    return response


# ============================================================
# HEADERS FOR RESPONSE
# ============================================================
def get_security_headers():
    """Return security headers for responses."""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
    }