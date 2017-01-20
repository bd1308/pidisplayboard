from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.wait import WebDriverWait
from xvfbwrapper import Xvfb
import boto3
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities



urllist = open("url_list", 'r')
storagelocation = "/tmp/"
s3bucket_name = 'home-displayboard'

for line in urllist:
    splitline = line.split(',')
    url = splitline[0]
    name = splitline[1].rstrip('\n')
    display = Xvfb(width=1920,height=1200)
    display.start()
    browser=webdriver.Firefox()

    capabilities = DesiredCapabilities.FIREFOX
    capabilities['marionette'] = True
    capabilities['acceptSslCerts'] = True

    profile = webdriver.FirefoxProfile()
    profile.accept_untrusted_certs = True
    profile.set_preference('network.http.phishy-userpass-length', 255)


    browser.get(url)
    filename = storagelocation+name+".png"
    if browser.save_screenshot(filename):
        print "save success"
    browser.quit()
    #s3 magic
    s3 = boto3.resource('s3')
    data = open(filename, 'rb')
    s3.Bucket(s3bucket_name).put_object(Key=name+'.png', Body=data)

