from math import ceil
from typing import Optional, List, TypeVar, Generic
from app.schemas.pagination import PageParams, PaginationResponse
from sqlalchemy import select

T = TypeVar('T')


class Pagination:
    def __init__(self, model, session, page_params: PageParams, items: Optional[List[T]]):
        self.model = model
        self.session = session
        self.page_params = page_params
        self.items = items
        self.page = page_params.page - 1
        self.offset = self.page * page_params.size
        self.limit = page_params.size


    async def get_pagination(self) -> PaginationResponse:
        items = self.items[self.offset:self.offset + self.limit]
        if not items:
            data = {
                "current_page": 0,
                "size": 0,
                "result": [],
                "total_pages": 0,
                "total_items": 0
            }
            return PaginationResponse.model_validate(data)
        total_items = len(self.items)
        self.total_pages = ceil(total_items / self.page_params.size)
        data = {
            "current_page": self.page_params.page,
            "size": self.page_params.size,
            "result": items,
            "total_pages": self.total_pages,
            "total_items": total_items
        }
        return PaginationResponse.model_validate(data)