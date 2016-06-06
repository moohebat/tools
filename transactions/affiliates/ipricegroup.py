from common import hasoffers, parse

import pandas

BASE_URL = 'https://api.hasoffers.com/Api/json?'
API_KEY = '509be7e6d7dd1260b62c04b56be6f727caad4e84d4824d5d6fb7d4451fb06924'
NETWORK_ID = 'ipricegroup'
AFFILIATE = 'ipricegroup'

TEST_ORDERS = {
  'ho:Stat.source': ['test', 'testoffer', 'testoffer??utm_medium=referral&utm_source=iprice&utm_campaign=affiliate'],
  'ho:Offer.name': ['iprice test offer', 'MY myVoucher', 'MK1 Offer', 'Test Store', 'Test Company Shop HK', 'voucher', 'Test Offer'],
  'ho:Stat.affiliate_info1': ['testoffer', 'test', 'Hussein'],
  'ho:Stat.affiliate_info2': ['Reza'],
  'ho:Stat.status_code': [21]
}

def detect_test_orders(data):
  for index, row in data.iterrows():
    for field, values in TEST_ORDERS.iteritems():
      if data.loc[index][field] in values:
        data.set_value(index, 'ipg:suspicious', "test order")
  return data

def get_transactions(start_date, end_date):
  # CPS
  conversions = hasoffers.get_conversions(BASE_URL, API_KEY, NETWORK_ID, start_date, end_date)
  
  if len(conversions) > 0:
    conversions['ipg:dealType'] = 'CPS'
    conversions['ipg:affiliate'] = AFFILIATE
      
  # CPC
  # TODO (0): compress data by replacing source dimension with product and channel dimension
  performance = hasoffers.get_performance(BASE_URL, API_KEY, NETWORK_ID, start_date, end_date)
  
  if len(performance) > 0:
    performance['ipg:dealType'] = 'CPC'
    performance['ipg:affiliate'] = AFFILIATE

  data = pandas.DataFrame()
  data = data.append(conversions, ignore_index=True)
  data = data.append(performance, ignore_index=True)
  
  data = detect_test_orders(data)
  
  return data
