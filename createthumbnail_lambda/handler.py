# install opencv-python PIL

import os
import uuid

import boto3

import cv2
from PIL import Image

s3client = boto3.client('s3')


def GetFileFromS3(filename, bucket):
    print("Step 1: Getting file from S3")
    key = filename
    print(key)
    # DownloadPath = '/tmp/{}_{}'.format(uuid.uuid4(), key)
    try:
        os.makedirs('/tmp/downloaded_files')
    except FileExistsError:
        pass
    key1 = filename.split('/')[-1]
    DownloadPath = '/tmp/downloaded_files/{}_{}'.format(uuid.uuid4(), key1)
    s3client.download_file(bucket, key, DownloadPath)
    print("Step 1: Done Getting file from S3")
    return DownloadPath


def ExtractVideoFrames(DownloadFile):
    print("Step 2: executing ExtractVideoFrames")
    cap = cv2.VideoCapture(DownloadFile)
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    frames = []
    if cap.isOpened() and video_length > 0:
        frame_ids = [0]
        if video_length >= 4:
            # frame_ids = [0,
            #             round(video_length * 0.25),
            #            round(video_length * 0.5),
            #             round(video_length * 0.75),
            #             video_length - 1]
            frame_ids = [round(video_length * 0.25)]
    count = 0
    success, image = cap.read()
    while success:
        if count in frame_ids:
            frames.append(image)
        success, image = cap.read()
        count += 1
    print("Step 2: done executing ExtractVideoFrames")
    return frames


def GenerateAndSaveThumbs(frames):
    print("Step 3: executing GenerateAndSaveThumbs")
    thumb_list = []
    for i in range(len(frames)):
        thumb = image_to_thumbs(frames[i])
        print(i)
        try:
             os.makedirs('/tmp/frames/%d' % i)
        except FileExistsError:
            pass
        for k, v in thumb.items():
            cv2.imwrite('/tmp/frames/%d/%s.jpeg' % (i, k), v)  # WORKS
            thumb_list.append('/tmp/frames/%d/%s.jpeg' % (i, k))
    print("Step 3: done executing GenerateAndSaveThumbs")
    return thumb_list


# cv2.imwrite('img_CV2_90.jpg', a, [int(cv2.IMWRITE_JPEG_QUALITY), 90])		0-100 Image quality


def image_to_thumbs(img):
    """Create thumbs from image"""
    height, width, channels = img.shape
    # thumbs = {"original": img}
    thumbs = {}
    sizes = [640, 320, 160]
    #    sizes = [640]
    #    for size in sizes:
    idx = 0
    while True:
        if width >= sizes[idx]:
            r = (sizes[idx] + 0.0) / width
            max_size = (sizes[idx], int(height * r))
            thumbs[str(sizes[idx])] = cv2.resize(img, max_size, interpolation=cv2.INTER_AREA)
            return thumbs
        idx = idx + 1


def for_image_thumbnail(infile, filename):
    print("Step 2: Create image thumbnail")
    im = Image.open(infile)
    im.thumbnail((640, 360), Image.ANTIALIAS)
    if infile[0:2] != "T_":  # don't save if thumbnail already exists
        try:
            if len(filename.split('/')) == 2:
                print('/tmp/frames/images/'+filename.split('/')[0])
                os.makedirs('/tmp/frames/images/'+filename.split('/')[0])
            elif len(filename.split('/')) == 1:
                os.makedirs('/tmp/frames/images/')
                print('/tmp/frames/images/')
        except FileExistsError:
            pass
        im = im.convert("RGB")
        im.save("/tmp/frames/images/%s_thumbnail.jpeg" % filename.split('.')[0], "JPEG")
    response = "/tmp/frames/images/%s_thumbnail.jpeg" % filename.split('.')[0]
    print("Step 2: Done Create image thumbnail")
    return [response]


# For uploading thumbnail to S3
def UploadThumbnailToS3(thumbfile, filename, flag):
    print("Uploading File to S3")
    for thumb_file in thumbfile:
        with open(thumb_file, 'rb') as file:
            object = file.read()
            bucket = 'mybucket-thumbnails'
            if flag:
                # thumb_file_formatted = 'videothumbnail/'+filename.split('.')[0]+'_'+thumb_file.split('/')[-1]
                thumb_file_formatted = 'videothumbnail/' + filename + '_thumbnail.jpeg'
            else:
                # thumb_file_formatted = 'imagethumbnail/' + filename.split('.')[0] + '_' + thumb_file.split('/')[-1]
                thumb_file_formatted = 'imagethumbnail/' + filename + '_thumbnail.jpeg'
            response = s3client.put_object(Body=object, Bucket=bucket,
                                           Key=thumb_file_formatted)  # s3client not a global object
            print("Done uploading file to S3")
            return response


'''
Merging of thumbnail to video
-----------------------------------|

from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize


fps=5
size=None
is_color=True
format="XVID"
def GenerateAndSaveThumbs(frames):
    thumb_list = []
    for i in range(len(frames)):
        thumb = image_to_thumbs(frames[i])
        print(i)
        try:
            os.makedirs('/tmp/frames/%d' % i)
        except FileExistsError:
            pass
        for k, v in thumb.items():
            cv2.imwrite('/tmp/frames/%d/%s.jpeg' % (i, k), v)  # WORKS
            thumb_list.append('/tmp/frames/%d/%s.jpeg' % (i, k))
    vid=None
    outvid='testing.mp4'
    for image in thumb_list:
    if not os.path.exists(image):
        raise FileNotFoundError(image)
    img = imread(image)
    if vid is None:
        if size is None:
            size = img.shape[1], img.shape[0]
        vid = VideoWriter(outvid, fourcc, float(fps), size, is_color)
    if size[0] != img.shape[1] and size[1] != img.shape[0]:
        img = resize(img, size)
    vid.write(img)
    vid.release()	

'''

'''

frames = ExtractVideoFrames(file)
GenerateAndSaveThumbs(frames)
thumb_file = GenerateAndSaveThumbs(frames)
print(thumb_file)
UploadThumbnailToS3(thumb_file)
for_image_thumbnail(img)

'''


def handler(event, context=None):
    image_formats = ['jpeg', 'png', 'jpg']
    bucket = event['Records'][0]['s3']['bucket']['name']
    filename = event['Records'][0]['s3']['object']['key']
    DownloadFile = GetFileFromS3(filename, bucket)
    if filename.split('.')[-1] in image_formats:
        thumb_file = for_image_thumbnail(DownloadFile, filename)
        flag = 0
    else:
        frames = ExtractVideoFrames(DownloadFile)
        flag = 1
        thumb_file = GenerateAndSaveThumbs(frames)
    response = UploadThumbnailToS3(thumb_file, filename, flag)
    return response



