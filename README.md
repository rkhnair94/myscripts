# Some quick and dirty scripts for automation
>
>
## *createthumbnail_lambda:*
>This script/lambda function will convert images and videos to thumbnail and store it to specified s3 bucket.

#### Pre-requisites:
>Install below python modules in your working directory:

```
pip3 install opencv-python -t ~/mywork/personal/createthumbnail_lambda/
pip3 install Pillow -t ~/mywork/personal/createthumbnail_lambda/
pip3 install  PIL -t ~/mywork/personal/createthumbnail_lambda/
pip3 install Image -t ~/mywork/personal/createthumbnail_lambda/
```
#### Create zip file of createthumbnail_lambda and upload it to lambda via s3
  
