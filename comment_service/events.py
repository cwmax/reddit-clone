import os
from typing import Callable
from asyncio import sleep

from comment_service.main import db, app


async def connect_to_db(db_connect_callable: Callable):
    retry_counter = 0
    while retry_counter < os.environ.get('DB_STARTUP_MAX_CONNECTION_RETRIES', 3):
        try:
            await db_connect_callable()
        except Exception as e:
            retry_counter += 1
            await sleep(os.environ.get('DB_STARTUP_CONNECTION_TIMEOUT', 2))
    raise e


async def disconnect_db(db_disconnect_callable: Callable):
    retry_counter = 0
    while retry_counter < os.environ.get('DB_SHUTDOWN_MAX_CONNECTION_RETRIES', 3):
        try:
            await db_disconnect_callable()
        except Exception as e:
            retry_counter += 1
            await sleep(os.environ.get('DB_SHUTDOWN_CONNECTION_TIMEOUT', 2))
    raise e


@app.on_event("startup")
async def startup_events():
    await db.connect()
    # await connect_to_db(db.connect)


@app.on_event("shutdown")
async def shutdown_events():
    await db.disconnect()
    # await disconnect_db(db.disconnect)
