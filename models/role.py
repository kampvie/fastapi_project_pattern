from typing import List
import datetime

from pydantic import BaseModel, EmailStr
from pydantic.fields import Field

class Role(BaseModel):
    role_id: int = Field(default=datetime.datetime.now().microsecond, description='ID role')
    name: str = Field(..., description="Tên vai trò")