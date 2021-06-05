# all-black 纯黑色底图


import cv2
import numpy
#全黑的灰度图
gray0=numpy.zeros((500,500),dtype=numpy.uint8)
# cv2.imshow('0',gray0)
#全白的灰度图
gray0[:,:]=255
gray255=gray0[:,:]
# cv2.imshow('255',gray255)
#将灰度图转换成彩色图
Img_rgb=cv2.cvtColor(gray255,cv2.COLOR_GRAY2RGB)
#将RGB通道全部置成0
Img_rgb[:,:,0:3]=0
cv2.imshow('(0,0,0)',Img_rgb)
# #将RGB通道全部置成255
# Img_rgb[:,:,0:3]=255
# cv2.imshow('(255,255,255)',Img_rgb)
cv2.waitKey(0)

# ————————————————
# 版权声明：本文为CSDN博主「Ybossceo」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/weixin_43951995/article/details/100836069