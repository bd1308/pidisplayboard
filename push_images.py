from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from xvfbwrapper import Xvfb
import boto3
import schedule
import time
import logging
import ConfigParser
import signal

config = ConfigParser.ConfigParser()
config.read("config.ini")
bucketLocation = config.get('main', 'aws_bucket_name')
storagelocation = config.get('main', 'tmp_file_location')
if config.get('main','log_level') == 'INFO':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
else:
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARNING)

# Create boto is aws sdk for python
# Requires aws_key_id and aws_secret_key, stored in config.ini
client = boto3.client(
's3',
aws_access_key_id=config.get('main', 'aws_access_id'),
aws_secret_access_key=config.get('main', 'aws_secret_key')
)

# gather_images gathers files from specified locations and returns a dictionary with imagename:imagepath format
def gather_images():
    logging.info("In gather_images()")
    # Open url_list file: stores list of urls to capture in format <url>|<save_image_as>
    urllist = open("url_list", 'r')
    filedict = dict()


    profile = webdriver.FirefoxProfile()
    profile.accept_untrusted_certs = True
    profile.set_preference('network.http.phishy-userpass-length', 255)
    profile.set_preference('webdriver.load.strategy', 'unstable')


    # Iterate through url_list to capture screenshots and save file
    for line in urllist:
        splitline = line.split('|')
        url = splitline[0]
        name = splitline[1].rstrip('\n')
        #display = Xvfb(width=1680,height=1050)
        #display.start()

        #driver = webdriver.Firefox(profile)
        #driver.set_window_size(1680,1050)
        #driver.set_page_load_timeout(15)

        driver = webdriver.PhantomJS()
        driver.set_window_size(1680,1050)
        driver.set_page_load_timeout(15)

        logging.info("getting " + url)

        try: 
            driver.get(url)
        except TimeoutException as e:
            logging.error("TimeOut Exception occurred:" + url)

        # Save file at storagelocation(specified in config.ini), append name and location in dictionary.
        filename = storagelocation+name+".png"
        if driver.save_screenshot(filename):
            logging.info(filename +" save success")
            filedict[name] = filename
        driver.service.process.send_signal(signal.SIGTERM) # kill the specific phantomjs child proc
        driver.quit()
        #display.stop()
    urllist.close()
    return filedict

# post_images opens files from location and name specified in dictionary(passed as argument) and saves in bucket.
# also creates and saves a file named file_list.txt in bucket.
# FIXME: file_list.txt should be picked from config.ini
def post_images(filedict):
    logging.info("In post_images()")
    try:
        open('file_list','w').close()
    except:
        logging.info("Can't clear file contents")

    try:
        f = open('file_list','a')
    except:
        logging.info("Can't open file for reading")

    # Iterate over dict filedict, open file at path(value), put it as name(key) on s3 bucket 
    for name, path in filedict.iteritems():
       uploadFailed = False
       try:
           data = open(path, 'rb')
           put_file(client, bucketLocation, name+'.png', data)
           data.close()
       except:
           logging.error("Upload of " + name + ".png "+ path +" failed.")
           uploadFailed = True

       if  not uploadFailed:
           f.write(name + '|' + path)

    f.close()

    try:
        data = open('file_list', 'r')
        put_file(client, bucketLocation, 'file_list.txt', data)
        data.close()
    except:
        logging.error("CANNOT UPLOAD FILE LIST!")

def job():
    logging.info("Push AWS Job Started.")
    imgdict = gather_images()
    post_images(imgdict)
    logging.info("AWS Push Job Completed.")

def heartbeat():
     logging.info("[HEARTBEAT] Heartbeat Log Entry")

def put_file(client, bucket, name, contents):
    logging.info("Putting file into S3: bucket="+bucket+ "name="+name)
    client.put_object(Bucket=bucket, Key=name, Body=contents)

logging.info("Running Job at Startup.")
job()

while True:
     time.sleep(300)
     job()

