from app.schemas.schema import TransactionCreate


class TransactionService:
    def __init__(self, session):
        self.session = session


    async def create_transaction(self, transaction: TransactionCreate) -> TransactionCreate:
       pass
