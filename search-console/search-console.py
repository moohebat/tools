#!/usr/bin/python
# pip install --upgrade google-api-python-client
# pip install progress

import argparse, datetime, urllib, socket, sys

from datetime import date, timedelta
from googleapiclient import sample_tools
from progress.bar import Bar

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
GSC_IDS = { 
  'SG': {
    'IPRICE' : 'iprice.sg'
  },
  'MY': {
    'IPRICE' : 'iprice.my',
    'SAYS' : 'coupon.says.com',
    'JUICE' : 'www.juiceonline.com/promotions'
  },
  'ID': {
    'IPRICE' : 'iprice.co.id'
  },
  'PH' : {
    'IPRICE' : 'iprice.ph',
    'RAPPLER' : 'coupons.rappler.com'
  }, 
  'TH': {
    'IPRICE' : 'ipricethailand.com'
  },
  'VN': {
    'IPRICE' : 'iprice.vn' 
  },
  'HK': {
    'IPRICE' : 'iprice.hk'
  }
}

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))
argparser.add_argument('week', type=str, help=('Week number).'))
argparser.add_argument('pages', type=int, help=('Top N pages).'))

PAGE_SIZE = 5000

def get_top_landing_pages(service, cc, website, week, n):
  data = service.data().ga().get(
    ids='ga:' + GA_IDS[cc][website],
    start_index='1',
    max_results=n,
    start_date=get_date(week)[0],
    end_date=get_date(week)[1],
    sort='-ga:sessions',
    dimensions='ga:landingPagePath',
    metrics='ga:sessions',
    filters='ga:medium==organic').execute()
  return data['rows']

def get_keyword_data(service, cc, website, week, url, protocol):
  retry = 1
  while retry >= 0:
    try:
      tmp = service.searchanalytics().query(
        siteUrl = protocol + "://" + GSC_IDS[cc][website] + "/",
        body = {
          'startDate' : get_date(week)[0],
          'endDate' : get_date(week)[1],
          'dimensions' : ['query', 'date'],
          'dimensionFilterGroups': [{
            'filters' : [{
              'dimension': 'page',
              'expression' : protocol + "://" + GSC_IDS[cc][website] + "/" + urllib.quote(url.encode('utf-8')),
              'operator' : 'equals'
            }]
          }],
          'rowLimit': PAGE_SIZE
        }).execute()

      retry = -1
      if 'rows' in tmp:
        return tmp['rows']

    except Exception, e:
      retry = retry - 1
      print >> sys.stderr, 'Failed downloading: %s (%s)' % (url, e)

  return []

def get_date(week):
    year, week = week.split("-")
    d = date(int(year),1,1)
    d = d - timedelta(d.weekday())
    dlt = timedelta(days = int(week)*7)
    return (d + dlt).isoformat(),  (d + dlt + timedelta(days=6)).isoformat()

def initialize_service(argv, id):
  service, flags = sample_tools.init(
      argv, id, 'v3', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/' + id + '.readonly')
  return service

def output(cc, website, url, traffic, data):
  for row in data:
    print '"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"' % (cc, website, url, row['keys'][1], row['keys'][0], row['impressions'], row['clicks'], row['ctr'], row['position'], traffic)

def main(argv):
  args = argparser.parse_args()

  print >> sys.stderr, '# Start: Keyword Data: %s, %s, %s, %s' % (args.cc, args.week, args.pages, datetime.datetime.now().time().isoformat())

  ga, gsc = initialize_service(argv, "analytics"), initialize_service(argv, "webmasters")

  print '"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"' % ("cc", "website", "url", "date", "keyword", "impressions", "clicks", "ctr", "position", "sessions (week)")
  
  bar = Bar('Processing', max=args.pages, suffix ='%(percent).1f%% - %(eta)ds')
  
  for website in GA_IDS[args.cc]:

    urls = get_top_landing_pages(ga, args.cc, website, args.week, args.pages)
    for row in urls:

      data = []

      # we switched from http to https between week 3 and 4
      if (args.week <= 4 and args.cc != 'VN') or website != "IPRICE":
        data.extend(get_keyword_data(gsc, args.cc, website, args.week, row[0][1:], "http"))
      if (args.week >=3 or args.cc == 'VN') and website == "IPRICE":
        data.extend(get_keyword_data(gsc, args.cc, website, args.week, row[0][1:], "https"))

      output(args.cc, website, row[0], row[1], data)

      bar.next()
    bar.finish()
      
  print >> sys.stderr, '# End: Keyword Data: %s, %s, %s, %s' % (args.cc, args.week, args.pages, datetime.datetime.now().time().isoformat())

if __name__ == '__main__':
    main(sys.argv)
