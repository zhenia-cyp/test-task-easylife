import pytest
from unittest.mock import AsyncMock
from app.models.model import User, Transaction
from app.schemas.pagination import PaginationListResponse, PageParams
from app.schemas.schema import UserCreate, UserResponse, UserTransactionsResponse


@pytest.mark.asyncio
async def test_add_user(user_service):
    user = UserCreate(username="new_user")
    user_service.is_user_exists = AsyncMock(return_value=False)
    user_service.add_user = AsyncMock(return_value=UserResponse(id=1))

    result = await user_service.add_user(user.username)

    assert isinstance(result, UserResponse)
    assert result.id == 1


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


@pytest.mark.asyncio
async def test_get_all_users(user_service):
    mock_user = User(id=1, username="user1")
    mock_transactions_user = Transaction(id=1, user_id=1, transaction_type="credit", amount=100.0, transaction_date="2024-01-01")

    user_transactions_response = [
        UserTransactionsResponse(
            user_id=mock_user.id,
            username=mock_user.username,
            transactions=[
                {
                    "id": mock_transactions_user.id,
                    "transaction_type": mock_transactions_user.transaction_type,
                    "amount": mock_transactions_user.amount,
                    "transaction_date": mock_transactions_user.transaction_date
                }
            ]
        )
    ]
    user_service.get_all_users = AsyncMock(return_value=PaginationListResponse(
        current_page=1,
        size=10,
        total_items=1,
        total_pages=1,
        result=user_transactions_response
    ))
    page_params = PageParams(page=1, size=10)
    result = await user_service.get_all_users(page_params)
    print(result.result[0].transactions)
    assert isinstance(result, PaginationListResponse)
    assert result.current_page == 1
    assert result.size == 10
    assert result.total_items == 1
    assert len(result.result) == 1

    assert result.result[0].user_id == mock_user.id
    assert result.result[0].username == mock_user.username
    assert len(result.result[0].transactions) == 1
    assert result.result[0].transactions[0].transaction_type == "credit"
    assert result.result[0].transactions[0].amount == 100.0
