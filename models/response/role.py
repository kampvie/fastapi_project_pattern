from typing import List
from pydantic import BaseModel
from pydantic.fields import Field
from starlette import status
from models.role import Role


class ListRole200(BaseModel):
    roles: List[Role]


class CreateRole200(BaseModel):
    status: str = Field(default="Thành công!",
                        description='Trạng thái tạo vai trò')


class UpdateRole200(BaseModel):
    status: str = Field(default='Thành công!',
                        description='Trạng thái cập nhật vai trò')


class DeleteRole200(BaseModel):
    status: str = Field(default='Thành công!',
                        description='Trạng thái xóa vai trò')
