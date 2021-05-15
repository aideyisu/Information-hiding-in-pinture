#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
from matplotlib import pyplot as plt

img_rgb = cv2.imread('12.png')
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
template = cv2.imread('123.png', 0)
w, h = template.shape[::-1]
print("hello")
res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
tl = max_loc # 左上角
br = (tl[0]+w, tl[1]+h) # 右下角
print(br)
print(min_val, max_val, min_loc, max_loc)
cv2.rectangle(img_rgb, tl, br, (0, 0, 255), 1)

cv2.imshow('res', img_rgb)
cv2.waitKey(0)

# 0是宽 1是高度
# print(loc[0], loc[1])
# print(loc[0][0], loc[0][-1], loc[-1][0], loc[-1][-1])
