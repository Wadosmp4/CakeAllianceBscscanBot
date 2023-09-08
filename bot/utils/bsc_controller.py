import re

from typing import List, Dict, Any
from bscscan import BscScan
from datetime import datetime

from config import BSC_SCAN_API_KEY, WEI_TO_BNB, DATE_FORMAT, TRANSACTION_FORMAT


class BscController:

    @staticmethod
    async def get_all_transactions(account_address: str):
        """Get all transactions by account."""
        page = 1
        result = []
        while True:
            try:
                data = await BscController.get_transactions_by_account(account_address=account_address, page=page)
                result += data
                page += 1
            except AssertionError:
                break
        return result

    @staticmethod
    async def get_transactions_by_account(account_address: str, page: int = 1,
                                          offset: int = 5_000, start_block: int = 0,
                                          end_block: int = 99_999_999, order: str = "asc") -> List[Dict[str, Any]]:
        """Get a list of transactions by account with specific parameters."""
        async with BscScan(BSC_SCAN_API_KEY) as bsc:
            result = await bsc.get_normal_txs_by_address_paginated(address=account_address, page=page,
                                                                   offset=offset, startblock=start_block,
                                                                   endblock=end_block, sort=order)
        return result

    @classmethod
    def transform_transaction_data(cls, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform a list of transaction dictionaries."""
        transformed_transactions = [
            {
                '_id': txn['hash'],
                'block': txn['blockNumber'],
                'date': cls.transform_txn_date(txn['timeStamp']),
                'method': cls.transform_txn_method(txn['functionName']) or txn['methodId'],
                'from': txn['from'],
                'to': txn['to'],
                'value': cls.convert_wei_to_bnb(int(txn['value'])),
                'txn_fee': cls.convert_wei_to_bnb(cls.calculate_gas_fee(txn['gasPrice'], txn['gasUsed'])),
                'success': bool(int(txn['txreceipt_status'])),
                'contract_address': txn['contractAddress']
            }
            for txn in transactions
        ]
        return transformed_transactions

    @staticmethod
    def transactions_to_show(transactions: List[Dict[str, Any]]):
        return "\n\n".join([TRANSACTION_FORMAT.format(**txn) for txn in transactions])

    @staticmethod
    def transform_txn_date(txn_date: str) -> str:
        """Transform a timestamp to a formatted date string."""
        return datetime.fromtimestamp(int(txn_date)).strftime(DATE_FORMAT)

    @staticmethod
    def transform_txn_method(txn_function: str) -> str:
        """Transform a transaction function to a human-readable name."""
        txn_funxtion_name = txn_function.split('(')[0]
        split_camel_case = re.sub(r'([a-z])([A-Z])', r'\1 \2', txn_funxtion_name)
        return split_camel_case.title()

    @staticmethod
    def calculate_gas_fee(gas_price: str, gas_used: str) -> int:
        """Calculate the transaction gas fee."""
        return int(gas_price) * int(gas_used)

    @staticmethod
    def convert_wei_to_bnb(wei: int) -> float:
        """Convert Wei to Binance Coin (BNB)."""
        return wei * WEI_TO_BNB
