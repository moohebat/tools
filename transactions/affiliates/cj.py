import pandas

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
        + 'presetPeriod%22%3A%22%22%2C%22reportDateType%22%3A%22postingDate%22%7D'
    
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

def detect_cc(website_name):
    # TODO (1): implement
    return pandas.np.nan

def detect_status(status):
    # TODO (1): implement
    return pandas.np.nan
    
def detect_device(os):
    # TODO (1): implement
    return pandas.np.nan

def get_transactions(sdate, edate):
    data = download(sdate, edate)
    
    if len(data) > 0:
        data['ipg:dealType'] = "CPS"
        
        data['ipg:affiliate'] = AFFILIATE
        data['ipg:merchantId'] = data.apply(lambda x: AFFILIATE + str(x['cj:Advertiser CID']), axis=1)
        
        data['ipg:cc'] = data.apply(lambda x: detect_cc(x['cj:Website Name']), axis=1)
        data['ipg:merchantName'] = data['cj:Advertiser Name']
        
        data['ipg:timestamp'] = data.apply(lambda x: parse.parse_datetime(x['cj:Posting Date'], "%d-%b-%Y %H:%M:%S"), axis=1)

        data['ipg:sessionId'] = data['cj:Transaction ID']
        data['ipg:orderId'] = data['cj:Order ID']
        data['ipg:currency'] = "USD"
        data['ipg:orderValue'] = data['cj:Sale Amount (USD)'] 
        data['ipg:commission'] = data['cj:Publisher Commission (USD)'] 
        data['ipg:status'] = data.apply(lambda x: detect_status(data['cj:Status']))
        
        data['ipg:device'] = data.apply(lambda x: detect_device(x['cj:Operating System']), axis=1)

        data['ipg:source'] = data['cj:SID']
    
    return data
