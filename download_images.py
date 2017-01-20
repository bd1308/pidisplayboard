import boto3

bucketLocation = 'home-displayboard'
fileLocation = '/tmp/'

s3 = boto3.client('s3')
list = s3.list_objects(Bucket=bucketLocation)['Contents']

for s3_key in list:
    s3_object = s3_key['Key']
    if not s3_object.endswith("/"):
        s3.download_file(bucketLocation, s3_object, fileLocation+s3_object)
    else:
        import os
        if not os.path_exists(s3_object):
            os.makedirs(s3_object)








