import sys
from loguru import logger

# Remove default handler
logger.remove()

# ─── Console handler (colored, human-readable) ────────────────────────────────
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
)

# ─── File handler — all INFO and above ───────────────────────────────────────
logger.add(
    "logs/app.log",
    level="INFO",
    rotation="10 MB",
    retention="14 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}",
)

# ─── File handler — ERROR only ────────────────────────────────────────────────
logger.add(
    "logs/errors.log",
    level="ERROR",
    rotation="5 MB",
    retention="30 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}",
)


def get_logger(name: str):
    """Return a logger instance bound to the given module name."""
    return logger.bind(name=name)
