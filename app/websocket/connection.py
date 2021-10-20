# TODO
# This file is incomplete need to be solution at scale while other connections on different host
# It's could be solve by using an database to store websocket connection under object type
# Corresponding to an uuid with only one connection
import logging
import uuid
from typing import Dict, Union

import requests
from fastapi import status, WebSocket, Path, Query
from starlette.websockets import WebSocketDisconnect

from configs.settings import app

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(module)s:%(lineno)d:%(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Create a connection list contains all all connection to specific endpoint
# Dictionary which have key as user_id, and value is websocket connection instance
GROUPS_ACTIVE_CONNECTION: Dict[Union[int, str], WebSocket] = {}
SYSTEM_ACTIVE_CONNECTION: Dict[Union[int, str], WebSocket] = {}


# TODO fix with rethink DB for horizontal scaling purpose

@app.websocket(path='/ws/group')
async def group_establish_connection(
        web_socket: WebSocket,
        user_id: Union[int, str] = Query(..., description='Use with access_token param for authentication purpose'),
        access_token: str = Query(..., description='Use for authentication purpose')
):
    global GROUPS_ACTIVE_CONNECTION
    # Checking if authentication success before accepting connection
    AUTHENTICATION_ENDPOINT = ''
    data = {
        'user_id': user_id,
        'access_token': access_token
    }
    response = requests.post(AUTHENTICATION_ENDPOINT, data=data)
    if response.status_code == status.HTTP_200_OK:
        conn_id = uuid.uuid4()
        await web_socket.send_json(
            {
                'conn_id': str(conn_id),
                'state': 'Connected'
            }
        )
        GROUPS_ACTIVE_CONNECTION[f'{conn_id}'] = web_socket
        try:
            json: Dict = await web_socket.receive_json()
            await web_socket.send_json(json)
        except WebSocketDisconnect:
            try:
                del GROUPS_ACTIVE_CONNECTION[f'{conn_id}']
                logger.info(f'Removed connection {conn_id}')
            except KeyError:
                logger.warning(f'{conn_id} does not exist to delete')
    await web_socket.close()


@app.websocket(path='/ws/system')
async def system_establish_connection(
        web_socket: WebSocket,
        user_id: Union[int, str] = Query(..., description='Use with access_token param for authentication purpose'),
        access_token: str = Query(..., description='Use for authentication purpose')
):
    global SYSTEM_ACTIVE_CONNECTION
    # Checking if authentication success before accepting connection
    AUTHENTICATION_ENDPOINT = ''
    data = {
        'user_id': user_id,
        'access_token': access_token
    }
    response = requests.post(AUTHENTICATION_ENDPOINT, data=data)
    if response.status_code == status.HTTP_200_OK:
        conn_id = uuid.uuid4()
        await web_socket.send_json(
            {
                'conn_id': str(conn_id),
                'state': 'Connected'
            }
        )
        SYSTEM_ACTIVE_CONNECTION[f'{conn_id}'] = web_socket
        try:
            json: Dict = await web_socket.receive_json()
            await web_socket.send_json(json)
        except WebSocketDisconnect:
            try:
                del SYSTEM_ACTIVE_CONNECTION[f'{conn_id}']
                logger.info(f'Removed connection {conn_id}')
            except KeyError:
                logger.warning(f'{conn_id} does not exist to delete')
    await web_socket.close()
