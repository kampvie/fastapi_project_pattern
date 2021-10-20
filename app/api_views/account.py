import logging
import random
from app.utils.send_verification_email import create_account_verification, send_reset_password_email
from fastapi import status, Form, Body, Depends, Path, Query
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from pymongo import ReturnDocument
from configs.settings import DB_NAME, PROJECT_SECRET_KEY, app, MONGO_CLIENT
from secure._token import get_data_from_access_token, create_access_token, valid_access_token, is_expired
from secure._password import get_password_hash, verify_password

from models.response.account import (
    CreateAccountResponse200,
    CreateAccountResponse403,
    LoginResponse200,
    LoginResponse403,
    LoginResponse404,
    VerifyAccountResponse200,
    VerifyAccountResponse403,
    ResetPasswordResponse201,
    ResetPasswordResponse404,
    PutResetPasswordResponse200,
    PutResetPasswordResponse400,
    ChangePasswordResponse200,
    UpdatePasswordResponse200,
    UpdatePasswordResponse400,
    UpdatePasswordResponse403,
)

from models.user import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s:%(levelname)s:%(module)s:%(lineno)d:%(message)s'
)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


@app.post(path='/account', responses={
    status.HTTP_200_OK: {
        'model': CreateAccountResponse200
    },
    status.HTTP_403_FORBIDDEN: {
        'model': CreateAccountResponse403
    }
}, tags=['account'])
async def create_account(
    email: EmailStr = Form(..., description='Email'),
    username: str = Form(..., description='Username'),
    password: str = Form(..., description='Password'),
    device_id: str = Form(..., description='Device ID'),
    verification_link: str = Form(...,
                                  description='Link giao diện xác nhận tài khoản')
):
    """Tạo tài khoản hệ thống"""
    import datetime
    # Check if user already exist
    if MONGO_CLIENT[f'{DB_NAME}']['users'].find({"email": {"$eq": email}}).count():
        return JSONResponse(content={
            "status": "Lỗi",
            "msg": "Email đã tồn tại!"
        }, status_code=status.HTTP_403_FORBIDDEN)
    # Create user in db
    access_token, secret_key = create_access_token(
        data={
            'email': email,
            'username': username
        }
    )
    token = Token(
        access_token=access_token,
        token_type='Bearer',
        device_id=device_id
    )
    user = User(
        username=username,
        tokens=[token],
        secret_key=secret_key,
        email=email,
        hashed_password=get_password_hash(password),
        datetime_created=datetime.datetime.now(),
        is_verified=False
    )
    inserted_id = MONGO_CLIENT[f'{DB_NAME}']['users'].insert_one(
        jsonable_encoder(user)
    ).inserted_id
    # Send email to verify account
    # Create access token container userId and expire time for a link
    encoded_jwt, _ = create_access_token({'user_id': str(inserted_id)},
                                         expires_delta=datetime.timedelta(minutes=30), secret_key=PROJECT_SECRET_KEY)
    await create_account_verification('customer@sasamviet.com', email, data={
        'User_Name': username,
        'msg': 'Nhấn vào link hoặc nút xác nhận bên dưới để xác nhận tài khoản',
        'Verification_Link': f'{verification_link}?verifyKey={encoded_jwt}'
    })
    return JSONResponse(content={
        'status': 'Tạo tài khoản thành công',
        'access_token': access_token,
        'secret_key': secret_key,
        'device_id': device_id,
        'is_verified': False
    }, status_code=status.HTTP_200_OK)


@app.post(path='/account/login', responses={
    status.HTTP_200_OK: {
        'model': LoginResponse200
    },
    status.HTTP_403_FORBIDDEN: {
        'model': LoginResponse403
    },
    status.HTTP_404_NOT_FOUND: {
        'model': LoginResponse404
    }
}, tags=['account'])
async def login(email: EmailStr = Body(...), password: str = Body(...), device_id: str = Body(..., description='Id của thiết bị đăng nhập')):
    """Đăng nhập"""
    user = MONGO_CLIENT[f'{DB_NAME}']['users'].find_one(
        {'email': {'$eq': email}}
    )
    if not user:
        return JSONResponse(content={'status': 'Lỗi', 'msg': 'Không tồn tại!'}, status_code=status.HTTP_404_NOT_FOUND)
    if verify_password(password, user.get('hashed_password')):
        # Create new access token for device
        secret_key = user.get('secret_key')
        access_token, _ = create_access_token(
            data={
                'email': user.get('email'),
                'username': user.get('username')
            },
            secret_key=secret_key
        )
        token = Token(
            access_token=access_token,
            token_type='Bearer',
            device_id=device_id
        )
        # If device id exist we just need to update toke for only that device
        is_existed = False
        for _token in user.get('tokens'):
            if _token.get('device_id') == device_id:
                is_existed = True

        if is_existed:
            MONGO_CLIENT[f'{DB_NAME}']['users'].find_one_and_update(
                filter={
                    '$and': [
                        {'email': {'$eq': email}},
                        {'tokens.device_id': {'$eq': device_id}}
                    ]
                },
                update={
                    '$set': {'tokens.$': jsonable_encoder(token)}
                }
            )
            return JSONResponse(content={'token': jsonable_encoder(token), 'secret_key': secret_key},
                                status_code=status.HTTP_200_OK)
        else:
            if len(user.get('tokens')) >= 5:
                return JSONResponse(content={'status': 'Lỗi', 'msg': 'Đạt giới hạn 5 thiết bị đăng nhập'}, status_code=status.HTTP_403_FORBIDDEN)
            user = MONGO_CLIENT[f'{DB_NAME}']['users'].find_one_and_update(
                filter={'email': {'$eq': email}},
                update={
                    '$push': {
                        'tokens': jsonable_encoder(token)
                    }
                },
                return_document=ReturnDocument.AFTER
            )
            return JSONResponse(content={'token': jsonable_encoder(token), 'secret_key': secret_key},
                                status_code=status.HTTP_200_OK)
    return JSONResponse(content={'status': 'Lỗi', 'msg': 'Đăng nhập không thành công!'}, status_code=status.HTTP_403_FORBIDDEN)


@app.get(path='/account/verify', responses={
    status.HTTP_200_OK: {
        'model': VerifyAccountResponse200
    },
    status.HTTP_403_FORBIDDEN: {
        'model': VerifyAccountResponse403
    }
}, tags=['account'])
async def verify_account(verify_key: str = Query(..., description='Key xác nhận tài khoản được gửi kèm là verifyKey trong link xác nhận tài khoản')):
    if not is_expired(verify_key, PROJECT_SECRET_KEY):
        data = get_data_from_access_token(verify_key, PROJECT_SECRET_KEY)
        user_id = data.get('user_id')
        _id = ObjectId(user_id)
        MONGO_CLIENT[f'{DB_NAME}']['users'].find_one_and_update(
            filter={'_id': _id},
            update={'$set': {'is_verified': True}}
        )
        return JSONResponse(content={'status': 'Thành công!', 'msg': 'Đã xác nhận tài khoản!'}, status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(content={'status': 'Lỗi!', 'msg': 'Key xác nhận không hợp lệ hoặc hết thời gian'}, status_code=status.HTTP_403_FORBIDDEN)


@app.post(path='/account/password/reset', responses={
    status.HTTP_201_CREATED: {
        'model': ResetPasswordResponse201
    },
    status.HTTP_404_NOT_FOUND: {
        'model': ResetPasswordResponse404
    }
}, tags=['account'])
async def reset_password(
    email: EmailStr = Form(..., description='Email khôi phục mật khẩu'),
):
    """ 
        Khôi phục lại mật khẩu, hệ thống gửi mail kèm theo mã để khôi phục lại mật khẩu
    """
    import datetime
    import secrets
    keyonce = secrets.token_urlsafe(6)
    expire_in = datetime.datetime.now() + datetime.timedelta(minutes=30)
    expire_at_timestamp = expire_in.timestamp()
    user = MONGO_CLIENT[f'{DB_NAME}']['users'].find_one(
        filter={'email': {'$eq': email}}
    )
    if not user:
        return JSONResponse(content={'status': 'Lỗi!', 'msg': 'Tài khoản không tồn tại!'}, status_code=status.HTTP_404_NOT_FOUND)
    # Check if keyonce is not used
    await send_reset_password_email('customer@sasamviet.com', email, data={
        'msg': 'Vui lòng xác nhận địa chỉ email của bạn bằng cách nhập mã xác minh bên dưới. Mã có giá trị trong 30 phút',
        'keyonce': keyonce
    })
    MONGO_CLIENT[f'{DB_NAME}']['users'].find_one_and_update(
        filter={'email': {'$eq': email}},
        update={'$set': {'keyonce': keyonce,
                         'keyonce_expire_at': expire_at_timestamp}}
    )
    return JSONResponse(content={'status': 'Thành công!', 'msg': 'Vui lòng kiểm tra email và nhập mã!'}, status_code=status.HTTP_201_CREATED)


@app.put(path='/account/password/reset', responses={
    status.HTTP_200_OK: {
        'model': PutResetPasswordResponse200
    },
    status.HTTP_400_BAD_REQUEST: {
        'model': PutResetPasswordResponse400
    }
}, tags=['account'])
async def reset_password(
    keyonce: str = Form(..., description='Mã một lần để khôi phục mật khẩu'),
    password: str = Form(..., description='Mật khẩu lần một'),
    re_password: str = Form(..., description='Mật khẩu lần hai'),
):
    """Khôi phục lại mật khẩu"""
    if password != re_password:
        return JSONResponse(content={'status': 'Lỗi!', 'msg': 'Mật khẩu không khớp!'}, status_code=status.HTTP_400_BAD_REQUEST)
    user = MONGO_CLIENT[f'{DB_NAME}']['users'].find_one_and_update(
        filter={
            'keyonce': {'$eq': keyonce}, 'keyonce_expire_at': {'$gte': datetime.datetime.now().timestamp()}
        },
        update={
            '$set': {
                'tokens': [],
                'hashed_password': get_password_hash(password)
            },
            '$unset': {
                'keyonce': '',
                'keyonce_expire_at': ''
            }
        }
    )
    if not user:
        return JSONResponse(content={'status': 'Lỗi!', 'msg': 'Mã hết thời gian hoặc không tồn tại!'}, status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse(content={'status': 'Thành công!', 'msg': 'Mật khẩu đã được thiết lập lại!'}, status_code=status.HTTP_200_OK)


@app.get(path='/account/password/change', responses={
    status.HTTP_200_OK: {
        'model': ChangePasswordResponse200
    }
}, tags=['account'])
async def change_password(
    valid_access_token: dict = Depends(valid_access_token)
):
    """Gửi yêu cầu thay đổi mật khẩu"""
    import datetime
    s_key = valid_access_token.get('s_key')
    nonce = random.randint(100000, 999999)
    expire_in = datetime.datetime.now() + datetime.timedelta(minutes=30)
    expire_at_timestamp = expire_in.timestamp()
    user = MONGO_CLIENT[f'{DB_NAME}']['users'].find_one(
        filter={'secret_key': s_key})
    while user:
        if user.get('nonce_expire_at') and user.get('nonce_expire_at') < datetime.datetime.now().timestamp():
            MONGO_CLIENT[f'{DB_NAME}']['users'].update_one(filter={'secret_key': {'$eq': s_key}}, update={
                                                           '$unset': {'nonce': '', 'nonce_expire_at': ''}})
        nonce = random.randint(100000, 999999)
        user = MONGO_CLIENT[f'{DB_NAME}']['users'].find_one(
            filter={'nonce': nonce})
    MONGO_CLIENT[f'{DB_NAME}']['users'].find_one_and_update(
        filter={'secret_key': {'$eq': s_key}},
        update={'$set': {'nonce': nonce, 'nonce_expire_at': expire_at_timestamp}}
    )
    return JSONResponse(content={'status': 'Thành công!', 'msg': 'Gửi yêu cầu thay đổi mật khẩu thành công!', 'nonce': nonce}, status_code=status.HTTP_200_OK)


@app.post(path='/account/password/change', responses={
    status.HTTP_200_OK: {
        'model': UpdatePasswordResponse200
    },
    status.HTTP_400_BAD_REQUEST: {
        'model': UpdatePasswordResponse400
    },
    status.HTTP_403_FORBIDDEN: {
        'model': UpdatePasswordResponse403
    }
}, tags=['account'])
async def update_password(
    nonce: int = Form(..., description='Mã một lần gồm 6 chữ số'),
    o_password: str = Form(..., description='Mật khẩu khẩu cũ'),
    password: str = Form(..., description='Mật khẩu lần một'),
    re_password: str = Form(..., description='Mật khẩu lần hai'),
    valid_access_token: dict = Depends(valid_access_token)
):
    """Cập nhật mật khẩu"""
    if password != re_password:
        return JSONResponse(content={'status': 'Lỗi!', 'msg': 'Mật khẩu không khớp!'}, status_code=status.HTTP_400_BAD_REQUEST)
    user = MONGO_CLIENT[f'{DB_NAME}']['users'].find_one(
        {
            'nonce': {'$eq': nonce},
            'nonce_expire_at': {
                '$gte': datetime.datetime.now().timestamp()
            }
        },
        {'hashed_password': True}
    )
    if not user:
        return JSONResponse(content={'status': 'Lỗi', 'msg': 'Mã thay đổi mật khẩu không đúng hoặc hết hạn!'}, status_code=status.HTTP_403_FORBIDDEN)
    if not verify_password(o_password, user.get('hashed_password')):
        return JSONResponse(content={'status': 'Lỗi!', 'msg': 'Mật khẩu cũ chưa chính xác!'}, status_code=status.HTTP_403_FORBIDDEN)
    MONGO_CLIENT[f'{DB_NAME}']['users'].find_one_and_update(
        filter={'nonce': {'$eq': nonce}},
        update={
            '$set': {'hashed_password': get_password_hash(password)},
            '$unset': {'nonce': '', 'nonce_expire_at': ''}
        }
    )
    return JSONResponse(content={'status': 'Thành công!', 'msg': 'Cập nhật mật khẩu thành công!'}, status_code=status.HTTP_200_OK)
