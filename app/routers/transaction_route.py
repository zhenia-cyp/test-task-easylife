from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.schemas.schema import TransactionResponse, TransactionCreate, BalanceResponse
from app.services.transaction_service import TransactionService


router_transaction = APIRouter()


@router_transaction.post("/create/transaction/", response_model=TransactionResponse)
async def create_transactions(transaction: TransactionCreate,
                              session: AsyncSession = Depends(get_async_session)):
    """returns the created transaction data"""
    transaction_service = TransactionService(session)
    new_transaction = await transaction_service.create_transaction(transaction)
    if not new_transaction:
        raise HTTPException(
            status_code=400,
            detail="The similar transaction you can create from а minute. Waite please!'. "
        )
    return new_transaction


@router_transaction.post("/request/{user_id}/{payout}/", response_model=TransactionResponse)
async def request_payout(user_id: int, payout: float,
                         session: AsyncSession = Depends(get_async_session)):
    """returns a payout transaction for the specified user and amount"""
    transaction_service = TransactionService(session)
    payout_transaction = await transaction_service.request_payout(user_id, payout)
    if not payout_transaction:
        raise HTTPException(
            status_code=400,
            detail="Payout transaction not found!"
        )
    return payout_transaction


@router_transaction.get("/filter/bonus/{user_id}/{start_date}/{end_date}/",
                        response_model= List[TransactionResponse])
async def filter_bonus_transactions(user_id: int, start_date: str,
                                    end_date: str,
                                    session: AsyncSession = Depends(get_async_session)):
    """returns a list of transactions from referrals filtered by date"""
    transaction_service = TransactionService(session)
    transactions = await transaction_service.filter_bonus_transactions_by_date(user_id, start_date, end_date)
    if not transactions:
        raise HTTPException(
            status_code=400,
            detail="Transactions not found!"
        )
    return transactions


@router_transaction.post("/get/balance/{user_id}/", response_model=BalanceResponse)
async def get_user(user_id: int,
                   session: AsyncSession = Depends(get_async_session)):
    """returns the wallet balance for the specified user"""
    transaction_service = TransactionService(session)
    balance = await transaction_service.get_user_balance(user_id)
    if not balance:
        raise HTTPException(
            status_code=404,
            detail="Wallet balance not found"
        )
    return balance


@router_transaction.get("/filter/payout/{user_id}/{start_date}/{end_date}/")
async def filter_payout_transaction_by_date(user_id: int, start_date: str,
                                           end_date: str,
                                           session: AsyncSession = Depends(get_async_session)):
    """returns a list of payout transactions filtered by date"""
    transaction_service = TransactionService(session)
    transactions = await transaction_service.filter_payout_transaction_by_date(user_id, start_date, end_date)
    if not transactions:
        raise HTTPException(
            status_code=400,
            detail="Transactions payout not found!"
        )
    return transactions


