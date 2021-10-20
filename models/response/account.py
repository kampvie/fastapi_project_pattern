from typing import List, Dict, Optional

from pydantic import BaseModel, Field

from models.user import Token


class CreateAccountResponse200(BaseModel):
    status: str = "Tạo tài khoản thành công!"
    access_token: str = Field(
        ...,
        description='JWT Access token'
    )
    device_id: str = Field(..., description='Id thiết bị')
    secret_key: str = Field(..., description='Secret key cho tài khoản')
    is_verified: bool = Field(
        False, description='Trạng thái xác thực tài khoản')


class CreateAccountResponse403(BaseModel):
    status: str = "Lỗi"
    msg: str = "Email đã tồn tại"


class LoginResponse200(BaseModel):
    token: Token = Field(..., description='Access token')
    secret_key: str = Field(..., description='Secret key')


class LoginResponse403(BaseModel):
    status: str = Field(default="Lỗi")
    msg: Optional[str] = Field(description='Thông báo lỗi')


class LoginResponse404(BaseModel):
    status: str = Field(default="Lỗi")
    msg: Optional[str] = Field(description='Không tồn tại')


class UpdateAccount200(BaseModel):
    status: str = Field(default='Cập nhật tài khoản thành công!')


class UpdateAccount302(BaseModel):
    status: str = Field(default='Lỗi!')
    msg: str


class UpdateAccount400(BaseModel):
    status: str = Field(default='Lỗi!')


class VerifyAccountResponse200(BaseModel):
    status: str = Field(default='Thành công!')
    msg: str = Field(default='Đã xác nhận tài khoản!')


class VerifyAccountResponse403(BaseModel):
    status: str = Field(default='Lỗi!')
    msg: str = Field(default='Key xác nhận không hợp lệ hoặc hết thời gian')


class ResetPasswordResponse201(BaseModel):
    status: str = Field(default='Thành công!')
    msg: str = Field(default='Vui lòng kiểm tra email và nhập mã!')


class ResetPasswordResponse404(BaseModel):
    status: str = Field(default='Lỗi!')
    msg: str = Field(default='Tài khoản không tồn tại!')


class PutResetPasswordResponse200(BaseModel):
    status: str = Field(default='Thành công!')
    msg: str = Field(default='Mật khẩu đã được thiết lập lại')


class PutResetPasswordResponse400(BaseModel):
    status: str = Field(default='Lỗi!')
    msg: str = Field(default='Mã hết thời gian hoặc không tồn tại!')


class ChangePasswordResponse200(BaseModel):
    status: str = Field(default='Thành công!')
    msg: str = Field(default='Gửi yêu cầu thay đổi mật khẩu thành công!')
    nonce: int = Field(default='123456', description='Mã 6 chữ số dùng 1 lần')


class UpdatePasswordResponse200(BaseModel):
    status: str = Field(default='Thành công!')
    msg: str = Field(default='Cập nhật mật khẩu thành công!')


class UpdatePasswordResponse400(BaseModel):
    status: str = Field(default='Lỗi!')
    msg: str = Field(default='Mật khẩu không khớp!')


class UpdatePasswordResponse403(BaseModel):
    status: str = Field(default='Lỗi!')
    msg: str = Field(..., description='Thông tin lỗi')
