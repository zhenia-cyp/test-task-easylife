from pydantic import BaseModel, conint, ConfigDict
from typing import Generic, List, TypeVar, Optional

T = TypeVar("T")

class PageParams(BaseModel):
    page: conint(ge=1) = 1
    size: conint(ge=1, le=100) = 5


class PaginationResponse(BaseModel, Generic[T]):
    user_id: Optional[int] = None
    username: Optional[str] = None
    result: List[T]
    current_page: int
    size: int
    total_pages: int
    total_items:int

    model_config = ConfigDict(from_attributes=True)


class PaginationListResponse(BaseModel, Generic[T]):
    result: List[T]
    current_page: int
    size: int
    total_pages: int
    total_items:int

    model_config = ConfigDict(from_attributes=True)