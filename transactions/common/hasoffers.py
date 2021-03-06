from common import parse

import pandas, re, requests, sys

def get_performance(url, key, network, sdate, edate):
    params = {}
    params['Method'] = 'getStats'
    
    params['groups[]'] = [
        'Stat.date',
        'Offer.name',
        'Stat.source'
    ]
    params['fields[]'] = [
        'Stat.date'
    ]
    params['filters[Stat.payout_type][conditional]'] = 'EQUAL_TO'
    params['filters[Stat.payout_type][values]'] = 'cpc'

    return parse_cpc(request(url, key, network, params, sdate, edate, None))
    
def get_conversions(url, key, network, sdate, edate, currency=None):
    params = {}
    params['Method'] = 'getConversions'
    params['fields[]'] = [
        'Stat.advertiser_info', # ad_sub1 query parameter
        'Stat.datetime',
        'Stat.refer', # referer URL
        'Stat.sale_amount', 
        'Stat.ad_id', # transaction ID for the cookie
        'Stat.id', # unique ID for the conversion
        'ConversionsMobile.device_os',
        'Stat.status',
        'Stat.status_code'
    ]
    return parse_cps(request(url, key, network, params, sdate, edate, currency))
    
def request(url, key, network, params, sdate, edate, currency):
    
    output = pandas.DataFrame()
    
    page = 1
    while True:
        params['api_key'] = key
        params['NetworkId'] = network
        params['Target'] = 'Affiliate_Report'
        params['limit'] = 10000
        params['page'] = page
        params['hour_offest'] = '8' # TODO (0): check whether this is correct for all merchants
        params['totals'] = 0
        params['filters[Stat.date][conditional]'] = 'BETWEEN'
        params['filters[Stat.date][values][]'] = [sdate.isoformat(), edate.isoformat()]
        params['fields[]'] += [
            'Browser.display_name',
            'Country.name',
            'Offer.name',
            'Stat.affiliate_info1', # aff_sub1 query parameter
            'Stat.affiliate_info2', # aff_sub2 query parameter
            'Stat.affiliate_info3', # aff_sub3 query parameter
            'Stat.affiliate_info4', # aff_sub4 query parameter
            'Stat.affiliate_info5', # aff_sub5 query parameter
            'Stat.payout',
            'Stat.source'
        ]
        
        if not currency:
            params['fields[]'] += [
                'Stat.currency'
            ]
        
        r = requests.get(url, params=params).json()
        if r['response']['status'] == -1:
            raise Exception(r['response']['errorMessage'])
        
        data = []
        for row in r['response']['data']['data']:
            entry = dict()
            # parse basic fields
            for field in params['fields[]']:
                parts = field.split(".")
                entry['ho:' + field] = row[parts[0]][parts[1]]
            
            # parse currencies
            if not currency:
                for field in r['response']['data']['currency_columns']:
                    parts = field.split(".")
                    if parts[1] in row[parts[0]]:
                        value = row[parts[0]][parts[1]]
                        field = field.split("@")[0]
                        entry['ho:' + field] = value
            else:
                entry['ho:Stat.currency'] = currency
            
            data.append(entry)

        if len(data) > 0:
            output = output.append(data, ignore_index=True)
    
        if r['response']['data']['page'] < r['response']['data']['pageCount']:
            page += 1
        else:
            break

    return output
    
    
def parse_cpc(data):
  if len(data) > 0:
    data['ipg:cc'] = data.apply(lambda x: detect_cc("", x['ho:Stat.affiliate_info2'], x['ho:Offer.name'], x['ho:Country.name']), axis=1)
    data['ipg:merchantName'] = data['ho:Offer.name']
    data['ipg:merchantId'] = pandas.np.nan
    
    data['ipg:timestamp'] = data.apply(lambda x: parse.parse_datetime(x['ho:Stat.date'], "%Y-%m-%d"), axis=1)
    data['ipg:sessionId'] = pandas.np.nan

    data['ipg:orderId'] = pandas.np.nan        
    data['ipg:currency'] = data['ho:Stat.currency']
    data['ipg:orderValue'] = pandas.np.nan 
    data['ipg:commission'] = data['ho:Stat.payout'] 
    data['ipg:status'] = "approved"

    data['ipg:device'] = data.apply(lambda x: detect_device(x['ho:Browser.display_name'], None, x['ho:Offer.name']), axis=1)
    
    data['ipg:source'] = data['ho:Stat.source']
    data['ipg:exitUrl'] =  pandas.np.nan
    
  return data


def parse_cps(data):
  if len(data) > 0:
    data['ipg:cc'] = data.apply(lambda x: detect_cc(x['ho:Stat.refer'], x['ho:Offer.name'], x['ho:Country.name'], x['ho:Stat.affiliate_info2']), axis=1)
    data['ipg:merchantName'] = data['ho:Offer.name']
    data['ipg:merchantId'] = pandas.np.nan
    
    data['ipg:timestamp'] = data.apply(lambda x: parse.parse_datetime(x['ho:Stat.datetime']), axis=1)
    data['ipg:sessionId'] = data['ho:Stat.ad_id']

    data['ipg:orderId'] = data['ho:Stat.advertiser_info']        
    data['ipg:currency'] = data['ho:Stat.currency']
    data['ipg:orderValue'] = data['ho:Stat.sale_amount'] 
    data['ipg:commission'] = data['ho:Stat.payout'] 
    data['ipg:status'] = data['ho:Stat.status']
        
    data['ipg:device'] = data.apply(lambda x: detect_device(x['ho:Browser.display_name'], x['ho:ConversionsMobile.device_os'], x['ho:Offer.name']), axis=1)

    data['ipg:source'] = data['ho:Stat.source']
    data['ipg:exitUrl'] = data['ho:Stat.refer']

  return data


def detect_cc(refer, offer, country, affsub2):
    # refer URL is always true
    cc = parse.detect_cc_refer(refer)
    if pandas.notnull(cc):
        return cc
    
    # backwards compatibiliy, detect from offer name
    cc = parse.detect_cc_name(offer)
    if pandas.notnull(cc):
        return cc    
        
    # if that isn't set either, take the user's country
    cc = parse.detect_cc_name(country)
    if pandas.notnull(cc):
        return cc    
      
    # otherwise use affsub2
    cc = parse.detect_cc_affid(affsub2)
    if pandas.notnull(cc):
        return cc    
        
    return pandas.np.nan

OS = {
    'Desktop' : 'desktop',
    'Mac OS X' : 'desktop',
    'iOS' : 'mobile',
    'Android' : 'mobile',
    'Windows Phone OS' : 'mobile',
    'RIM OS' : 'mobile',
    'Symbian OS' : 'mobile',
    'MeeGo' : 'mobile',
    'Windows RT' : 'mobile',
    'Windows Mobile OS' : 'mobile',
    'MTK/Nucleus OS' : 'mobile'
}

BROWSERS = {
    'Partially Web-Capable Devices' : 'mobile',
    'NetFront Browser (newer devices)' : 'mobile',
    'Android' : 'mobile',
    'iPad' : 'mobile',
    'iPhone / iPod' : 'mobile',
    'BlackBerry (newer devices)' : 'mobile',
    'Firefox' : 'desktop',
    'Internet Explorer' : 'desktop',
    'Chrome' : 'desktop',
    'Safari' : 'desktop',
    'Opera' : 'desktop',
    'Other' : 'desktop'
}
def detect_device(browser, os, offer):
    if os:
        if os in OS:
            return OS[os]
        else:
            print >> sys.stderr, "Couldn't detect device from os: %s" % os
            
    if browser:
        if browser in BROWSERS:
            return BROWSERS[browser]
        else:
            print >> sys.stderr, "Couldn't detect device from browser: %s" % browser
            
    # Lazada: "Mobile app", "App"; Zalora: "App"; ShopStylers: "Mobile" / "Mobile app"
    for word in offer.split(" "):  
        if word.lower() in ["app", "mobile"]:
            return "mobile"

    return pandas.np.nan
