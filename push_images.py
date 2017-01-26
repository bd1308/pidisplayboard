from selenium import webdriver
from xvfbwrapper import Xvfb
import boto3
import schedule
import time
import logging

urllist = open('url_list','r')
storagelocation = '/tmp/'
s3bucket_name = 'home-displayboard'
filelist = list()

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.INFO)



def job():
    urllist = open("url_list", 'r')
    logging.info("Push AWS Job Started.")
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
            filelist.append(name+'|'+filename)
        driver.quit()
        #s3 magic
        uploadFailed = False
        try:
            s3 = boto3.resource('s3')
            data = open(filename, 'rb')
            s3.Bucket(s3bucket_name).put_object(Key=name+'.png', Body=data)
        except:
            logging.error("Upload of " + filename + " failed.")
            uploadFailed = True

        if  not uploadFailed:
            filelist.append(name + '|' + filename)

    with open('file_list','w') as f:
        for line in filelist:
            f.write(line+'\n')

    try:
        s3 = boto3.resource('s3')
        data = open('file_list', 'rb')
        s3.Bucket(s3bucket_name).put_object(Key='file_list.txt', Body=data)
    except:
        logging.error("CANNOT UPLOAD FILE LIST!")

    urllist.close()
    logging.info("AWS Push Job Completed.")


def heartbeat():
     logging.info("[HEARTBEAT] Heartbeat Log Entry")

logging.info("Running Job at Startup.")
job()
schedule.every(1).minutes.do(heartbeat)
schedule.every(5).minutes.do(job)



while 1:
    schedule.run_pending()
    time.sleep(1)

