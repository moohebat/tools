#!/usr/bin/python
# pip install --upgrade google-api-python-client
# pip install progress

# TODO:
# - Support for more than 10 metrics, by running multiple queries

import argparse, ConfigParser, datetime, urllib, socket, re, pandas, sys

from datetime import date, datetime, timedelta
from pprint import pprint

from googleapiclient import sample_tools

reload(sys)
sys.setdefaultencoding("UTF-8")
socket.setdefaulttimeout(10)

GA_IDS = { 
  'SG': {
    'IPRICE' : '75448761'
  },
  'MY': {
    'IPRICE' : '75229758',
    'SAYS' : '110258562',
    'JUICE' : '110251884'
  },
  'ID': {
    'IPRICE' : '75897118'
  },
  'PH' : {
    'IPRICE' : '75445974',
    'RAPPLER' : '111816390'
  }, 
  'TH': {
    'IPRICE' : '79109064'
  },
  'VN': {
    'IPRICE' : '75895336' 
  },
  'HK': {
    'IPRICE' : '75887160'
  }
}

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))
argparser.add_argument('week', type=str, help=('Week number).'))
argparser.add_argument('query', type=str, help=('Path to query file).'))

PAGE_SIZE = 10000

def call(service, cc, website, week, query):
  start_index = 1
  data = []
  while True:    
    page = service.data().ga().get(
      ids='ga:' + GA_IDS[cc][website],
      start_index=start_index,
      max_results=PAGE_SIZE,
      samplingLevel="HIGHER_PRECISION",
      include_empty_rows=False,
      start_date=get_date(week)[0],
      end_date=get_date(week)[1],
      dimensions=query['dimensions'],
      metrics=query['metrics'],
      filters=query['filters'] if query['filters'] else None).execute()

    if 'rows' in page:
      data += page['rows']

    if start_index + PAGE_SIZE <= page['totalResults']:
      start_index = start_index + PAGE_SIZE  
    else:
      break

  return data
  
def get_date(week):
  year, week = week.split("-")
  d = date(int(year),1,1)
  d = d - timedelta(d.weekday())
  dlt = timedelta(days = int(week)*7)
  return (d + dlt).isoformat(),  (d + dlt + timedelta(days=6)).isoformat()

def parse_week(value):
  d = datetime.strptime(value, '%Y%m%d')
  year = str(d.isocalendar()[0])
  week = str(d.isocalendar()[1]).zfill(2)
  return year + "-" + week

def parse_month(value):
  d = datetime.strptime(value, '%Y%m%d')
  return datetime.strftime(d, '%Y-%m')

def parse_device(value):
  # most of our affiliate networks don't support tablet, bucket it into mobile
  value = value.lower()
  if value == 'tablet':
    return 'mobile'
  else:
    return value

def parse_merchant(value):
   split = str(value).split("|")
   
   merchantName = "n/a"
   merchantCode = "n/a"
   
   if len(split) > 0:
    if split[0] != "" and split[0] != "nan":
      merchantName = split[0]
   if len(split) > 1:
     if split[1] != "" and split[1] != "nan":
      merchantCode = split[1]
      
   return (merchantName, merchantCode)

def parse_product(value1, value2, website):
  value1 = value1.lower()
  value2 = value2.lower()

  product, subproduct = 'n/a', 'n/a'

  # media partners don't fully support content groups right now
  if value1 == '(not set)' and website != 'IPRICE':
    product = 'coupon'

  # backwards compatibility with old usage of ga:ContentGroup1
  elif value1 in ['shop', 'brand', 'mixed', 'category', 'search', 'shingle', 'gender', 'list']:
    product = 'shop'
  
  elif value1 in ['coupons', 'coupon', 'coupon-store', 'coupon-category']:
    product = 'coupon'
      
  elif value1 in ['static', 'home', 'info', 'page', 'blog', 'redirect']:
    product = 'static'

  # backwards compatibility with old usage of ga:ContentGroup1
  if value2 != '(not set)':
    subproduct = value2
  
  elif value1 in ['brand', 'mixed', 'category', 'search']:
    subproduct = value1
  
  elif value1 in ['coupon-store', 'coupon-category']:
    subproduct = value1
      
  elif value1 in ['static', 'home', 'info', 'page', 'blog', 'redirect']:
    subproduct = value1

  if product == 'n/a' and value1 != '(not set)' and value1 != '':
    print>> sys.stderr, "Warning: Can't parse product '%s'" % value
  if subproduct == 'n/a' and value2 != '(not set)' and value2 != '':
    print>> sys.stderr, "Warning: Can't parse subproduct '%s'" % value
    
  return (product, subproduct)

def process(cc, website, df):
  df['ipg:cc'] = cc;
  df['ipg:website'] = website;

  if 'ga:date' in df:
    df['ipg:week'] = df.apply(lambda x: parse_week(x['ga:date']), axis=1)
    df['ipg:month'] = df.apply(lambda x: parse_month(x['ga:date']), axis=1)
  if 'ga:deviceCategory' in df:
    df['ipg:device'] = df.apply(lambda x: parse_device(x['ga:deviceCategory']), axis=1)
  if 'ga:contentGroup1' in df:
    df['ipg:product'] = df.apply(lambda x: parse_product(x['ga:contentGroup1'], '', website)[0], axis=1)
  if 'ga:contentGroup1' in df and 'ga:contentGroup2' in df:
    df['ipg:subProduct'] = df.apply(lambda x: parse_product(x['ga:contentGroup1'], x['ga:contentGroup2'], website)[1], axis=1)
  if 'ga:dimension6' in df:
    df['ipg:merchantName'] = df.apply(lambda x: parse_merchant(x['ga:dimension6'])[0], axis=1)
    df['ipg:merchantCode'] = df.apply(lambda x: parse_merchant(x['ga:dimension6'])[1], axis=1)
    
  return df

def parse_query(filename):
  config = ConfigParser.RawConfigParser()
  config.read(filename)
  
  query = {}
  query['dimensions'] = config.get("query", 'dimensions')
  query['metrics'] = config.get("query", 'metrics')
  query['filters'] = config.get("query", 'filters')

  return query

def initialize_service(argv, id):
  service, flags = sample_tools.init(
      argv, id, 'v3', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/' + id + '.readonly')
  return service
  
def main(argv):
  args = argparser.parse_args()

  print >> sys.stderr, '# Start: Google Analytics: %s, %s, %s, %s' % (args.cc, args.week, args.query, datetime.now().time().isoformat())

  ga = initialize_service(argv, "analytics")
  
  query = parse_query(args.query)
  headers = query['dimensions'].split(",") + query['metrics'].split(",")  

  output = pandas.DataFrame()
  for website in GA_IDS[args.cc]:
  
    newQuery = query.copy()    
    # Quirk: Merchant code was only introduced in CW13 and does not exist for CooD yet
    cd6 = re.compile('(,ga:dimension6)').findall(newQuery['dimensions'])
    if len(cd6) > 0 and (int(args.week.split("-")[1]) < 13 or website != "IPRICE"):
      newQuery['dimensions'] = newQuery['dimensions'].replace(cd6[0], '')

    newHeaders = newQuery['dimensions'].split(",") + newQuery['metrics'].split(",")  
    # Quirk: Our CGs in SG are offset one from the rest
    if args.cc == "SG" and website == "IPRICE":
      for cg in reversed(re.compile('(ga:contentGroup([0-9]{1,2}))').findall(newQuery['dimensions'])):
        newQuery['dimensions'] = newQuery['dimensions'].replace(cg[0], 'ga:contentGroup' + str(int(cg[1]) + 1))
    
    data = call(ga, args.cc, website, args.week, newQuery)

    if len(data) == 0:
      print >> sys.stderr, 'Warning: Query did not return any data for website %s' % (website)
      continue

    # need to get all columns in if some where cut previously 
    df = pandas.DataFrame(columns = headers)
    dfNew = pandas.DataFrame(data, columns = newHeaders)
    df = pandas.concat([df, dfNew])
    df = process(args.cc, website, df)
    
    output = pandas.concat([output, df])

  output.to_csv(sys.stdout, header=True, index=False)

  print >> sys.stderr, '# End: Keyword Data: %s, %s, %s, %s' % (args.cc, args.week, args.query, datetime.now().time().isoformat())

if __name__ == '__main__':
    main(sys.argv)
