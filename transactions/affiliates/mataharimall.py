from common import hasoffers

BASE_URL = 'https://api.hasoffers.com/Apiv3/json?'
API_KEY = '8364d537e84a82afb71e221a076a368d35f49c87ccdedf040e2d2637ee71c948'
NETWORK_ID = 'mataharimall'
AFFILIATE = 'mataharimall'
MERCHANT_NAME = 'MatahariMall'
MERCHANT_ID =  'MM101'

def get_transactions(start_date, end_date):
  data = hasoffers.get_conversions(BASE_URL, API_KEY, NETWORK_ID, start_date, end_date, currency = "IDR")
  
  if len(data) > 0:
    data['ipg:dealType'] = 'CPS'
    data['ipg:affiliate'] = AFFILIATE
    
    data['ipg:merchantName'] = MERCHANT_NAME
    data['ipg:merchantId'] = MERCHANT_ID
    
  return data
