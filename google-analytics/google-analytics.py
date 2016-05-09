#!/usr/bin/python
# pip install --upgrade google-api-python-client
# pip install progress

import argparse, ConfigParser, datetime, urllib, socket, sys

from datetime import date, timedelta
from progress.bar import Bar
from pprint import pprint

from googleapiclient import sample_tools

reload(sys)
sys.setdefaultencoding("UTF-8")
socket.setdefaulttimeout(10)

# TODO: put common code into external library
GA_IDS = { 'SG':'75448761', 'MY':'75229758','ID':'75897118', 'PH':'75445974', 'TH':'79109064', 'VN':'75895336', 'HK':'75887160' }

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))
argparser.add_argument('week', type=int, help=('Week number).'))
argparser.add_argument('queries', type=str, help=('Path to queries file).'))

# TODO: Make YEAR default value
YEAR, PAGE_SIZE = 2016, 10000

def call(service, cc, week, query):

  # Our CGs in SG are offset one from the rest
  newQuery = query.copy()
  if cc == "SG" and "ga:ContentGroup1" in newQuery['dimensions']:
    newQuery['dimensions'].replace("ga:ContentGroup1", "ga:ContentGroup2")
  if cc == "SG" and "ga:ContentGroup2" in newQuery['dimensions']:
    newQuery['dimensions'].replace("ga:ContentGroup2", "ga:ContentGroup3")
  if cc == "SG" and "ga:ContentGroup3" in newQuery['dimensions']:
    newQuery['dimensions'].replace("ga:ContentGroup3", "ga:ContentGroup4")
  if cc == "SG" and "ga:ContentGroup4" in newQuery['dimensions']:
    newQuery['dimensions'].replace("ga:ContentGroup4", "ga:ContentGroup5")
    
  start_index = 1
  data = []
  while True:    
    page = service.data().ga().get(
      ids='ga:' + GA_IDS[cc],
      start_index=start_index,
      max_results=PAGE_SIZE,
      samplingLevel="HIGHER_PRECISION",
      include_empty_rows=False,
      start_date=get_date(YEAR, week)[0],
      end_date=get_date(YEAR, week)[1],
      dimensions=newQuery['dimensions'],
      metrics=newQuery['metrics'],
      filters=newQuery['filters'] if newQuery['filters'] else None).execute()
    
    data.append(page)
      
    if start_index + PAGE_SIZE <= page['totalResults']:
      start_index = start_index + PAGE_SIZE  
    else:
      break

  return data
  
def get_date(year, week):
    d = date(year,1,1)
    d = d - timedelta(d.weekday())
    dlt = timedelta(days = week*7)
    return (d + dlt).isoformat(),  (d + dlt + timedelta(days=6)).isoformat()

def initialize_service(argv, id):
  service, flags = sample_tools.init(
      argv, id, 'v3', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/' + id + '.readonly')
  return service

def parse_query(filename):
    config = ConfigParser.RawConfigParser()
    config.read(filename)
    
    query = {}
    query['dimensions'] = config.get("query", 'dimensions')
    query['metrics'] = config.get("query", 'metrics')
    query['filters'] = config.get("query", 'filters')

    return query

def output(data, cc):
  for page in data:
    for row in page['rows']:
      print cc + '\t' + '\t'.join(row)

def main(argv):
  args = argparser.parse_args()

  print >> sys.stderr, '# Start: Google Analytics: %s, %s, %s' % (args.cc, args.week, datetime.datetime.now().time().isoformat())

  ga = initialize_service(argv, "analytics")
    
  if args.cc.lower() == "all":
    ccs = ["HK", "ID", "MY", "PH", "SG", "TH", "VN"]
  else:
    ccs = [args.cc]

  query = parse_query(args.queries)

  bar = Bar('Processing', max=len(ccs), suffix ='%(percent).1f%% - %(eta)ds')
  
  headers = ['website']
  headers.extend(query['dimensions'].split(","))
  headers.extend(query['metrics'].split(","))
  print '\t'.join(headers)
  
  for cc in ccs:
    output(call(ga, cc, args.week, query), cc)
    bar.next()
    
  bar.finish()

  print >> sys.stderr, '# End: Keyword Data: %s, %s, %s' % (args.cc, args.week, datetime.datetime.now().time().isoformat())

if __name__ == '__main__':
    main(sys.argv)
