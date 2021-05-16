#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import random
from matplotlib import pyplot as plt

# 每行的间距
strand_site_col = 180
# 每个单词的间距
strand_site_row = 200
# 字母映射表
zi = {
    1:"A",
    2:"B",
    3:"C",
    4:"D",
    5:"E",
    6:"F",
    7:"G",
    8:"H",
    9:"I",
    10:"J",
    11:"K",
    12:"L",
    13:"M",
    14:"N",
    15:"O",
    16:"P",
    17:"Q",
    18:"R",
    19:"S",
    20:"T",
    21:"U",
    22:"V",
    23:"W",
    24:"X",
    25:"Y",
    26:"Z"
}

# img_rgb = cv2.imread('site_result.png')
# img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

def site_jiemi(pic_path):
    img_rgb = cv2.imread(pic_path)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    # 最终结果页面
    fin_loc = []
    # 相似率
    threshold = 0.985

    for i in range(1, 26+1):
        temp_zi = zi[i]
        template = cv2.imread(f'pic/{temp_zi}.png', 0)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        # print(temp_zi, loc)

        # 过滤
        for i in range(len(loc[0])):
            if len(fin_loc) == 0:
                fin_loc.append((loc[1][i], loc[0][i]))
                continue

            K = 0
            for item in fin_loc:        
                # 如果 行相同(差为0)列大于100 如果列相同(差为0) 行大于100
                if abs(item[1] - loc[0][i]) == 0 and abs(item[0] - loc[1][i]) < 100:
                    K = 1
                elif abs(item[0] - loc[1][i]) == 0 and abs(item[1] - loc[0][i]) < 100:
                    K = 1
            if K != 1:
                fin_loc.append((loc[1][i], loc[0][i]))
            else:
                print(f"有一个小朋友被淘汰啦!")

    # 结果收束 
    for item in fin_loc:
        cv2.rectangle(img_rgb, item, (item[0] + w, item[1] + h), (0, 0, 255), 1)

    # # 展示检测图像结果
    # cv2.imshow('res', img_rgb)
    # cv2.waitKey(0)

    # 排序
    fin_loc.sort(key=lambda x: (x[1], x[0]))
    # print(fin_loc)

    # 执行解密操作
    result_str = ""
    for item in range(len(fin_loc)-1):
        # 判断换行
        if fin_loc[item][1] != fin_loc[item + 1][1]:
            continue
        
        cha_yi = fin_loc[item+1][0] - fin_loc[item][0]
        print(cha_yi)
        Q = fin_loc[item+1][0] - fin_loc[item][0]- strand_site_row
        result_str += zi[Q] if 1 <= Q  and 26 >= Q else " "

    # 返回结果
    print(result_str)
    return result_str
        

# site_jiemi('site_result.png')