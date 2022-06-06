from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.proxy import Proxy, ProxyType
import stem
from datetime import datetime
import stem.process
import os
import getpass
import logging
import time
import json
from selenium.webdriver.common.action_chains import ActionChains
import db_controller
import utils
import crawler_conti
import crawler_hive
import crawler_ragnar_locker
import crawler_lockbit
import crawler_lorenz
import crawler_midas
import crawler_pysa
import crawler_quantum
import crawler_ransomexx
import crawler_snatch
import shutil

# Scraping data
SPAN_CLASS_AUTHOR = 'X43Kjb'
DIV_CLASS_STARS = 'pf5lIe'
SPAN_CLASS_TIMESTAMP = 'p2TkOb'
SPAN_JSNAME_DESCRIPTION = 'bN97Pc'
DIV_CLASS_REPLY = 'LVQB0b'
SPAN_CLASS_REPLY_AUTHOR = 'X43Kjb'
SPAN_CLASS_REPLY_TIMESTAMP = 'p2TkOb'

OUTPUT_DIR = '.'

# Setup logging stuff
LOG_DIR = 'logs/'
LOG_TO_FILE = False
log_format = "%(asctime)s %(name)s [%(levelname)s] %(message)s"
log = logging.getLogger(__name__)
logFile = LOG_DIR+"crawl_"+datetime.now().strftime('%Y%m%d_%H%M%S')+".log"
if LOG_TO_FILE:
    logging.basicConfig(filename=logFile, format=log_format,
                        level=logging.INFO, datefmt='%d-%m-%Y_%H:%M:%S')
else:
    logging.basicConfig(format=log_format, level=logging.INFO,
                        datefmt='%d-%m-%Y_%H:%M:%S')
logging.getLogger("selenium").setLevel(logging.ERROR)
logging.getLogger("stem").setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)


# Path to Firefox binary
# FIREFOX_BINARY='/Applications/Firefox.app/Contents/MacOS/firefox'
FIREFOX_BINARY = 'C:\Program Files\Mozilla Firefox\Firefox.exe'


# Returns a driver using Firefox 
def get_driver(port, useragent):
    # Settings
    webdriver.DesiredCapabilities.FIREFOX[
        "firefox.page.customHeaders.User-Agent"] = useragent
    webdriver.DesiredCapabilities.FIREFOX[
        'firefox.page.customHeaders.Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    webdriver.DesiredCapabilities.FIREFOX['firefox.page.customHeaders.Accept-Language'] = "en-US,en;q=0.5"
    caps = webdriver.DesiredCapabilities.FIREFOX.copy()

    # Set preferences to access .onion
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('javascript.enabled', True)  # This preference doesn't work (era false, Firefox siempre a True igual)
    firefox_profile.set_preference('network.dns.blockDotOnion', False)
    firefox_profile.set_preference('network.proxy.socks_remote_dns', True)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')  
    firefox_profile.set_preference('dom.webdriver.enabled', False)
    firefox_profile.set_preference('useAutomationExtension', False)

    firefox_profile.set_preference('permissions.default.image', 2)      # añadido para no descargar imágenes

    firefox_profile.set_preference("network.proxy.type", 1)
    firefox_profile.set_preference("network.proxy.http", '127.0.0.1')
    firefox_profile.set_preference("network.proxy.http_port", int(port))
    firefox_profile.update_preferences()

    # Options
    options = Options()
    options.binary = FIREFOX_BINARY
    options.profile = firefox_profile
    options.add_argument('--headless')      # IN BACKGROUND

    caps.update(options.to_capabilities())

    # Obtain driver
    driver = webdriver.Firefox(desired_capabilities=caps, options=options)
    # create action chain object
    action = ActionChains(driver)

    set_proxy(driver, socks_addr='127.0.0.1', socks_port=str(port))

    return driver, action


# Set proxy to connect .onion
def set_proxy(driver, http_port='', http_addr='', ssl_addr='', ssl_port=0, socks_addr='', socks_port=5):
    driver.execute("SET_CONTEXT", {"context": "chrome"})
    try:
        driver.execute_script("""
			Services.prefs.setIntPref('network.proxy.type', 1);
			Services.prefs.setCharPref("network.proxy.http", arguments[0]);
			Services.prefs.setIntPref("network.proxy.http_port", arguments[1]);
			Services.prefs.setCharPref("network.proxy.ssl", arguments[2]);
			Services.prefs.setIntPref("network.proxy.ssl_port", arguments[3]);
			Services.prefs.setCharPref('network.proxy.socks', arguments[4]);
			Services.prefs.setIntPref('network.proxy.socks_port', arguments[5]);
			""", http_addr, http_port, ssl_addr, ssl_port, socks_addr, socks_port)
    finally:
        driver.execute("SET_CONTEXT", {"context": "content"})


# Scrapes the content. ASsumes all content has been loaded by scrolling down
def scrape_all_content(driver):
    reviews = []
    all_reviews = driver.find_elements_by_xpath('//div[@jsname="fk8dgd"]/div')
    for rev in all_reviews:
        try:
            full_button = rev.find_elements_by_xpath(
                './/button[contains(text(),"Full Review")]')
            full_button.click()
        except:
            pass
        starts_element = rev.find_element_by_xpath(
            './/div[contains(@aria-label,"Rated")]')
        numStars = int(starts_element.get_attribute('aria-label').split()[1])
        author = rev.find_element_by_xpath(
            './/span[@class="%s"]' % SPAN_CLASS_AUTHOR).text
        timestamp = rev.find_element_by_xpath(
            './/span[@class="%s"]' % SPAN_CLASS_TIMESTAMP).text
        description = rev.find_element_by_xpath(
            './/span[@jsname="%s"]' % SPAN_JSNAME_DESCRIPTION).text
        try:
            numVotes = int(rev.find_element_by_xpath(
                './/div[contains(@aria-label,"Number of times this review was rated helpful")]').text)
        except ValueError:
            numVotes = 0
        has_reply = False
        try:
            reply_element = rev.find_element_by_xpath(
                './/div[@class="%s"]' % DIV_CLASS_REPLY)
            has_reply = True
        except:
            pass
        if has_reply:
            reply_author = reply_element.find_element_by_xpath(
                './/span[@class="%s"]' % SPAN_CLASS_REPLY_AUTHOR).text
            reply_timestamp = reply_element.find_element_by_xpath(
                './/span[@class="%s"]' % SPAN_CLASS_REPLY_TIMESTAMP).text
            reply_text = reply_element.text.split('\n')[1]
            reviews.append({'author': author, 'timestamp': timestamp, 'numStars': numStars, 'upVotes': numVotes, 'review': description, 'reply': {
                           'rAuthor': reply_author, 'rTimestamp': reply_timestamp, 'rText': reply_text}})
        else:
            reviews.append({'author': author, 'timestamp': timestamp, 'numStars': numStars,
                           'upVotes': numVotes, 'review': description, 'reply': {}})
    return {i+1: reviews[i] for i in range(0, len(reviews))}


# Once scrolled, call the get_all_content method
def scroll_down(driver):
    newContentLoaded = True
    all_reviews = driver.find_elements_by_xpath('//div[@jsname="fk8dgd"]/div')
    current = len(all_reviews)
    while (newContentLoaded):
        prev = current
        driver.execute_script("""
		window.scrollTo(0, document.body.scrollHeight)
		""")
        time.sleep(2)
        all_reviews = driver.find_elements_by_xpath(
            '//div[@jsname="fk8dgd"]/div')
        current = len(all_reviews)
        # print ('Prev: %d, Current:%d'%(prev,current))
        newContentLoaded = current != prev
        if not newContentLoaded:
            try:
                element = driver.find_element_by_xpath(
                    '//span[contains(text(),"Show More")]')
                newContentLoaded = True
                element.click()
            except:
                newContentLoaded = False

# Invoke a Tor process which is subsequently used.


def bootstrap_tor(port, exitNode, dataDir):
    if not os.path.exists(dataDir):
        os.makedirs(dataDir)
    try:
        proc = stem.process.launch_tor_with_config(
            config={
                "SOCKSPort": str(port),
                "ExitNodes": exitNode,
                "DataDirectory": dataDir,
            },
            # timeout=300,				# OSError-You cannot launch tor with a timeout on Windows
            take_ownership=True,
            completion_percent=80,
        )
        log.info("Successfully started Tor process (PID=%d)." % proc.pid)
    except OSError as e:
        log.warning("Couldn't launch Tor on socks port %s: %s-%s " %
                    (port, e.__class__.__name__, e))
        return None
    return proc


def read_relay_useragent():
    return '2bd1936e0b4d5bb615cf99b0cff74eaf19426888', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0'
    # return '2bd1936e0b4d5bb615cf99b0cff74eaf19426888','Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:59.0) Gecko/20100101 Firefox/59.0'



def main():
    relay, useragent = read_relay_useragent()
    log.info(' Relay:'+relay+' UA:'+useragent)
    torPort = 9065
    # usernameOS = getpass.getuser()
    # dirName="/home/"+usernameOS+"/tmdp/torDataDir"
    dirName = '/tmp/torDataDir'
    dataDir = dirName+str(torPort)
    log.info("Trying to launch Tor on port %s using data dir:%s" %
             (torPort, dataDir))
    while (not bootstrap_tor(torPort, relay, dataDir)):
        torPort = torPort+1
        dataDir = dirName+str(torPort)
        log.info("Trying to launch Tor on port %s using data dir:%s" %
                 (torPort, dataDir))
    # Get a driver connection
    log.info("Getting Firefox driver")
    driver = get_driver(torPort, useragent)


    # Open connection DB
    con = db_controller.sql_connection()
    
    # Create new DB
    db_controller.sql_create(con)

    print("\nEntering Families Site Page...")
    
    familiesSite = ""       # URL to Ransomware Families Sites
    driver[0].get(familiesSite)

    
    # Crawlers ('con' for DB, 'familiesSite' to return to main page after each crawler)
      
    crawler_conti.crawl_conti(driver[0], con, familiesSite)                         # 45'
    crawler_ragnar_locker.crawl_ragnar_locker(driver[0], con, familiesSite)         # 4'   
    crawler_hive.crawl_hive(driver[0], con, familiesSite)                           # 2'
    crawler_lockbit.crawl_lockbit(driver[0], con, familiesSite)                     # 60'
    crawler_lorenz.crawl_lorenz(driver[0], con, familiesSite)                       # 5'
    #crawler_midas.crawl_midas(driver[0], con, familiesSite)                        # 4' (down)
    #crawler_pysa.crawl_pysa(driver[0], con, lenTable)                              # 12'(down)
    crawler_quantum.crawl_quantum(driver[0], con, familiesSite)                     # 5'
    crawler_ransomexx.crawl_ransomexx(driver[0], con, familiesSite)                 # 2'
    crawler_snatch.crawl_snatch(driver[0], con, familiesSite)                       # 3'     


    con.close()
    log.info("END!")

main()
