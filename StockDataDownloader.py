import pandas
from datetime import date

class StockDataDownloader(object):
    """Downloads data from various stock services"""

    def get_data_from_finam(self, ticker, period, marketCode, insCode, dateFrom, dateTo):
        """Downloads data from FINAM.ru stock service"""
        addres = 'http://export.finam.ru/data.txt?market=' + str(marketCode) + '&em=' + str(insCode) + '&code=' + ticker + '&df=' + str(dateFrom.day) + '&mf=' + str(dateFrom.month-1) + '&yf=' + str(dateFrom.year) + '&dt=' + str(dateTo.day) + '&mt=' + str(dateTo.month-1) + '&yt=' + str(dateTo.year) + '&p=' + str(period + 2) +'data&e=.txt&cn=GAZP&dtf=4&tmf=4&MSOR=1&sep=1&sep2=1&datf=5&at=1'
        return pandas.read_csv(addres)