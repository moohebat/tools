#!/usr/bin/python
# TODO: Retry logic

import argparse, datetime, urllib, sys

from datetime import date, timedelta
from googleapiclient import sample_tools
from progress.bar import Bar

reload(sys)
sys.setdefaultencoding("UTF-8")

GA_IDS = {
'SG':'75448761',
'MY':'75229758',
'ID':'75897118',
'PH':'75445974',
'TH':'79109064',
'VN':'75895336',
'HK':'75887160',
}

GSC_IDS = {
'SG':'https://iprice.sg/',
'MY':'https://iprice.my/',
'ID':'https://iprice.co.id/',
'PH':'https://iprice.ph/',
'TH':'https://ipricethailand.com/',
'VN':'https://iprice.vn/',
'HK':'https://iprice.hk/',
}

GSC_OLD_IDS = {
'SG':'http://iprice.sg/',
'MY':'http://iprice.my/',
'ID':'http://iprice.co.id/',
'PH':'http://iprice.ph/',
'TH':'http://ipricethailand.com/',
'VN':'http://iprice.vn/',
'HK':'http://iprice.hk/',
}


argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))
argparser.add_argument('week', type=int, help=('Week number).'))

year = 2016
pages = 10

def get_top_landing_pages(service, cc, week, n):
  data = service.data().ga().get(
    ids='ga:' + GA_IDS[cc],
    start_index='1',
    max_results=n,
    start_date=get_date(year, week)[0],
    end_date=get_date(year, week)[1],
    sort='-ga:sessions',
    dimensions='ga:landingPagePath',
    metrics='ga:sessions',
    filters='ga:medium==organic').execute()
  return data['rows']

def get_keyword_data(service, cc, week, url):

  if week in [3, 4] and cc != 'VN':
    old, new = True, True
  elif week in [1, 2] and cc != 'VN':
    old, new = True, False
  else:
    old, new = True, False

  data = []

  if old:
    tmp = service.searchanalytics().query(
      siteUrl=GSC_OLD_IDS[cc],
      body={
        'startDate' : get_date(year, week)[0],
        'endDate' : get_date(year, week)[1],
        'dimensions' : ['query', 'date'],
        'dimensionFilterGroups': [{
          'filters' : [{
            'dimension': 'page',
            'expression' : GSC_OLD_IDS[cc] + urllib.quote(url.encode('utf-8')),
            'operator' : 'equals'
          }]
        }],
        'rowLimit': 5000
      }).execute()

    if 'rows' in tmp:
      data.extend(tmp['rows'])

  if new: 
    tmp = service.searchanalytics().query(
      siteUrl=GSC_IDS[cc],
      body={
        'startDate' : get_date(year, week)[0],
        'endDate' : get_date(year, week)[1],
        'dimensions' : ['query', 'date'],
        'dimensionFilterGroups': [{
          'filters' : [{
            'dimension': 'page',
            'expression' : GSC_IDS[cc] + urllib.quote(url.encode('utf-8')),
            'operator' : 'equals'
          }]
        }],
        'rowLimit': 5000
      }).execute()

    if 'rows' in tmp:
      data.extend(tmp['rows'])

  return data

def get_date(year, week):
    d = date(year,1,1)
    d = d - timedelta(d.weekday())
    dlt = timedelta(days = (week-1)*7)
    return (d + dlt).isoformat(),  (d + dlt + timedelta(days=6)).isoformat()

def initialize_ga(argv):
  service, flags = sample_tools.init(
      argv, 'analytics', 'v3', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/analytics.readonly')
  return service

def initialize_gsc(argv):
  service, flags = sample_tools.init(
      argv, 'webmasters', 'v3', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/webmasters.readonly')
  return service

def output(url, traffic, data):
  for row in data:
    print '"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"' % (url, row['keys'][1], row['keys'][0], row['impressions'], row['clicks'], row['ctr'], row['position'], traffic)

def main(argv):
  args = argparser.parse_args()

  print >> sys.stderr, '# Start: Keyword Data: %s, %s, %s' % (args.cc, args.week, datetime.datetime.now().time().isoformat())

  ga = initialize_ga(argv)
  gsc = initialize_gsc(argv)

  print '"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"' % ("url", "date", "keyword", "impressions", "clicks", "ctr", "position", "sessions (week)")
  
  bar = Bar('Processing', max=pages, suffix ='%(percent).1f%% - %(eta)ds')
  urls = get_top_landing_pages(ga, args.cc, args.week, pages)
  for row in urls:
    data = get_keyword_data(gsc, args.cc, args.week, row[0][1:])
    output(row[0], row[1], data)

    bar.next()
  bar.finish()
    
  print >> sys.stderr, '# End: Keyword Data: %s, %s, %s' % (args.cc, args.week, datetime.datetime.now().time().isoformat())

if __name__ == '__main__':
    main(sys.argv)
