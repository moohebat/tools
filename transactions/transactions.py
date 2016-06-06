#!/usr/bin/python
# pip install xlrd

import argparse, calendar, datetime, importlib, requests, os, sys, pandas
from progress.bar import Bar

from common import exchangerates, parse, suspicious

reload(sys)
sys.setdefaultencoding("UTF-8")

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('month', type=str, help=('Year and month).'))
argparser.add_argument('affiliate', type=str, help=('Affiliate or all).'))

def main(argv):
  args = argparser.parse_args()

  print >> sys.stderr, '# Start: Transactions: %s, %s, %s' % (args.month, args.affiliate, datetime.datetime.now().time().isoformat())

  # 0. calculate time frame
  (year, month) = args.month.split("-")
  (year, month) = (int(year), int(month))
  start_date = datetime.date(year, month, 1)
  end_date = datetime.date(year, month, calendar.monthrange(year, month)[1])

  # 1. download, expected format:
  #  ipg:cc, ipg:site, ipg:affiliate, ipg:merchantName, ipg:merchantId, ipg:dealType
  #  ipg:sessionId, ipg:timestamp, ipg:date, ipg:month, ipg:week, ipg:time
  #  ipg:orderId, ipg:status, ipg:currency, ipg:orderValue, ipg:comission
  #  ipg:source, ipg:trackingId, ipg:channel, ipg:device, ipg:product
  data = pandas.DataFrame()
  if args.affiliate.upper() == "ALL":
    for f in os.listdir("affiliates"):
      if f == "__init__.py" or ".pyc" in f:
        continue
      affiliate = importlib.import_module("affiliates.%s" % f.split(".")[0])
      print >> sys.stderr, "# Progress: Downloading %s" % f
      tmp = affiliate.get_transactions(start_date, end_date)
      if len(tmp) > 0:
        data = data.append(tmp, ignore_index=True)
  else:
    try:
        affiliate = importlib.import_module("affiliates.%s" % args.affiliate)
        data = affiliate.get_transactions(start_date, end_date)
    except ImportError, e:
        print >> sys.stderr, "ERORR: Couldn't load affiliate %s" % args.affiliate
  
  if len(data) > 0:
    # 0. set meta data for script vs manual download
    data['ipg:download'] = "SCRIPT"
    
    # 1. dates and times
    data['ipg:date'] = data.apply(lambda x: parse.detect_datetime(x['ipg:timestamp'])[0], axis=1)
    data['ipg:month'] = data.apply(lambda x: parse.detect_datetime(x['ipg:timestamp'])[1], axis=1)
    data['ipg:week'] = data.apply(lambda x: parse.detect_datetime(x['ipg:timestamp'])[2], axis=1)
    data['ipg:time'] = data.apply(lambda x: parse.detect_datetime(x['ipg:timestamp'])[3], axis=1)
    
    # 2. merchant name and id
    # TODO: (0): full list
    data['ipg:merchantId'] = data.apply(lambda x: parse.detect_merchant(x['ipg:merchantName'])[1] if pandas.isnull(x['ipg:merchantId']) else pandas.np.nan, axis=1)
    data['ipg:merchantName'] = data.apply(lambda x: parse.detect_merchant(x['ipg:merchantName'])[0] if pandas.notnull(x['ipg:merchantId']) else x['ipg:merchantName'], axis=1)
    
    # 3. currency conversions
    # TODO (-1): empty order valsue / gmv calculations
    # TODO (-1): cpc value calculations
    # TODO (1): order count
    data['ipg:orderId'] = data.apply(lambda x: parse.detect_orderid(x['ipg:timestamp'], x['ipg:sessionId']) if pandas.isnull(x['ipg:orderId']) else x['ipg:orderId'], axis=1)
    data['ipg:orderValue'] = data.apply(lambda x: exchangerates.convert(x['ipg:orderValue'], x['ipg:date'], x['ipg:currency'], "USD"), axis=1)
    data['ipg:commission'] = data.apply(lambda x: exchangerates.convert(x['ipg:commission'], x['ipg:date'], x['ipg:currency'], "USD"), axis=1)
    data['ipg:currency'] = "USD"
    
    # 4. detect suspicious transactions
    # TODO (0): test orders
    data = suspicious.detect(data)
    
    # 5. enrich information from log database
    data['ipg:trackingId'] = data.apply(lambda x: parse.detect_tracking_id(x['ipg:source']), axis=1)
    # TOOD (0): data = log.enrich(data)
    
    # 6. detect not set fields from source
    data['ipg:site'] = data.apply(lambda x: parse.detect_site(x['ipg:source']), axis=1)
    data['ipg:channel'] = data.apply(lambda x: parse.detect_channel(x['ipg:source']), axis=1)
    data['ipg:product'] = data.apply(lambda x: parse.detect_product(x['ipg:url'], x['ipg:source']), axis=1)
    
    # 7. weight other nan values
    # TODO (0): do it

  # output
  #for c in data.columns.values:
  #  if not c.startswith("ipg:"):
  #    data.drop(c, axis=1, inplace=True)
  data.to_csv(sys.stdout, index=False, na_rep='nan')
  
  print >> sys.stderr, '# End: Transactions: %s, %s, %s' % (args.month, args.affiliate, datetime.datetime.now().time().isoformat())

if __name__ == '__main__':
    main(sys.argv)
