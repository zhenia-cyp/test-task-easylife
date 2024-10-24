from math import ceil
from typing import Optional, List, TypeVar, Type
from pydantic import BaseModel
from app.schemas.pagination import PageParams

T = TypeVar('T')


class Pagination:
    """a class for paginating data based on page parameters"""
    def __init__(self, page_params: PageParams, items: Optional[List[T]], schema: Type[BaseModel]):

        self.page_params = page_params
        self.items = items
        self.page = max(page_params.page - 1, 0)
        self.offset = self.page * page_params.size
        self.limit = page_params.size
        self.schema = schema


    async def get_pagination(self):
        """get the paginated response based on the provided
        items and page parameters"""
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
        """returns an empty paginated response when no items are available"""
        data = {
            "current_page": 0,
            "size": 0,
            "result": [],
            "total_items": 0,
            "total_pages": 0

        }
        return self.schema.model_validate(data)
