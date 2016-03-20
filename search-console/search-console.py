#!/usr/bin/python

import argparse, datetime, urllib, socket, sys

from datetime import date, timedelta
from googleapiclient import sample_tools
from progress.bar import Bar

reload(sys)
sys.setdefaultencoding("UTF-8")
socket.setdefaulttimeout(10)

GA_IDS = { 'SG':'75448761', 'MY':'75229758','ID':'75897118', 'PH':'75445974', 'TH':'79109064', 'VN':'75895336', 'HK':'75887160' }
GSC_IDS = { 'SG':'iprice.sg', 'MY':'iprice.my', 'ID':'iprice.co.id', 'PH':'iprice.ph', 'TH':'ipricethailand.com', 'VN':'iprice.vn', 'HK':'iprice.hk' }

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))
argparser.add_argument('week', type=int, help=('Week number).'))

YEAR, PAGES, PAGE_SIZE = 2016, 1000, 5000

def get_top_landing_pages(service, cc, week, n):
  data = service.data().ga().get(
    ids='ga:' + GA_IDS[cc],
    start_index='1',
    max_results=n,
    start_date=get_date(YEAR, week)[0],
    end_date=get_date(YEAR, week)[1],
    sort='-ga:sessions',
    dimensions='ga:landingPagePath',
    metrics='ga:sessions',
    filters='ga:medium==organic').execute()
  return data['rows']

def get_keyword_data(service, cc, week, url, protocol):
  retry = 1
  while retry >= 0:
    try:
      tmp = service.searchanalytics().query(
        siteUrl = protocol + "://" + GSC_IDS[cc] + "/",
        body = {
          'startDate' : get_date(YEAR, week)[0],
          'endDate' : get_date(YEAR, week)[1],
          'dimensions' : ['query', 'date'],
          'dimensionFilterGroups': [{
            'filters' : [{
              'dimension': 'page',
              'expression' : protocol + "://" + GSC_IDS[cc] + "/" + urllib.quote(url.encode('utf-8')),
              'operator' : 'equals'
            }]
          }],
          'rowLimit': PAGE_SIZE
        }).execute()

      retry = -1
      if 'rows' in tmp:
        return tmp['rows']

    except Exception:
      retry = retry - 1
      print >> sys.stderr, 'Failed downloading: %s' % (url)

  return []

def get_date(year, week):
    d = date(year,1,1)
    d = d - timedelta(d.weekday())
    dlt = timedelta(days = (week-1)*7)
    return (d + dlt).isoformat(),  (d + dlt + timedelta(days=6)).isoformat()

def initialize_service(argv, id):
  service, flags = sample_tools.init(
      argv, id, 'v3', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/' + id + '.readonly')
  return service

def output(url, traffic, data):
  for row in data:
    print '"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"' % (url, row['keys'][1], row['keys'][0], row['impressions'], row['clicks'], row['ctr'], row['position'], traffic)

def main(argv):
  args = argparser.parse_args()

  print >> sys.stderr, '# Start: Keyword Data: %s, %s, %s' % (args.cc, args.week, datetime.datetime.now().time().isoformat())

  ga, gsc = initialize_service(argv, "analytics"), initialize_service(argv, "webmasters")

  print '"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"' % ("url", "date", "keyword", "impressions", "clicks", "ctr", "position", "sessions (week)")
  
  bar = Bar('Processing', max=PAGES, suffix ='%(percent).1f%% - %(eta)ds')
  urls = get_top_landing_pages(ga, args.cc, args.week, PAGES)
  for row in urls:

    data = []

    # we switched from http to https between week 3 and 4
    if args.week <= 4 and args.cc != 'VN':
      data.extend(get_keyword_data(gsc, args.cc, args.week, row[0][1:], "http"))
    if args.week >=3 or args.cc == 'VN':
      data.extend(get_keyword_data(gsc, args.cc, args.week, row[0][1:], "https"))

    output(row[0], row[1], data)

    bar.next()
  bar.finish()
    
  print >> sys.stderr, '# End: Keyword Data: %s, %s, %s' % (args.cc, args.week, datetime.datetime.now().time().isoformat())

if __name__ == '__main__':
    main(sys.argv)
