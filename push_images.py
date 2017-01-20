from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from xvfbwrapper import Xvfb
import boto3
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import schedule
import time
import logging




urllist = open("url_list", 'r')
storagelocation = "/tmp/"
s3bucket_name = 'home-displayboard'



def job():
    for line in urllist:
        splitline = line.split('|')
        url = splitline[0]
        name = splitline[1].rstrip('\n')
        display = Xvfb(width=1920,height=1200)
        display.start()

        profile = webdriver.FirefoxProfile()
        profile.accept_untrusted_certs = True
        profile.set_preference('network.http.phishy-userpass-length', 255)

        driver = webdriver.Firefox(profile)

        logging.info("getting " + url)
        driver.get(url)

        filename = storagelocation+name+".png"
        if driver.save_screenshot(filename):
            logging.info("save success")
        driver.quit()
        #s3 magic
        s3 = boto3.resource('s3')
        data = open(filename, 'rb')
        s3.Bucket(s3bucket_name).put_object(Key=name+'.png', Body=data)
def heartbeat():
     logging.info("[HEARTBEAT] Heartbeat Log Entry")

schedule.every(1).minutes.do(heartbeat)
schedule.every(5).minutes.do(job)
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.INFO)


while 1:
    schedule.run_pending()
    time.sleep(1)

