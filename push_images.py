from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from xvfbwrapper import Xvfb
import boto3
import schedule
import time
import logging
import ConfigParser

config = ConfigParser.ConfigParser()
config.read("config.ini")
bucketLocation = config.get('main', 'aws_bucket_name')
storagelocation = config.get('main', 'tmp_file_location')
if config.get('main','log_level') == 'INFO':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
else:
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARNING)



def job():
    urllist = open("url_list", 'r')
    filelist = list()
    logging.info("Push AWS Job Started.")
    client = boto3.client(
        's3',
        aws_access_key_id=config.get('main', 'aws_access_id'),
        aws_secret_access_key=config.get('main', 'aws_secret_key')
    )
    for line in urllist:
        splitline = line.split('|')
        url = splitline[0]
        name = splitline[1].rstrip('\n')
        display = Xvfb(width=1680,height=1050)
        display.start()

        profile = webdriver.FirefoxProfile()
        profile.accept_untrusted_certs = True
        profile.set_preference('network.http.phishy-userpass-length', 255)

        driver = webdriver.Firefox(profile)
        driver.set_window_size(1680,1050)

        logging.info("getting " + url)
        driver.get(url)
        delay = config.getint('main', 'wait_timeout')
        WebDriverWait(driver, delay)


        filename = storagelocation+name+".png"
        if driver.save_screenshot(filename):
            logging.info("save success")
        driver.quit()
        display.stop()
        #s3 magic
        uploadFailed = False
        try:
            data = open(filename, 'rb')
            put_file(client, bucketLocation, name+'.png', data)
	    data.close()
        except:
            logging.error("Upload of " + filename + " failed.")
            uploadFailed = True

        if  not uploadFailed:
            filelist.append(name + '|' + storagelocation + name+'.png')


    with open('file_list','w') as f:
        for line in filelist:
            f.write(line+'\n')

    try:
        data = open('file_list', 'r')
        put_file(client, bucketLocation, 'file_list.txt', data)
 	data.close()
    except:
        logging.error("CANNOT UPLOAD FILE LIST!")

    urllist.close()
    logging.info("AWS Push Job Completed.")


def heartbeat():
     logging.info("[HEARTBEAT] Heartbeat Log Entry")

def put_file(client, bucket, name, contents):
    logging.info("Putting file into S3: bucket="+bucket+ "name="+name)
    client.put_object(Bucket=bucket, Key=name, Body=contents)

logging.info("Running Job at Startup.")
job()

if config.getboolean('main','run_always'):
    schedule.every(1).minutes.do(heartbeat)
    schedule.every(5).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(10)

