from datetime import timedelta

""" Config is maintained so that if there are any nomenclature/constant value changes required later, they can be made at a single place
and all dependent changes would be handled accordingly. """

# Stock config
TYPE = 'Type'
LAST_DIVIDEND = 'Last Dividend'
FIXED_DIVIDEND = 'Fixed Dividend'
PAR_VALUE = 'Par Value'
TRADES = 'Trades'

# Trade config
TIMESTAMP = 'Time Stamp'
QUANTITY = 'Quantity'
TRADE_TYPE = 'TradeType'
PRICE = 'Price'

class StockType(object):
    COMMON = 'Common'
    PREFERRED = 'Preferred'

class TradeType(object):
    BUY = 'Buy'
    SELL = 'Sell'

THRESHOLD_MINUTES = 5
TIME_INTERVAL = timedelta(minutes=THRESHOLD_MINUTES)