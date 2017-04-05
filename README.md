# pidisplayboard
* push_images.py - Collects snapshots from URLs in file_list, and uploads them to S3 bucket
* download_images.py - Downloads files from S3 location, and displays them in a pygame slideshow
* url_list - list of URLs and titles/descriptions ( | delimited)

## Configuration
Create a file called `url_list` in your working directory.
This file will have a format like the following:
```
http://www.google.com|Google
http://www.hackaday.com|Hackaday
```



Create a file called `config.ini` in your working (current) directory.
This file should contain this information: 
```
[main]
aws_access_id: AWS_ACCESS_ID
aws_secret_key: AWS_SECRET_KEY
aws_bucket_name: bucket_name
log_level: INFO
tmp_file_location: /tmp/
wait_timeout: 3

[slideshow]
slideshow_update_interval: 20
use_fullscreen: True
```

These options will be used by the two programs to load properties. 


## Installation for Client 
pip install -r requirements.txt

There are some packages required for deployment/running. One of these is Xvfb, and thus requires the client to be ran via sudo, as directfb seems to require root for proper access. I've managed to finally get pip to build pygame, but it's much easier to install pygame from your repository as well. 

## Installation for Server
pip install -r requirements.txt

