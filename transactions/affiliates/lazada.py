from common import hasoffers

BASE_URL = 'https://api.hasoffers.com/Apiv3/json'
API_KEY = 'c531cd691a887debe3829e733c201d02b7c553cec109eb10a4ba931c14b3c0e0'
NETWORK_ID = 'lazada'
AFFILIATE = 'lazada'
MERCHANT_NAME = 'lazada'
MERCHANT_ID = 'LZ' # this is only the prefix, postfix is CC

def get_transactions(start_date, end_date):
  data = hasoffers.get_conversions(BASE_URL, API_KEY, NETWORK_ID, start_date, end_date)
  
  if len(data) > 0:
    data['ipg:dealType'] = 'CPS'
    data['ipg:affiliate'] = AFFILIATE
    
    data['ipg:merchantName'] = MERCHANT_NAME
    data['ipg:merchantId'] = data.apply(lambda x: MERCHANT_ID + x['ipg:cc'], axis=1)
  
  return data
  
