from typing import List
from pydantic import BaseModel, Field


class UpdateAccount(BaseModel):
    username: str = Field(..., description='Tên người dùng')
    roles_id: List[int] = Field(..., description='Danh sách vai trò của user')
