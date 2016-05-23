#!/usr/bin/python
# pip install --upgrade google-api-python-client
# pip install progress

# TODO:
# - Improve product / sub-product parsing to the next level
# - Support for custom dimensions, remove custom dimensions for dates before CW 21  
# - Support for more than 10 metrics, by running multiple queries

import argparse, ConfigParser, datetime, urllib, socket, re, sys

from datetime import date, datetime, timedelta
from pprint import pprint
from pandas import DataFrame

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
    'JUICE' : '110251884',
    'OHBULAN' : '110268914',
    'HANGER' : '110262569'
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

def parse_product(value, website):
  # media partners didn't have content groups set for a long time
  if value == '(not set)' and website != 'IPRICE':
    return 'coupon'

  # backwards compatibility with old usage of ga:ContentGroup1
  value = value.lower()
  if value in ['shop', 'brand', 'mixed', 'category', 'search']:
    return 'shop'
  
  if value in ['coupons', 'coupon', 'coupon-store', 'coupon-category']:
    return 'coupon'
      
  if value in ['static', 'home', 'info', 'page', 'blog', 'redirect']:
    return 'static'

  if value == '(not set)':
    return 'n/a'
  
  print>> sys.stderr, "Warning: Can't parse product '%s'" % value
  return ""

def process(cc, website, df):
  df['ipg:cc'] = cc;
  df['ipg:website'] = website;

  if 'ga:date' in df:
    df['ipg:week'] = df.apply(lambda x: parse_week(x['ga:date']), axis=1)
    df['ipg:month'] = df.apply(lambda x: parse_month(x['ga:date']), axis=1)
  if 'ga:deviceCategory' in df:
    df['ipg:device'] = df.apply(lambda x: parse_device(x['ga:deviceCategory']), axis=1)
  if 'ga:contentGroup1' in df:
    df['ipg:product'] = df.apply(lambda x: parse_product(x['ga:contentGroup1'], website), axis=1)
    
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

  print >> sys.stderr, '# Start: Google Analytics: %s, %s, %s' % (args.cc, args.week, datetime.now().time().isoformat())

  ga = initialize_service(argv, "analytics")
  
  query = parse_query(args.query)

  data = []
  for website in GA_IDS[args.cc]:
  
    # Quirk: Our CGs in SG are offset one from the rest
    newQuery = query.copy()
    if args.cc == "SG" and website == "IPRICE":
      for cg in reversed(re.compile('(ga:contentGroup([0-9]{1,2}))').findall(newQuery['dimensions'])):
        newQuery['dimensions'] = newQuery['dimensions'].replace(cg[0], 'ga:contentGroup' + str(int(cg[1]) + 1))

    data += call(ga, args.cc, website, args.week, newQuery)

  headers = query['dimensions'].split(",") +query['metrics'].split(",")  
  df = DataFrame(data, columns = headers)
  df = process(args.cc, website, df)
  df.to_csv(sys.stdout, header=True, index=False)

  print >> sys.stderr, '# End: Keyword Data: %s, %s, %s' % (args.cc, args.week, datetime.now().time().isoformat())

if __name__ == '__main__':
    main(sys.argv)