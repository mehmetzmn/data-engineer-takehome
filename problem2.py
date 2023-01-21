# Move all image files from one S3 bucket to another S3 bucket, 
# but only if the image has no transparent pixels
# Followings:
# List all the image files in a given S3 bucket
# Check if each image file has transparent pixels
# If an image file has no transparent pixels, copy it to different S3 bucket
# If an image file has transparent pixels, log it in separate file


import logging
import boto3
from botocore.exceptions import ClientError
from PIL import Image

def create_bucket(bucket_name, region=None):
    # Create an S3 bucket in a specified region,
    # If a region is not specified, the bucket is created in the S3 default region (us-east-1).

    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def get_bucket_names():
    input_buckets_list = []
    print("Please enter source bucket name: ")
    source_bucket = list(map(str ,input().split()))
    print("Please enter destination bucket name: ")
    destination_bucket = list(map(str, input().split()))

    # Check current s3 client, 
    # store all existed buckets
    s3 = boto3.client("s3")

    buckets_resp = s3.list_buckets()
    bucket_list = [x['Name'] for x in buckets_resp['Buckets']]

    # if input bucket has whitespace, then combine the name
    if len(source_bucket) >= 2 or len(destination_bucket) >= 2:
        input_buckets_list.extend([" ".join(source_bucket), " ".join(destination_bucket)])
    else:
        input_buckets_list.extend([source_bucket[0], destination_bucket[0]])

    # if input_bucket is not in existed buckets, 
    # then create a new bucket
    for input_bucket in input_buckets_list:
        if input_bucket not in bucket_list:
            create_bucket(input_bucket)
        
    return input_buckets_list


def has_transparency(img):
    # if img object has transparency key then it is transparent
    if img.info.get("transparency", None) is not None:
        return True
    # if the image is using indexed colors (such as in GIFs),
    # it gets the index of the transparent color in the palette, 
    # and checks if it's used anywhere in the canvas 
    if img.mode == "P":
        transparent = img.info.get("transparency", -1)
        for _, index in img.getcolors():
            if index == transparent:
                return True
    #  If the image is in RGBA mode, then presumably it has transparency in it
    elif img.mode == "RGBA":
        extrema = img.getextrema()
        if extrema[3][0] < 255:
            return True
    # The image is not transparent
    return False

s3 = boto3.client("s3")

# list all buckets
buckets_resp = s3.list_buckets()
bucket_list = [x['Name'] for x in buckets_resp['Buckets']]

bucket_list = get_bucket_names()

# upload image file to a bucket, for testing
# with open(r"PATH\transparent.png", "rb") as f:
#     print(f.name)
#     s3.upload_fileobj(f, bucket_list[0], "transparent.png")

# Create buckets, upload image file to a bucket, for testing
# create_bucket("bucket-temp-02")

# List all objects in a bucket
response = s3.list_objects_v2(Bucket=bucket_list[0])

# Objects from source bucket
for obj in response["Contents"]:
    # Creating source dictionary first bucket in bucket_list
    copy_source = {
        'Bucket' : bucket_list[0],
        'Key': obj['Key']
    }
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_list[1])

    # reading object as PIL object
    img = Image.open(obj['Key'])
    # Check transparency, if the image has transparency create log.txt and save it in, 
    # else copy it in destination bucket
    if has_transparency(img):
        object = s3.Object(bucket_list[1], 'log.txt')
        object.put(Body=f"{obj['Key']} has transparent pixels")
    else:
        bucket.copy(copy_source, f"Copied/{obj['Key']}")



