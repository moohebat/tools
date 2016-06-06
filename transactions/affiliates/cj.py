import md5, pandas, sys

from common import browser, parse
from datetime import timedelta
from selenium.webdriver.common.keys import Keys

URL = 'https://members.cj.com/member/login'
USERNAME = 'affiliate@ipricegroup.com'
PASSWORD = 'ipricerocks2015'
AFFILIATE = 'CJ'

def download(sdate, edate):
    driver = browser.setup_driver()
    
    # login
    driver.get(URL)
    emailtxt = driver.find_element_by_name('uname')
    passtxt = driver.find_element_by_name('pw')
    emailtxt.send_keys(USERNAME)
    passtxt.send_keys(PASSWORD)
    
    with browser.wait_for_page_load(driver):
        login = driver.find_element_by_name('go')
        login.click()

    # report
    transaction_url = 'https://members.cj.com/member/4018940/publisher/navigate_reports.cj#?tab=transaction&criteria=' \
        + '%7B%22filters%22%3A%5B%5D%2C%22columnSorts%22%3A%5B%5D%2C%22reportGroupId%22%3A%22transaction%22%2C%22reportId%22%3A%22commissionDetail%22%2C%22reportName%22%3A%22Commission%20Detail%22%2C%22' \
        + 'startDate%22%3A%22' + (sdate - timedelta(days=1)).strftime('%Y-%m-%d') + 'T16%3A00%3A00.000Z%22%2C%22' \
        + 'endDate%22%3A%22' + (edate - timedelta(days=1)).strftime('%Y-%m-%d') + 'T16%3A00%3A00.000Z%22%2C%22' \
        + 'presetPeriod%22%3A%22%22%2C%22reportDateType%22%3A%22eventDate%22%7D'
    
    with browser.wait_for_page_load(driver):
        driver.get(transaction_url)
        driver.find_element_by_class_name('publisherCommissionTotals');

    # download
    driver.execute_script("document.getElementById('transactionDownloadButton').click();")
    driver.execute_script("document.getElementById('fileName').value='cj_transaction';")
    driver.execute_script("document.getElementsByClassName('primary-btn btn-d small-btn')[0].click();")

    df = browser.download('cj_transaction.csv')
    df = df.rename(columns = lambda x : 'cj:' + x)
    
    browser.close_driver(driver)
    
    return df

def detect_cc(refer, advertiser, site):
    # refer URL is always true
    cc = parse.detect_cc_refer(refer)
    if pandas.notnull(cc):
        return cc

    # if that isn't set either, take the advertiser name
    cc = parse.detect_cc_name(advertiser)
    if pandas.notnull(cc):
        return cc

    # otherwise fall back to the site name
    cc = parse.detect_cc_name(site)
    if pandas.notnull(cc):
        return cc

    return pandas.np.nan

def detect_status(status, value):
    if pandas.notnull(status):
        status = status.lower()
        
        if value < 0:
            return "rejected"
        
        if status == "new":
            return "pending"
        elif status == "extended":
            return "pending"
        elif status == "locked":
            return "approved"
        elif status == "closed":
            return "approved"
        
    return pandas.np.nan

OS = {
    'Windows' : 'desktop',
    'Windows XP' : 'desktop',
    'Windows Vista' : 'desktop',
    'Windows 7' : 'desktop',
    'Windows RT' : 'desktop',
    'Windows 8' : 'desktop',
    'Windows 8.1' : 'desktop',
    'Windows 10' : 'desktop',
    'Mac OS X' : 'desktop',
    'Linux' : 'desktop',
    'Ubuntu' : 'desktop',
    'Chrome OS' : 'desktop',
    'Android' : 'mobile',
    'Android 4.x' : 'mobile',
    'Android 5.x' : 'mobile',
    'Android 4.x Tablet' : 'mobile',
    'Android 5.x Tablet' : 'mobile',
    'iOS' : 'mobile',
    'iOS 6 (iPhone)' : 'mobile',
    'Windows Phone' : 'mobile',
    'RIM' : 'mobile',
    'BlackBerryOS' : 'mobile'
}
def detect_device(os):
    if pandas.notnull(os):
        if os in OS:
            return OS[os]
        elif pandas.notnull(os) and os != "Unknown":
            print >> sys.stderr, "Couldn't detect device from os: %s" % os

    return pandas.np.nan

def convert_transactions(data):
    # first sort by orderId (so we can iterate) and orderValue (so that the actual value is first)
    data.sort_values(["ipg:orderId", "ipg:orderValue"], ascending=False, inplace=True)
    
    orderIndex = None
    count = 0
    for index, row in data.iterrows():
        if orderIndex and data.loc[index]['ipg:orderId'] == data.loc[orderIndex]['ipg:orderId']:
            count = count + 1
            if data.loc[index]['ipg:orderValue'] < 0:
                # substract amount from first basket
                data.set_value(orderIndex, 'ipg:orderValue', data.loc[orderIndex]['ipg:orderValue'] + data.loc[index]['ipg:orderValue'])
                data.set_value(orderIndex, 'ipg:commission', data.loc[orderIndex]['ipg:commission'] + data.loc[index]['ipg:commission'])
                
                # make these positive values 
                data.set_value(index, 'ipg:orderValue', -1 * data.loc[index]['ipg:orderValue'])
                data.set_value(index, 'ipg:commission', -1 * data.loc[index]['ipg:commission'])
        else:
            orderIndex = index
            count = 0
        
    return data

def get_transactions(sdate, edate):
    #data = download(sdate, edate)
    
    data = pandas.read_csv("/Users/Heinrich/Downloads/commission_detail_1-jan-2015_-_31-dec-2015_event_date.csv")
    data = data.rename(columns = lambda x : 'cj:' + x)
    
    if len(data) > 0:
        data['ipg:dealType'] = "CPS"
        data['ipg:affiliate'] = AFFILIATE
        
        data['ipg:cc'] = data.apply(lambda x: detect_cc(x['cj:Click Referring URL'], x['cj:Advertiser Name'], x['cj:Website Name']), axis=1)
        data['ipg:merchantName'] = data['cj:Advertiser Name']
        data['ipg:merchantId'] = data.apply(lambda x: AFFILIATE + str(x['cj:Advertiser CID']), axis=1)
        
        data['ipg:timestamp'] = data.apply(lambda x: parse.parse_datetime(x['cj:Event Date'], "%d-%b-%Y %H:%M:%S"), axis=1)
        data['ipg:sessionId'] = data.apply(lambda x: parse.generate_id([
            x['cj:Click Date'], x['cj:SID'], x['cj:Operating System'], x['cj:Action Name'], x['cj:Website Name'], x['cj:Ad ID'], x['cj:Click Referring URL']
        ]), axis=1)
        
        data['ipg:orderId'] = data['ipg:cc'] + data.apply(lambda x: filter(str.isdigit, x['cj:Order ID']) or x['cj:Order ID'], axis=1)
        data['ipg:currency'] = "USD"
        data['ipg:orderValue'] = data['cj:Sale Amount (USD)'] 
        data['ipg:commission'] = data['cj:Publisher Commission (USD)'] 
        data['ipg:status'] = data.apply(lambda x: detect_status(x['cj:Status'], x['ipg:orderValue']), axis=1)
        
        data['ipg:device'] = data.apply(lambda x: detect_device(x['cj:Operating System']), axis=1)

        data['ipg:source'] = data['cj:SID']
        data['ipg:url'] = data['cj:Click Referring URL']

    if len(data) > 0:
        data = convert_transactions(data)
    
    return data
