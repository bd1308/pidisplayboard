from selenium import webdriver
from xvfbwrapper import Xvfb


urllist = open("url_list", 'r')
storagelocation = "/tmp"

for line in urllist:
    splitline = line.split(',')
    url = splitline[0]
    name = splitline[1].rstrip('\n')
    display = Xvfb(width=1920,height=1200)
    display.start()
    browser=webdriver.Firefox()
    browser.get(url)
    if browser.save_screenshot("/tmp/"+name+".png"):
        print "success"
    browser.quit()
