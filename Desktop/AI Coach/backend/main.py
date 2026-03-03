import redis.asyncio as aioredis
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logger import get_logger
from app.middleware.logging import RequestLoggingMiddleware
from app.utils.response import error_response
from app.api import auth, users, health, dashboard, tasks, habits, study_sessions, productivity, ai_coach

log = get_logger(__name__)


# ─── Startup / Shutdown ───────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — Redis/rate-limiting is optional (degrades gracefully in dev)
    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2,
        )
        await redis_client.ping()  # fail fast if Redis isn't reachable
        await FastAPILimiter.init(redis_client)
        log.info("Rate limiter initialized with Redis: {url}", url=settings.REDIS_URL)
    except Exception as e:
        log.warning(
            "Redis not available — rate limiting disabled. Start Redis to enable it. ({error})",
            error=str(e),
        )

    log.info("AI Student Dashboard API starting up…")
    yield

    # Shutdown
    log.info("AI Student Dashboard API shutting down…")


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Student Dashboard API",
    description="Backend API for the AI Student Dashboard — productivity tracking, habit management, and AI coaching for students.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── Middleware (order matters — outermost first) ─────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)


# ─── Global Error Handlers ────────────────────────────────────────────────────
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    log.warning(
        "HTTP {status_code} — {detail} [{method} {path}]",
        status_code=exc.status_code,
        detail=exc.detail,
        method=request.method,
        path=request.url.path,
    )
    return error_response(str(exc.detail), exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    message = "; ".join(
        f"{' → '.join(str(loc) for loc in e['loc'])}: {e['msg']}" for e in errors
    )
    log.warning(
        "Validation error [{method} {path}]: {message}",
        method=request.method,
        path=request.url.path,
        message=message,
    )
    return error_response(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.error(
        "Unhandled server error [{method} {path}]: {error}",
        method=request.method,
        path=request.url.path,
        error=str(exc),
    )
    return error_response("An unexpected server error occurred.", status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Routers ─────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix=API_PREFIX)
app.include_router(tasks.router, prefix=API_PREFIX)
app.include_router(habits.router, prefix=API_PREFIX)
app.include_router(study_sessions.router, prefix=API_PREFIX)
app.include_router(productivity.router, prefix=API_PREFIX)
app.include_router(ai_coach.router, prefix=API_PREFIX)


# ─── Root ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": "AI Student Dashboard API", "docs": "/docs"}
