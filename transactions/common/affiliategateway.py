import sys, pandas

from common import parse

from suds.client import Client
from suds.xsd.doctor import Import, ImportDoctor

COUNTRIES = {
    1637: 'SG', 
    2345: 'SG', # quirk SG
    948: 'SG', # SG SG
    1638: 'TH',
    1641: 'MY',
    1621: 'MY', # old MY
    1642: 'ID',
    1624: 'ID', # quirk ID
    1643: 'VN',
    1644: 'PH',
    1645: 'HK',
    }

def request(url, username, password, sdate, edate):
    imp = Import('http://theaffiliategateway.com/data/schemas')
    client = Client(url, doctor=ImportDoctor(imp))

    authentication = client.factory.create('AuthenticationType')
    authentication.username = username
    authentication.apikey = password

    criteria = client.factory.create('CriteriaType')
    
    criteria.StartDateTime = sdate.isoformat() + ' 00:00:00'
    criteria.EndDateTime = edate.isoformat() + ' ' + '00:00:00'

    result = client.service.GetSalesData(authentication, criteria)
    
    data = []
    if result.Transactions:
        for transaction in result.Transactions.Transaction:
            entry = dict()
            for field in transaction:
                entry[field[0]] = field[1]
            data.append(entry)

    output = pandas.DataFrame()
    if len(data) > 0:
        output = output.append(data, ignore_index=True)
        output = output.rename(columns = lambda x : 'ag:' + x)
    
    return output

def detect_cc(refer, program, site_id):
    # refer URL is always true
    cc = parse.detect_cc_refer(refer)
    if pandas.notnull(cc):
        return cc

    # use merchant and product
    cc = parse.detect_cc_name(program)
    if pandas.notnull(cc):
        return cc
        
    # otherwise use site id
    if pandas.notnull(site_id):
        if site_id in COUNTRIES:
            return COUNTRIES[site_id]
        else:
            print >> sys.stderr, "Couldn't detect cc from site id: %s" % site_id
    
    return pandas.np.nan

def detect_status(status):
    if pandas.notnull(status):
        status = status.lower()
        
        if status == "approved":
            return "approved"
        elif status == "declined":
            return "rejected"
        elif status == "pending":
            return "pending"
        
    return pandas.np.nan

def get_transactions(url, username, password, sdate, edate, affiliate):
    data = request(url, username, password, sdate, edate)
    
    if len(data) > 0:
        data['ipg:dealType'] = "CPS"
        data['ipg:affiliate'] = affiliate
        
        data['ipg:cc'] = data.apply(lambda x: detect_cc(x['ag:OriginURL'], x['ag:ProgramName'], x['ag:AffiliateSiteId']), axis=1)
        data['ipg:merchantName'] = data['ag:MerchantName']
        data['ipg:merchantId'] = data.apply(lambda x: affiliate + str(x['ag:MerchantId']), axis=1)
        
        data['ipg:timestamp'] = data.apply(lambda x: parse.parse_datetime(x['ag:TransactionDateTime'], "%d/%m/%Y %H:%M:%S"), axis=1)
        data['ipg:sessionId'] = data.apply(lambda x: parse.generate_id([
            x['ag:AffiliateSubId'], x['ag:ClickDateTime'], x['ag:CreativeId'], x['ag:OriginURL']
        ]), axis=1)
        
        data['ipg:orderId'] = data['ag:TransactionId']
        data['ipg:currency'] = "USD"
        data['ipg:orderValue'] = data['ag:OrderAmount'] 
        data['ipg:commission'] = data['ag:AffiliateCommissionAmount'] 
        data['ipg:status'] = data.apply(lambda x: detect_status (x['ag:ApprovalStatus']), axis=1)
        
        data['ipg:device'] = pandas.np.nan

        data['ipg:source'] = data['ag:AffiliateSubId']
        data['ipg:url'] = data['ag:OriginURL']
    
    return data
