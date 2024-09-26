import pytest
from unittest.mock import AsyncMock
from app.models.model import User, Transaction
from app.schemas.schema import UserCreate, UserResponse, UserTransactionsResponse


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


@pytest.mark.asyncio
async def test_get_user(user_service):
    mock_user = User(id=1, username="test_user")
    mock_transactions = [
        Transaction(id=1, user_id=1, amount=100, transaction_type="electricity", transaction_date="2024-09-24"),
        Transaction(id=2, user_id=1, amount=200, transaction_type="сentral heating", transaction_date="2024-09-25")
    ]
    user_service.get_user = AsyncMock(return_value=UserTransactionsResponse(
        user_id=mock_user.id,
        username=mock_user.username,
        transactions=mock_transactions
    ))

    result = await user_service.get_user(mock_user.id)

    assert isinstance(result, UserTransactionsResponse)
    assert result.user_id == mock_user.id
    assert result.username == mock_user.username
    assert len(result.transactions) == 2
    assert result.transactions[0].amount == 100
    assert result.transactions[1].amount == 200
