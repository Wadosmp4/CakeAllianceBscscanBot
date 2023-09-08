WEI_TO_BNB = 10e-18

DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f%z'

TRANSACTIONS_PER_PAGE = 3

SUBSCRIBED_ADDRESSES = 'subscribed_addresses'
SUBSCRIBERS = 'subscribers'
TRANSACTIONS = 'transactions'
ID = '_id'

TRANSACTION_FORMAT = ('⭕️ <b>Transaction:</b> {_id}\n'
                      '🧱 <b>Block:</b> {block}\n'
                      '⏳ <b>Date:</b> {date}\n'
                      '🔄 <b>Method:</b> {method}\n'
                      '👤 <b>From:</b> {from}\n'
                      '🎯 <b>To:</b> {to}\n'
                      '💰 <b>Value:</b> {value}\n'
                      '💼 <b>Transaction Fee:</b> {txn_fee}\n'
                      '✅ <b>Success:</b> {success}\n'
                      '📦 <b>Contract Address:</b> {contract_address}')
