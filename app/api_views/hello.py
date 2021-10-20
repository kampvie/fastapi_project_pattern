from typing import Optional

from fastapi import status, Query
from fastapi.responses import JSONResponse
from fastapi_versioning import version
from configs.settings import app


@app.get(path='/hello', tags=['greet'])
@version(1, 0)
async def hello(greeting: Optional[str] = Query(default='Hello world')):
    return JSONResponse(content={'status': greeting + ' Version 1.0'}, status_code=status.HTTP_200_OK)


@app.get(path='/hello', tags=['greet'])
@version(1, 1)
async def hello(greeting: Optional[str] = Query(default='Hello world')):
    return JSONResponse(content={'status': greeting + ' Version 1.1'}, status_code=status.HTTP_200_OK)
