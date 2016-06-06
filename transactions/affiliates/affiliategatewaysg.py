from common import affiliategateway

URL = 'https://www.tagadmin.sg/ws/AffiliateSOAP.wsdl'
USERNAME = 'affiliate@ipricegroup.com'
PASSWORD = 'ipricerocks2015'

def get_transactions(sdate, edate):
    return affiliategateway.get_transactions(URL, USERNAME, PASSWORD, sdate, edate, "AGSG")
