import logging

from fastapi import FastAPI
from comment_service.core import get_database, get_redis_cache


db = get_database()
redis_cache = get_redis_cache()

logger = logging.getLogger(__name__)


def get_application() -> FastAPI:
    from comment_service.api.comments import router as comment_router
    app = FastAPI()

    app.logger = logger
    app.include_router(comment_router)
    return app

app = get_application()

from comment_service.events import startup_events, shutdown_events
