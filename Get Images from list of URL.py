import os
import urllib.request as ulib
import numpy as np
import cv2

link = 'D:/urls.txt'
with open(link) as f:
    lines = f.readlines()

#neg_images_link = 'http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=n02958343'
#neg_image_urls = ulib.urlopen(neg_images_link).read().decode()

if not os.path.exists('images'):
    os.makedirs('images')

pic_num = 0

for i in lines:
    try:
        print(i)
        ulib.urlretrieve(i, "images/"+str(pic_num)+'.jpg')
        pic_num += 1

    except Exception as e:
        print(str(e))

#for i in neg_image_urls.split("\n"):
#    try:
#        print(i)
#        ulib.urlretrieve(i, "images/"+str(pic_num)+'.jpg')
#        pic_num += 1

#    except Exception as e:
#        print(str(e))