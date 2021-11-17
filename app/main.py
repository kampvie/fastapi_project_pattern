import os
import subprocess
import shlex
import signal
import multiprocessing
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import schema
from typing import Any
from pydantic.fields import ModelField
from configs.settings import (
    PROJECT_SECRET_KEY, PROJECT_TITLE, PROJECT_DESCRIPTION, __VERSION__, MONGO_CLIENT)
# Starting import api views
from app.api_views.hello import *


# Ending import api views
# API Versioning for FastAPI application
from fastapi_versioning import VersionedFastAPI
app = VersionedFastAPI(
    app, version_format='{major}.{minor}',
    prefix_format='/v{major}.{minor}',
    enable_latest=True
)


def start_celery_beat():
    # Starting celery schedule
    if not os.path.exists("./logs"):
        os.mkdir("./logs")
    if os.path.exists("./celerybeat-schedule"):
        os.remove("./celerybeat-schedule")
    celery_logs = open("logs/celery_tasks.log", "w", encoding="utf8")
    cmd_start_celery_schedule = 'celery -A app.tasks.celery worker -E -l info -B'
    started_celery_schedule = subprocess.Popen(
        shlex.split(cmd_start_celery_schedule),
        universal_newlines=True, stdout=celery_logs
    )
    started_celery_schedule.communicate()


@app.on_event('startup')
async def startup():
    start_celery_beat_pc = multiprocessing.Process(target=start_celery_beat)
    start_celery_beat_pc.start()
    # Save pid for later shutdown action
    MONGO_CLIENT['celery']['pid'].update_one({'start_celery_beat_pc': True}, {
                                             '$set': {'pid': start_celery_beat_pc.pid}}, upsert=True)


@app.on_event('shutdown')
async def shutdown():
    pid = MONGO_CLIENT['celery']['pid'].find_one(
        {'start_celery_beat_pc': True}, {'pid': 1}).get('pid')
    os.kill(pid, signal.SIGTERM)


def custom_openapi():
    openapi_schema = get_openapi(
        title=PROJECT_TITLE,
        description=PROJECT_DESCRIPTION,
        version=__VERSION__,
        routes=app.routes
    )
    openapi_schema['info']['x-logo'] = {
        'url': '{{PROJECT_LOGO_URL}}'
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Provide which origins should be accepted to call apis
origins = [
    'http://localhost',
    'http://127.0.0.1',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    # Using session in request like
    # from fastapi.requests import Request
    # @app.get(...)
    # async def api_function(request: Resquest):
    #       request.sesssion['key'] = value
    SessionMiddleware, secret_key=PROJECT_SECRET_KEY
)

# Make custom field_schema to
# Exclude some field out of model when generating schema


def field_schema(field: ModelField, **kwargs: Any) -> Any:
    if field.field_info.extra.get("hidden_from_schema", False):
        raise schema.SkipField(f"{field.name} field is being hidden")
    else:
        return original_field_schema(field, **kwargs)


original_field_schema = schema.field_schema
schema.field_schema = field_schema
