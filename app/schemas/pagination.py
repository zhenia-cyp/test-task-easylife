from typing import Generic, List, TypeVar, Optional
from pydantic import BaseModel, conint, ConfigDict

T = TypeVar("T")

class PageParams(BaseModel):
    """schema for pagination parameters, including page number and page size"""
    page: conint(ge=1) = 1
    size: conint(ge=1, le=100) = 5


class PaginationResponse(BaseModel, Generic[T]):
    """a generic pagination response schema"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    result: List[T]
    total_items: int
    current_page: int
    size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)


class PaginationListResponse(BaseModel, Generic[T]):
    """a generic pagination list response schema, without user details,
        containing the result list and pagination metadata"""
    result: List[T]
    total_items: int
    current_page: int
    size: int
    total_pages: int


    model_config = ConfigDict(from_attributes=True)
