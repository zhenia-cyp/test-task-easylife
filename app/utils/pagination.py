from math import ceil
from typing import Optional, List, TypeVar
from app.schemas.pagination import PageParams, PaginationListResponse
from pydantic import BaseModel
from typing import Type
T = TypeVar('T')


class Pagination:
    def __init__(self, page_params: PageParams, items: Optional[List[T]], schema: Type[BaseModel]):

        self.page_params = page_params
        self.items = items
        self.page = max(page_params.page - 1, 0)
        self.offset = self.page * page_params.size
        self.limit = page_params.size
        self.schema = schema


    async def get_pagination(self):
        items = self.items[self.offset:self.offset + self.limit]
        if not items:
            return self.empty_response()

        total_items = len(self.items)
        total_pages = ceil(total_items / self.page_params.size)
        data = {
            "current_page": self.page_params.page,
            "size": self.page_params.size,
            "result": items,
            "total_items": total_items,
            "total_pages": total_pages,

        }
        return self.schema.model_validate(data)


    def empty_response(self):
        data = {
            "current_page": 0,
            "size": 0,
            "result": [],
            "total_items": 0,
            "total_pages": 0

        }
        return self.schema.model_validate(data)