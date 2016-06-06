from common import hasoffers

BASE_URL = 'https://api.hasoffers.com/Apiv3/json?'
API_KEY = '60f10cb0a51c93ac9d0cd39943896e07dc948d8cfa33900a944c296a82032e7f'
NETWORK_ID = 'zalorasea'
AFFILIATE = 'zalora'
MERCHANT_NAME = 'zalora'
MERCHANT_ID = 'ZA' # this is only the prefix, postfix is CC

def get_transactions(start_date, end_date):
  data = hasoffers.get_conversions(BASE_URL, API_KEY, NETWORK_ID, start_date, end_date)

  if len(data) > 0:
    data['ipg:dealType'] = 'CPS'
    data['ipg:affiliate'] = AFFILIATE
    
    data['ipg:merchantName'] = MERCHANT_NAME
    data['ipg:merchantId'] = data.apply(lambda x: MERCHANT_ID + x['ipg:cc'], axis=1)
    
  return data
