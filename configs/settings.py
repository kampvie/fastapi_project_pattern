import os
import subprocess
import shlex

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from pymongo import MongoClient
from pydantic import schema
from typing import Any
from pydantic.fields import ModelField

from configs.tags_metadata import TAGS_METADATA

PROJECT_SECRET_KEY = "{{PROJECT_SECRET_KEY}}"

DEBUG = os.environ.get('DEBUG', 0)

PROJECT_TITLE = "{{PROJECT_TITLE}}"
PROJECT_DESCRIPTION = "{{PROJECT_DESCRIPTION}}"
__VERSION__ = '1.0'

# Initial FastAPI app
app = FastAPI(
    debug=bool(DEBUG),
    title=PROJECT_TITLE,
    docs_url=None,
    redoc_url=None
)


@app.get(path='/docs', include_in_schema=False)
async def overridden_swagger():
    return get_swagger_ui_html(openapi_url='/openapi.json', title=PROJECT_TITLE, swagger_favicon_url='')


@app.get(path='/redoc', include_in_schema=False)
async def overridden_redoc():
    return get_redoc_html(openapi_url='/openapi.json', title=PROJECT_TITLE, redoc_favicon_url='')


def custom_openapi():
    openapi_schema = get_openapi(
        title=PROJECT_TITLE,
        description=PROJECT_DESCRIPTION,
        version=__VERSION__,
        tags=TAGS_METADATA,
        routes=app.routes
    )
    openapi_schema['info']['x-logo'] = {
        'url': ''
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

# Get DB host from docker-compose environment
DB_HOST = os.environ.get('DB_HOST')

DB_PORT = os.environ.get('DB_PORT')

RABBITMQ = os.environ.get('RABBITMQ')

CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

REMOTE_MONGO_URL = os.environ.get('REMOTE_MONGO_URL')

MONGO_INITDB_ROOT_USERNAME = os.environ.get('MONGO_INITDB_ROOT_USERNAME')

MONGO_INITDB_ROOT_PASSWORD = os.environ.get('MONGO_INITDB_ROOT_PASSWORD')

REMOTE_POSTGRES_URL = os.environ.get('REMOTE_POSTGRES_URL')

RABBITMQ_DEFAULT_USER = os.environ.get('RABBITMQ_DEFAULT_USER')

RABBITMQ_DEFAULT_PASS = os.environ.get('RABBITMQ_DEFAULT_PASS')

CELERY_APP_NAME = 'app'

MONGO_CLIENT = None

DB_NAME = os.environ.get('MONGO_DATABASE_NAME')  # Database name to use it as MONGO_CLIENT[f'{DB_NAME}']

if all([DB_HOST, DB_PORT]):
    # initial connection to database
    MONGO_CLIENT = MongoClient(
        f'mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{DB_HOST}:{DB_PORT}/?authMechanism=SCRAM-SHA-256')
    # Create schedule db for storing result backend
    if not MONGO_CLIENT['celery'].command('usersInfo', usersInfo={"user": MONGO_INITDB_ROOT_USERNAME, "db": "celery"}).get('users'):
        MONGO_CLIENT['celery'].command(
            'createUser',
            createUser=MONGO_INITDB_ROOT_USERNAME,
            pwd=MONGO_INITDB_ROOT_PASSWORD,
            roles=["readWrite", "dbAdmin"],
            mechanisms=["SCRAM-SHA-256"],
        )

if REMOTE_MONGO_URL and REMOTE_MONGO_URL != "None":
    # Switch back to remote mongo database service
    MONGO_CLIENT = MongoClient(REMOTE_MONGO_URL)

# Setting up events
started_celery_schedule = None


@app.on_event('startup')
async def startup():
    # Starting celery schedule
    if not os.path.exists("./logs"):
        os.mkdir("./logs")
    celery_logs = open("logs/celery_tasks.log", "w", encoding="utf8")
    cmd_start_celery_schedule = 'celery -A app.tasks.celery worker -E -l info -B'
    started_celery_schedule = subprocess.Popen(
        shlex.split(cmd_start_celery_schedule),
        universal_newlines=True, stdout=celery_logs
    )
    started_celery_schedule.communicate()


@app.on_event('shutdown')
async def shutdown():
    if started_celery_schedule:
        started_celery_schedule.kill()
