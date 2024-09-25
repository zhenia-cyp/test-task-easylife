from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.schemas.schema import TransactionResponse, TransactionCreate
from app.services.transaction_service import TransactionService
from fastapi import HTTPException


router_transaction = APIRouter()


@router_transaction.post("/create/transaction/", response_model=TransactionResponse)
async def create_transactions(transaction: TransactionCreate, session: AsyncSession = Depends(get_async_session)):
    transaction_service = TransactionService(session)
    new_transaction = await transaction_service.create_transaction(transaction)
    if not new_transaction:
        raise HTTPException(status_code=400, detail="The similar transaction you can create from а minute. Waite please!'. ")
    return new_transaction


