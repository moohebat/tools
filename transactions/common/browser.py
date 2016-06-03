import os, pandas, sys, tempfile, time

from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

TIMEOUT = 60
TMP_DIR = tempfile.mkdtemp()

def setup_driver():
    profile = FirefoxProfile()
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
        "text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.dir", TMP_DIR)
    
    driver = webdriver.Firefox(firefox_profile=profile)
    driver.implicitly_wait(TIMEOUT)
    
    return driver

def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + TIMEOUT:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    raise Exception('Timeout waiting for {}'.format(condition_function.__name__))
    
class wait_for_page_load(object):
    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)

def download(filename):
    absolute = os.path.join(TMP_DIR, filename)
    
    timeout = TIMEOUT
    while True:
        time.sleep(3)
        timeout = timeout - 3
        if not os.path.isfile(absolute + ".part"):
            break
        elif timeout == 0:
            print >> sys.stderr, "ERROR: Downloading %s timeout" % filename
            break 

    # TODO (1): remove    
    print >> sys.stderr, absolute
    if os.path.isfile(absolute):
        if ".xls" in filename:
            df = pandas.read_excel(absolute)
        else:
            df = pandas.read_csv(absolute)
    else:
        df = pandas.DataFrame()
    
    return df

def close_driver(driver):
    driver.close()
    # TODO (1): cleanup tmpdir
