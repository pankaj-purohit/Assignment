import datetime
import logging
import operator
import gbce_trading_config
from numbers import Number
from functools import reduce

EXCHANGE_STOCKS = {} # Note : Ideally all stocks details/objects to be stored in database, this dict is maintained for assignment purpose

class Stock(object):
    def __init__(self, symbol):
        """
        :param symbol: The symbol that identifies the stock
        Note : self.trades holds list of recorded instances of Trade
        """
        self.symbol = symbol
        self.trades = []

    def addStockDetails(self, type, lastDividend, parValue, fixedDividend=None):
        """
        Adds the Stock details to EXCHANGE_STOCKS cache(dict)
        :param type: Type of Stock i.e. Common, Preferred (maintained in gbce_trading_config.StockType
        :param lastDividend: An absolute value that indicates the last dividend per share for the stock
        :param parValue: The face value per share for the stock
        :param fixedDividend: Percentage value that indicates fixed dividend to the face value of the share
        """
        EXCHANGE_STOCKS[self.symbol] = {
                                            gbce_trading_config.TYPE : type,
                                            gbce_trading_config.LAST_DIVIDEND : lastDividend,
                                            gbce_trading_config.FIXED_DIVIDEND : fixedDividend / 100 if fixedDividend else fixedDividend,
                                            #As Fixed Dividend is represented in percentage so for proper calculations dividing by 100
                                            gbce_trading_config.PAR_VALUE : parValue,
                                            gbce_trading_config.TRADES : self.trades
                                        }

    def recordTrade(self, trade):
        """
        Records the trade and updates accordingly in EXCHANGE_STOCKS cache(dict)
        :param trade: Trade instance for the share
        """
        if not isinstance(trade, Trade):
            raise TypeError('Argument trade {0} should be of type Trade'.format(trade))
        elif self.symbol is not trade.symbol:
            raise ValueError('Argument trade {0} does not belong to this Stock'.format(trade.symbol))
        else:
            self.trades.append(trade)
            EXCHANGE_STOCKS[self.symbol][gbce_trading_config.TRADES] = self.trades

    @staticmethod
    def getAllStocks():
        """
        :return: Returns all Stocks details of exchange
        """
        return EXCHANGE_STOCKS

    @staticmethod
    def getStock(symbol):
        """
        :param symbol: Symbol of Share for which details are required
        :return: Returns Stock details for the given symbol
        """
        return EXCHANGE_STOCKS[symbol]


class Trade(object):
    def __init__(self, symbol, quantity, tradeType, price, timestamp=datetime.datetime.now()):
        """
        :param symbol: The symbol that identifies the stock
        :param quantity: quantity of Stock for Buy/Sell
        :param tradeType: Buy or Sell
        :param price: Trade price
        :param timestamp: Time at which trade took place
        """
        self.symbol = symbol
        if quantity > 0:
            self.quantity = quantity
        else:
            raise ValueError('The quantity of shares should be positive')
        self.tradeType = tradeType
        if price > 0.0:
            self.price = price
        else:
            raise ValueError('Price of share should be positive')
        self.timestamp = timestamp

    @property
    def totalPrice(self):
        """
        return: The total price of the trade
        """
        return self.quantity * self.price


class GBCETrading(object):
    def __init__(self, stocks=None):
        """
        :param stocks: All stock details of exchange
        """
        self.stocks = stocks or Stock.getAllStocks()

    def getDividendYield(self, symbol, price):
        """
        :param symbol: The symbol that identifies the stock
        :param price: Input price for which Dividend Yield to be calculated
        :return: Dividend for the stock at given input price
        """
        if symbol not in self.stocks:
            raise ValueError('Symbol {0} is not present in current stocks. Please consider adding details for {0}'.format(symbol))
        if not isinstance(price, Number) or price < 0:
            raise ValueError('Price must be a positive number. Input price is : {0}'.format(price))
        dividendYield = None
        stockRecord = self.stocks[symbol]
        if stockRecord[gbce_trading_config.TYPE] == gbce_trading_config.StockType.COMMON:
            try:
                dividendYield = stockRecord[gbce_trading_config.LAST_DIVIDEND] / price
            except ZeroDivisionError:
                logging.info('Price is zero hence Dividend yield cannot be calculated')
        else:
            try:
                dividendYield = (stockRecord[gbce_trading_config.FIXED_DIVIDEND] * stockRecord[gbce_trading_config.PAR_VALUE]) / price
            except ZeroDivisionError:
                logging.info('Price is zero hence Dividend yield cannot be calculated' )
        return dividendYield

    def getPERatio(self, symbol, price):
        """
        :param symbol: The symbol that identifies the stock
        :param price: Input price for which PE ratio to be calculated
        :return: PE ratio for the stock at given input price
        """
        if symbol not in self.stocks:
            raise ValueError('Symbol {0} is not present in current stocks. Please consider adding details for {0}'.format(symbol))
        if not isinstance(price, Number) or price < 0:
            raise ValueError('Price must be a positive number. Input price is : {0}'.format(price))
        peratio = None
        try:
            peratio = price / self.getDividendYield(symbol=symbol, price=price)
        except ZeroDivisionError:
            logging.info('Dividend Yield is zero hence PE Ratio cannot be calculated')
        except TypeError:
            logging.info('Price is zero hence Dividend yield and PE Ratio cannot be calculated')
        return peratio

    def getVolumeWeightedStockPrice(self, symbol):
        """
        :param symbol: The symbol that identifies the stock
        :return: Volume Weighted Stock Price for a given stock based on trades in past 5 minutes
        """
        if symbol not in self.stocks:
            raise ValueError('Symbol {0} is not present in current stocks. Please consider adding details for {0}'.format(symbol))
        volumeWeightedStockPrice = None
        currentTime = datetime.datetime.now()
        allTrades = self.stocks[symbol][gbce_trading_config.TRADES]
        requiredTrades = [trade for trade in allTrades if trade.timestamp >= currentTime - gbce_trading_config.TIME_INTERVAL]
        if len(requiredTrades) > 0:
            tradePrices = (trade.totalPrice for trade in requiredTrades)
            quantities = (trade.quantity for trade in requiredTrades)
            volumeWeightedStockPrice = sum(tradePrices) / sum(quantities)
        return volumeWeightedStockPrice

    def getGBCEAllShareIndex(self):
        """
        :return: Returns the GBCE All Share Index using the geometric mean of the Volume Weighted Stock Price for all Stocks
        """
        allShareIndex = None
        volumeWeightedStockPrices = [self.getVolumeWeightedStockPrice(symbol) for symbol in self.stocks]
        if not None in volumeWeightedStockPrices:
            product = reduce(operator.mul, volumeWeightedStockPrices, 1)
            allShareIndex = product**(1/len(self.stocks))
        return allShareIndex


if __name__ == '__main__':
    ### Setup

    # Trades entries
    trade1 = Trade(symbol='TEA', quantity=100, tradeType=gbce_trading_config.TradeType.BUY, price=120.5)
    #trade2 = Trade(symbol='TEA', quantity=50, tradeType=gbce_trading_config.TradeType.SELL, price=125.4, timestamp=datetime.datetime.now() - datetime.timedelta(minutes=7))
    trade2 = Trade(symbol='TEA', quantity=50, tradeType=gbce_trading_config.TradeType.SELL, price=125.4)
    trade3 = Trade(symbol='TEA', quantity=20, tradeType=gbce_trading_config.TradeType.BUY, price=118)
    trade4 = Trade(symbol='TEA', quantity=60, tradeType=gbce_trading_config.TradeType.SELL, price=122.5)
    trade5 = Trade(symbol='POP', quantity=200, tradeType=gbce_trading_config.TradeType.BUY, price=250)
    trade6 = Trade(symbol='POP', quantity=100, tradeType=gbce_trading_config.TradeType.SELL, price=240.4)
    trade7 = Trade(symbol='ALE', quantity=50, tradeType=gbce_trading_config.TradeType.BUY, price=348)
    trade8 = Trade(symbol='ALE', quantity=50, tradeType=gbce_trading_config.TradeType.SELL, price=354.8)
    trade9 = Trade(symbol='GIN', quantity=549, tradeType=gbce_trading_config.TradeType.BUY, price=465)
    trade10 = Trade(symbol='JOE', quantity=400, tradeType=gbce_trading_config.TradeType.SELL, price=462.4)
    #trade10 = Trade(symbol='JOE', quantity=400, tradeType=gbce_trading_config.TradeType.SELL, price=462.4, timestamp=datetime.datetime.now() - datetime.timedelta(minutes=8))
    trade11 = Trade(symbol='JOE', quantity=240, tradeType=gbce_trading_config.TradeType.BUY, price=534.75)

    # Initial Exchange stocks entries and trades recording
    stockTea = Stock(symbol='TEA')
    stockTea.addStockDetails(type=gbce_trading_config.StockType.COMMON, lastDividend=0, parValue=100)
    stockTea.recordTrade(trade1)
    stockTea.recordTrade(trade2)
    stockTea.recordTrade(trade3)
    stockTea.recordTrade(trade4)
    stockPop = Stock(symbol='POP')
    stockPop.addStockDetails(type=gbce_trading_config.StockType.COMMON, lastDividend=8, parValue=100)
    stockPop.recordTrade(trade5)
    stockPop.recordTrade(trade6)
    stockAle = Stock(symbol='ALE')
    stockAle.addStockDetails(type=gbce_trading_config.StockType.COMMON, lastDividend=23, parValue=60)
    stockAle.recordTrade(trade7)
    stockAle.recordTrade(trade8)
    stockGin = Stock(symbol='GIN')
    stockGin.addStockDetails(type=gbce_trading_config.StockType.PREFERRED, lastDividend=8, fixedDividend=2, parValue=100)
    stockGin.recordTrade(trade9)
    stockJoe = Stock(symbol='JOE')
    stockJoe.addStockDetails(type=gbce_trading_config.StockType.COMMON, lastDividend=13, parValue=250)
    stockJoe.recordTrade(trade10)
    stockJoe.recordTrade(trade11)

    obj = GBCETrading()
    #print(obj.stocks)
    #print(Stock.getStock('TEA'))
    print(obj.getDividendYield(symbol = 'GIN', price = 2.2))
    print(obj.getPERatio(symbol='GIN', price = 2.2))
    print(obj.getVolumeWeightedStockPrice(symbol = 'TEA'))
    print(obj.getGBCEAllShareIndex())