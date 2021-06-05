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
print(len(res))
threshold = 0.99
loc = np.where(res >= threshold)
# print((loc[::-1]))
fin_loc = []

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

    if min_1 > 2 and min_2 > 2:
        fin_loc.append((loc[1][i], loc[0][i]))

        # if abs(item[1] - loc[0][i]) > 2 and abs(item[0] - loc[1][i]) > 2:
        #     fin_loc.append((loc[1][i], loc[0][i]))
        #     break

print(fin_loc)

for pt in zip(*loc[::-1]):
    print(pt)
    cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 1)
    # print(pt[0], w, pt[1] , h)

cv2.imshow('res', img_rgb)
cv2.waitKey(0)

# 0是宽 1是高度
# print(loc[0], loc[1])
# print(loc[0][0], loc[0][-1], loc[-1][0], loc[-1][-1])
