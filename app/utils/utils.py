async def replace_date_format(array):
    for transaction in array:
        formatted_date = transaction.get_transaction_date_in_local().strftime('%d.%m.%Y, %H:%M')
        transaction.transaction_date = formatted_date
    return array