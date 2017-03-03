# pidisplayboard
* push_images.py - Collects snapshots from URLs in file_list, and uploads them to S3 bucket
* download_images.py - Downloads files from S3 location, and displays them in a pygame slideshow
* url_list - list of URLs and titles/descriptions ( | delimited)

# Configuration
Create a file called `config.ini` in your working (current) directory.
This file should contain this information: 
```
[main]
aws_access_id: AWS_ACCESS_ID
aws_secret_key: AWS_SECRET_KEY
aws_bucket_name: bucket_name
log_level: INFO
tmp_file_location: /tmp/

[slideshow]
slideshow_update_interval: 20
use_fullscreen: True
```

These options will be used by the two programs to load properties. 