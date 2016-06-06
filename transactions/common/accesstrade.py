from common import browser, parse
import pandas

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

def request(url, username, password, sitecode, sdate, edate):
    driver = browser.setup_driver()
    
    # login
    driver.get(url)
    login_user = driver.find_element_by_id('login-username')
    login_user.send_keys(username)
    login_pass = driver.find_element_by_id('login-password')
    login_pass.send_keys(password, Keys.RETURN)
        
    # select english
    dropdown = driver.find_element_by_id('flag')
    dropdown.click()
    English = dropdown.find_element_by_tag_name('li')
    English.click()
    
    # go to report
    driver.get(url + '/p/report-result')

    # select date
    date = driver.find_element_by_id('datePeriod')
    date.clear()
    date.send_keys(sdate.strftime('%B %Y'))
    
    # select site
    sites = Select(driver.find_element_by_id('siteNo'))
    sites.select_by_value(sitecode)
    
    # wait for campaigns being loaded
    date = driver.find_element_by_css_selector('#listCampaign > option')
    
    # search    
    with browser.wait_for_page_load(driver):
        btn = driver.find_element_by_name('btnSearch')
        btn.click()

    # download    
    driver.execute_script("document.getElementById('ToolTables_tblView_3').click()")
    
    filename = 'ExportAdditionalParamemter_%s_%s.xls' % (sitecode, sdate.strftime('%Y%m'))
    df = browser.download(filename)
    df = df.rename(columns = lambda x : 'at:' + x)
    
    browser.close_driver(driver)
    
    return df

def detect_status(status):
    if pandas.notnull(status):
        status = status.lower()
        
        if status == "approved":
            return "approved"
        elif status == "reject":
            return "rejected"
        elif status == "pending":
            return "pending"
        
    return pandas.np.nan


def get_transactions(url, username, password, sitecode, affiliate, sdate, edate):
    data = request(url, username, password, sitecode, sdate, edate)
    
    if len(data) > 0:
        data['ipg:dealType'] = "CPS"
        data['ipg:affiliate'] = "AT" + affiliate
        
        data['ipg:cc'] = affiliate
        data['ipg:merchantName'] = data['at:Campaign Name']
        data['ipg:merchantId'] = pandas.np.nan
        
        data['ipg:timestamp'] = data.apply(lambda x: parse.parse_datetime(x['at:Occur Date'], "%Y/%m/%d %H:%M:%S"), axis=1)
        data['ipg:sessionId'] = data['at:Session ID']

        data['ipg:orderId'] = data['at:seqNo']
        data['ipg:currency'] = "THB"
        data['ipg:orderValue'] = data['at:Total Price'] 
        data['ipg:commission'] = data['at:Reward Amount'] 
        data['ipg:status'] = data.apply(lambda x: parse.parse_status(data['at:Status']), axis=1)
        
        data['ipg:device'] = pandas.np.nan

        # TODO (0): at:coupon and at:shop
        data['ipg:source'] = data['at:subid']
        data['ipg:url'] = pandas.np.nan
    
    return data
