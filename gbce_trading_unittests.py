import datetime
import unittest
import gbce_trading_config
from gbce_trading import GBCETrading, Stock, Trade

class GBCEUnitTests(unittest.TestCase):
    def test_getDividendYield(self):
        stockComm = {'POP': {'Type': 'Common', 'Last Dividend': 8, 'Fixed Dividend': None, 'Par Value': 100, 'Trades': []}}
        testObj = GBCETrading(stockComm)
        self.assertEqual(testObj.getDividendYield(symbol='POP', price=160.0), 0.05)
        self.assertEqual(testObj.getDividendYield(symbol='POP', price=0), None)
        self.assertRaises(ValueError, testObj.getDividendYield, symbol='POP', price=-10.7)
        self.assertRaises(ValueError, testObj.getDividendYield, symbol = 'ABC', price=24.7)
        stockPref = {'JOE': {'Type': 'Preferred', 'Last Dividend': 18, 'Fixed Dividend': 4, 'Par Value': 200, 'Trades': []}}
        testObj2 = GBCETrading(stockPref)
        self.assertAlmostEqual(testObj2.getDividendYield(symbol='JOE', price=254.5), 3.143, 2)

    def test_getPERatio(self):
        stockComm = {'ALE': {'Type': 'Common', 'Last Dividend': 23, 'Fixed Dividend': None, 'Par Value': 60, 'Trades': []}}
        testObj = GBCETrading(stockComm)
        self.assertAlmostEqual(testObj.getPERatio(symbol='ALE', price=88.0), 336.695, 2)
        self.assertEqual(testObj.getPERatio(symbol='ALE', price=0), None)
        self.assertRaises(ValueError, testObj.getPERatio, symbol='POP', price=-75.7)
        self.assertRaises(ValueError, testObj.getPERatio, symbol='XYZ', price=190.2)
        stockPref = {'GIN': {'Type': 'Preferred', 'Last Dividend': 24, 'Fixed Dividend': 14, 'Par Value': 250, 'Trades': []}}
        testObj2 = GBCETrading(stockPref)
        self.assertEqual(testObj2.getPERatio(symbol='GIN', price=350), 35)

    def test_getVolumeWeightedStockPrice(self):
        trade1 = Trade(symbol='TEA', quantity=100, tradeType=gbce_trading_config.TradeType.BUY, price=120.5)
        trade2 = Trade(symbol='TEA', quantity=50, tradeType=gbce_trading_config.TradeType.SELL, price=125.4)
        trade3 = Trade(symbol='TEA', quantity=200, tradeType=gbce_trading_config.TradeType.BUY, price=110.5, timestamp=datetime.datetime.now() - datetime.timedelta(minutes=7))
        stockGin = Stock(symbol='GIN')
        stockGin.addStockDetails(type=gbce_trading_config.StockType.COMMON, lastDividend=20, parValue=200)
        stockTea = Stock(symbol='TEA')
        stockTea.addStockDetails(type=gbce_trading_config.StockType.COMMON, lastDividend=0, parValue=100)
        stockTea.recordTrade(trade1)
        stockTea.recordTrade(trade2)
        stockTea.recordTrade(trade3)
        testObj = GBCETrading()
        self.assertAlmostEqual(testObj.getVolumeWeightedStockPrice(symbol='TEA'), 122.133, 2)
        self.assertRaises(ValueError, testObj.getVolumeWeightedStockPrice, symbol='PQR')
        self.assertEqual(testObj.getVolumeWeightedStockPrice(symbol='GIN'), None)

    def test_getGBCEAllShareIndex(self):
        trade1 = Trade(symbol='TEA', quantity=100, tradeType=gbce_trading_config.TradeType.BUY, price=120.5)
        trade2 = Trade(symbol='TEA', quantity=50, tradeType=gbce_trading_config.TradeType.SELL, price=125.4)
        stockGin = Stock(symbol='GIN')
        stockGin.addStockDetails(type=gbce_trading_config.StockType.COMMON, lastDividend=20, parValue=200)
        stockTea = Stock(symbol='TEA')
        stockTea.addStockDetails(type=gbce_trading_config.StockType.COMMON, lastDividend=0, parValue=100)
        stockTea.recordTrade(trade1)
        stockTea.recordTrade(trade2)
        testObj = GBCETrading()
        self.assertEqual(testObj.getGBCEAllShareIndex(), None)
        trade3 = Trade(symbol='GIN', quantity=150, tradeType=gbce_trading_config.TradeType.BUY, price=225.4)
        stockGin.recordTrade(trade3)
        self.assertAlmostEqual(testObj.getGBCEAllShareIndex(), 165.918, 2)

if __name__ == '__main__':
    unittest.main()