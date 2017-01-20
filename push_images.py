from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from xvfbwrapper import Xvfb
import boto3
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities



urllist = open("url_list", 'r')
storagelocation = "/tmp/"
s3bucket_name = 'home-displayboard'

for line in urllist:
    splitline = line.split('|')
    url = splitline[0]
    name = splitline[1].rstrip('\n')
    display = Xvfb(width=1920,height=1200)
    display.start()

    capabilities = DesiredCapabilities.FIREFOX
    capabilities['marionette'] = True
    capabilities['acceptSslCerts'] = True

    profile = webdriver.FirefoxProfile()
    profile.accept_untrusted_certs = True
    profile.set_preference('network.http.phishy-userpass-length', 255)

    driver = webdriver.Firefox()

    print "getting " + url
    driver.get(url)
    try:
        alert = driver.switch_to.alert.accept()
    except NoAlertPresentException:
        print('No Phishing Warning Popup')


    filename = storagelocation+name+".png"
    if driver.save_screenshot(filename):
        print "save success"
    driver.quit()
    #s3 magic
    s3 = boto3.resource('s3')
    data = open(filename, 'rb')
    s3.Bucket(s3bucket_name).put_object(Key=name+'.png', Body=data)

