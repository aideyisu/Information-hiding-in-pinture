#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
from matplotlib import pyplot as plt

# img_rgb = cv2.imread('12.png')
img_rgb = cv2.imread('site_result_test.png')
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
# template = cv2.imread('123.png', 0)
template = cv2.imread('pic/A.png', 0)
w, h = template.shape[::-1]

res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

threshold = 0.993
loc = np.where(res >= threshold)
# print((loc[::-1]))
fin_loc = []

# 过滤
for i in range(len(loc[0])):
    if len(fin_loc) == 0:
        fin_loc.append((loc[1][i], loc[0][i]))
        continue

    min_1, min_2 = 9999, 9999
    for item in fin_loc:        
        if abs(item[1] - loc[0][i]) < min_1:
            min_1 = abs(item[1] - loc[0][i])
        if abs(item[0] - loc[1][i]) < min_2:
            min_2 = abs(item[0] - loc[1][i])

    if min_1 > 2 or min_2 > 2:
        fin_loc.append((loc[1][i], loc[0][i]))

print(fin_loc)

for item in fin_loc:
    print(type(item))
    cv2.rectangle(img_rgb, item, (item[0] + w, item[1] + h), (0, 0, 255), 1)


cv2.imshow('res', img_rgb)
cv2.waitKey(0)
