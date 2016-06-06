# https://oxr.readme.io/
# data is cached because the free version of the API has a limit of 1000 calls/month

import calendar, datetime, dateutil.parser, os, cPickle, pandas, requests, sys, tempfile

FILENAME = "openexchangerates.obj"
APP_ID = "f235da0c106b4df7ad41e1e80052bd2d"
TMP_DIR = tempfile.gettempdir()

class ExchangeRates():
    exchangeRates = {}

    def __init__(self, offset = 0):
        self.__load()
    
    def __load(self):
        absolute = os.path.join(TMP_DIR, FILENAME)
        if os.path.isfile(absolute):
            file = open(absolute, "rb")
            self.exchangeRates = cPickle.load(file)
            file.close()
    
    def __save(self):
        fd = open(os.path.join(TMP_DIR, FILENAME), "wb")
        cPickle.dump(self.exchangeRates, fd)
        fd.close()

    def getExchangeRates(self, date):
        if not date in self.exchangeRates:
            r = requests.get("https://openexchangerates.org/api/historical/%s.json?app_id=%s" % (date, APP_ID))
            self.exchangeRates[date] = r.json()['rates']
            self.exchangeRates[date]['USD'] = 1.0
            self.__save()

        return self.exchangeRates[date]
            
ER = ExchangeRates()

def convert(value, transaction_date, old_currency, new_currency):
    try:
        value = float(value)
    except ValueError:
        return pandas.np.nan
    except TypeError:
        return pandas.np.nan

    dateNow = datetime.datetime.now().date()
    dateTransaction = dateutil.parser.parse(transaction_date)
    
    # if the month is still ongoing take today's exchangeRate
    if (dateTransaction.month == dateNow.month):
        date = dateNow
    # else use the one from the last day of the month
    else:
        date = datetime.date(dateTransaction.year, dateTransaction.month, 
            calendar.monthrange(dateTransaction.year, dateTransaction.month)[1])

    oldRate = ER.getExchangeRates(date.isoformat())[old_currency]
    newRate = ER.getExchangeRates(date.isoformat())[new_currency]
    
    value = float(value) / oldRate * newRate
    
    return value
