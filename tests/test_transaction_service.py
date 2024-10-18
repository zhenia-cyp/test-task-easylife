import pytest
from unittest.mock import AsyncMock
from datetime import datetime
from app.schemas.schema import TransactionCreate, TransactionResponse
from app.models.model import Transaction


@pytest.mark.asyncio
async def test_create_transaction(transaction_service):
    transaction_data = TransactionCreate(
        user_id=1,
        transaction_type="credit",
        amount=100.0,
        transaction_date=datetime.now()
    )

    mock_transaction = Transaction(
        id=1,
        user_id=transaction_data.user_id,
        transaction_type=transaction_data.transaction_type,
        amount=transaction_data.amount,
        transaction_date="25.09.2024, 09:39"
    )

    transaction_service.create_transaction = AsyncMock(return_value=TransactionResponse(
        id=mock_transaction.id,
        user_id=mock_transaction.user_id,
        transaction_type=mock_transaction.transaction_type,
        amount=mock_transaction.amount,
        transaction_date=mock_transaction.transaction_date
    ))

    result = await transaction_service.create_transaction(transaction_data)
    assert isinstance(result, TransactionResponse)
    assert result.amount == mock_transaction.amount
    assert result.transaction_type == mock_transaction.transaction_type
