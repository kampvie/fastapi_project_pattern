import os
from fastapi import FastAPI
from pymongo import MongoClient
from sqlalchemy import create_engine

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

# Database name to use it as MONGO_CLIENT[f'{DB_NAME}']
DB_NAME = os.environ.get('MONGO_DATABASE_NAME')

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

# Establishing Connectivity with SQL Database
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

SQL_ENGINE = None

if all([POSTGRES_USER, POSTGRES_DB, POSTGRES_PASSWORD]):
    SQL_ENGINE = create_engine(
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
