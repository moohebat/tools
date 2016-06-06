from common import browser, parse
import pandas, sys

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

BASEURL = 'https://www.optimise.my/login/'
USERNAME = 'affiliate@ipricegroup.com'
PASSWORD = 'Ipricerocks2015'

def download(sdate, edate):
    driver = browser.setup_driver()
    driver.get(BASEURL)
    
    # login
    username = driver.find_element_by_id('emailaddress')
    username.send_keys(USERNAME)
    password = driver.find_element_by_id('password')
    password.send_keys(PASSWORD)
        
    with browser.wait_for_page_load(driver):
        login = driver.find_element_by_id('Submit')
        login.click()
    
    # report parameters
    driver.get('https://admin.optimisemedia.com/v2/reports/affiliate/leads/leadSummaryReport.aspx')
    
    startdate = driver.find_element_by_id('ContentPlaceHolder1_dpStart_txtProcessDate')
    startdate.clear()
    startdate.send_keys(sdate.isoformat()   )

    enddate = driver.find_element_by_id('ContentPlaceHolder1_dpEnd_txtProcessDate')
    enddate.clear()
    enddate.send_keys(edate.isoformat())
    
    searchdate = Select(driver.find_element_by_id('ContentPlaceHolder1_DDLSearchDate'))
    searchdate.select_by_visible_text("Transaction Date")

    with browser.wait_for_page_load(driver):
        reportbtn = driver.find_element_by_id('ContentPlaceHolder1_ButtonGet')
        reportbtn.click()
    
    # download 
    excelbtn = driver.find_element_by_id('ContentPlaceHolder1_btnXlsExport')
    excelbtn.click()

    df = browser.download('LeadSummaryReport.xlsx')
    df = df.rename(columns = lambda x : 'omg:' + x)
    
    browser.close_driver(driver)
    
    return df

def detect_cc(refer, merchant, product, uid2):
    # refer URL is always true
    cc = parse.detect_cc_refer(refer)
    if pandas.notnull(cc):
        return cc

    # use merchant and product
    cc = parse.detect_cc_name(merchant)
    if pandas.notnull(cc):
        return cc    
    
    cc = parse.detect_cc_name(product)
    if pandas.notnull(cc):
        return cc   
        
    # otherwise use uid2
    cc = parse.detect_cc_affid(uid2)
    if pandas.notnull(cc):
        return cc    

    return pandas.np.nan

def detect_status(status):
    if pandas.notnull(status):
        status = status.lower()
        
        if status == "validated":
            return "approved"
        elif status == "rejected":
            return "rejected"
        elif status == "pending":
            return "pending"
        
    return pandas.np.nan

def get_transactions(sdate, edate):
    data = download(sdate, edate)

    if len(data) > 0: 
        data['ipg:dealType'] = "CPS"
        data['ipg:affiliate'] = "OMG"
        
        data['ipg:cc'] = data.apply(lambda x: detect_cc(x['omg:Referrer'], x['omg:Merchant'], x['omg:Product'], x['omg:UID2']), axis=1)
        data['ipg:merchantId'] = data.apply(lambda x: "OM" + str(x['omg:MID']), axis=1)
        data['ipg:merchantName'] = data['omg:Merchant']
        
        data['ipg:timestamp'] = data.apply(lambda x: parse.parse_datetime(x['omg:Transaction Time'].isoformat().replace("T", " ")), axis=1)

        data['ipg:sessionId'] = data['omg:TransactionID']
        data['ipg:orderId'] = data['omg:Merchant Ref']
        data['ipg:currency'] = data.apply(lambda x: x['omg:Currency'].strip(), axis=1)
        data['ipg:orderValue'] = data['omg:Transaction Value'] 
        data['ipg:commission'] = data['omg:SR'] 
        data['ipg:status'] = data['omg:Status']
    
        # TODO: calculate split on separate report
        data['ipg:device'] = pandas.np.nan

        data['ipg:source'] = data['omg:UID']
        data['ipg:url'] = data['omg:Referrer']
        
    return data
