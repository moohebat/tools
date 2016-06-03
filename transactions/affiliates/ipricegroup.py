from common import hasoffers, parse

import pandas

BASE_URL = 'https://api.hasoffers.com/Api/json?'
API_KEY = '509be7e6d7dd1260b62c04b56be6f727caad4e84d4824d5d6fb7d4451fb06924'
NETWORK_ID = 'ipricegroup'
AFFILIATE = 'ipricegroup'

# TODO: make sure this one works
filterList = {'source': ['test', 'testoffer'], 'Affiliate': ['test Affiliate'],
              'offer': ['myVoucher', 'MK1 Offer', 'Test Store', 'Test Company Shop HK', 'voucher', 'Test Offer'],
              'subid_1': ['Reza']}

# TODO: What does this mean?
CPC_CAP = {'Galleon': {'2015-09': 0, '2015-10': 0}}


def get_transactions(start_date, end_date):
  # CPS
  conversions = hasoffers.get_conversions(BASE_URL, API_KEY, NETWORK_ID, start_date, end_date)
  
  if len(conversions) > 0:
    conversions['ipg:dealType'] = 'CPS'
    conversions['ipg:affiliate'] = AFFILIATE
    
  # CPC
  performance = hasoffers.get_performance(BASE_URL, API_KEY, NETWORK_ID, start_date, end_date)
  
  if len(performance) > 0:
    performance['ipg:dealType'] = 'CPC'
    performance['ipg:affiliate'] = AFFILIATE

  data = pandas.DataFrame()
  data = data.append(conversions, ignore_index=True)
  data = data.append(performance, ignore_index=True)
  
  return data
