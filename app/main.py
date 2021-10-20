from app.api_views.hello import *


# API Versioning for FastAPI application
from fastapi_versioning import VersionedFastAPI
app = VersionedFastAPI(
    app, version_format='{major}.{minor}',
    prefix_format='/v{major}.{minor}'
)
