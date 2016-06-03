from common import accesstrade

URL = 'https://member.accesstrade.in.th'
USERNAME = 'kavitha.daniel@ipricegroup.com'
PASSWORD = 'ipricerocks2015'
SITE_CODE = '4869'

def get_transactions(sdate, edate):
    return accesstrade.get_transactions(URL, USERNAME, PASSWORD, SITE_CODE, 'TH', sdate, edate)
