from fastapi import FastAPI
from comment_service.core import get_database, get_redis_cache
from comment_service.db.redis_cache.redis_cache_helper import RedisCacheHelper

db = get_database()
redis_cache = RedisCacheHelper(get_redis_cache())


def get_application() -> FastAPI:
    app = FastAPI()

    add_event_handlers(app)
    return app


def add_event_handlers(app: FastAPI) -> None:
    # need this to avoid circular imports
    from comment_service.events import startup_events, shutdown_events

    app.add_event_handler("startup", startup_events())
    app.add_event_handler("shutdown", shutdown_events())


app = get_application()
