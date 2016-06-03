from common import hasoffers, parse

BASE_URL = 'https://api.hasoffers.com/Api/json?'
API_KEY = 'fd48513d3b1502e9e77d8ec0fd7ba28f43225ea44525d74271bb7706d588e851'
NETWORK_ID = 'sscpa'
AFFILIATE = 'shopstylers'
              
def get_transactions(start_date, end_date):
  data = hasoffers.get_conversions(BASE_URL, API_KEY, NETWORK_ID, start_date, end_date)

  if len(data) > 0:
    data['ipg:dealType'] = 'CPS'
    data['ipg:affiliate'] = AFFILIATE
    
  return data

