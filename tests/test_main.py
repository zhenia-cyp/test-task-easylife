import pytest
from unittest.mock import AsyncMock
from app.schemas.schema import UserCreate, UserResponse


@pytest.mark.asyncio
async def test_add_user(user_service):
    user = UserCreate(username="new_user")
    user_service.is_user_exists = AsyncMock(return_value=False)
    user_service.add_user = AsyncMock(return_value=UserResponse(id=1))

    result = await user_service.add_user(user.username)

    assert isinstance(result, UserResponse)
    assert result.id == 1
    user_service.is_user_exists.assert_not_called()
    user_service.add_user.assert_called_once_with(user.username)