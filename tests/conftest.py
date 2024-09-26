import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import UserService


@pytest.fixture(scope="function")
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture(scope="function")
def user_service(mock_session):
    return UserService(mock_session)