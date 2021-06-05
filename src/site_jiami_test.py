import cv2
import random
import numpy as np

# 每行的间距
strand_site_col = 170
# 每个单词的间距
strand_site_row = 180
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

def mergeImg(inputImg,maskImg,contourData,drawPosition):
    '''
    :param inputImg: 输入的图像
    :param maskImg: 输入的模板图像
    :param contourData: 输入的模板中轮廓数据 numpy 形式如[(x1,y1),(x2,y2),...,]
    :param drawPosition: （x,y） 大图中要绘制模板的位置,以maskImg左上角为起始点
    :return: outPutImg：输出融合后的图像
             outContourData: 输出轮廓在inputImg的坐标数据
             outRectData: 输出轮廓的矩形框在inputImg的坐标数据
    '''
    #通道需要相等
    if (inputImg.shape[2] != maskImg.shape[2]):
        print("inputImg shape != maskImg shape")
        return
    inputImg_h=inputImg.shape[0]
    inputImg_w=inputImg.shape[1]
    maskImg_h = maskImg.shape[0]
    maskImg_w = maskImg.shape[1]
    #inputImg图像尺寸不能小于maskImg
    if(inputImg_h<maskImg_h or inputImg_w<maskImg_w):
        print("inputImg size < maskImg size")
        return
    #画图的位置不能超过原始图像
    if(((drawPosition[0]+maskImg_w)>inputImg_w) or ((drawPosition[1]+maskImg_h)>inputImg_h)):
        print("drawPosition + maskImg > inputImg range")
        return
    outPutImg=inputImg.copy()
    input_roi=outPutImg[drawPosition[1]:drawPosition[1]+maskImg_h,drawPosition[0]:drawPosition[0]+maskImg_w]
    imgMask_array=np.zeros((maskImg_h,maskImg_w,maskImg.shape[2]),dtype=np.uint8)
    #triangles_list = [np.zeros((len(contourData), 2), int)]
    triangles_list=[contourData]
    cv2.fillPoly(imgMask_array, triangles_list, color=(1,1,1))
    cv2.fillPoly(input_roi, triangles_list, color=(0, 0, 0))
    #cv2.imshow('imgMask_array', imgMask_array)
    imgMask_array=imgMask_array*maskImg
    output_ori=input_roi+imgMask_array
    outPutImg[drawPosition[1]:drawPosition[1] + maskImg_h, drawPosition[0]:drawPosition[0] + maskImg_w]=output_ori
    triangles_list[0][:, 0] = contourData[:, 0] +drawPosition[0]
    triangles_list[0][:, 1] = contourData[:, 1] +drawPosition[1]
    outContourData=triangles_list[0]
  
    return outPutImg,outContourData#,outRectData

def make_picture(insert_code, img, x_site, y_site):
    # 制作图像,将小的贴到大的上面

    # 加载图像
    # img=cv2.imread(big_one_path)
    maskImg=cv2.imread(f"pic/{insert_code}.png")

    # 判断字母需要使用哪个尺寸 - 这个变量在操作过程中会发生改变,所以使用.copy只传递变量拷贝
    contourData = np.array([(0,0),(175,0), (175,154),(0,154)]) if insert_code == "W" else np.array([(0,0),(150,0), (150,150),(0,150)]) 
    outPutImg, _ =mergeImg(img, maskImg, contourData.copy(), (x_site,y_site))

    return outPutImg

# 随机数生成
def ran_zi():
    return zi[random.randrange(26)]

def detect_zi(english_zi):
    if ord(english_zi) > 96 and ord(english_zi) < 123:
        return ord(english_zi) - 96
    elif  ord(english_zi) > 64 and ord(english_zi) < 91:
        return ord(english_zi) - 64


# 加密
def site_jiami(secret_text):
    # 输入 1密文 
    # 2明文(明文长度必须大于密文长度 * 1.2 + 1)保证换行可用 
    
    # 起始位置
    x_start = 20
    y_start = 20
    imgStr0 = '12.png' # 大的那个
    imgStr=cv2.imread(imgStr0)
    num = 1
    # 先打印一个字
    Picture = make_picture(ran_zi(), imgStr, x_start, y_start)
    cv2.imshow('2', Picture)
    cv2.waitKey(0)

    for sec_item in secret_text:
        print(f"当前是 {sec_item}")
        x_start += (strand_site_row + detect_zi(sec_item))
        # 打印一个字
        Picture = make_picture(ran_zi(), Picture, x_start, y_start)
        
        # 收尾
        num += 1
        if num %10 == 0:
            num = 1
            x_start += strand_site_col

    cv2.imshow('3', Picture)
    # 保存
    cv2.imwrite('site_result.png', Picture)
    cv2.waitKey(0)    
    return Picture
    # 输出 加密图片一张

site_jiami("wy")


# if(__name__=="__main__"):
#     # 初始化
#     insert_code = "A"
#     imgStr = '12.png' # 大的那个
#     imgMaskStr = 'pic/A.png' # 小的那个
    
#     # 加载图像
#     img=cv2.imread(imgStr)
#     maskImg=cv2.imread(imgMaskStr)
#     # contourData=np.a  rray([(0,0),(169,0), (169,209),(0,209)]) # 此处逻辑为一次 
    
#     # 判断字母需要使用哪个尺寸 - 这个变量在操作过程中会发生改变,所以使用.copy只传递变量拷贝
#     contourData = np.array([(0,0),(175,0), (175,154),(0,154)]) if insert_code == "W" else np.array([(0,0),(150,0), (150,150),(0,150)]) 
#     # 图像实施加载
#     outPutImg,outContourData=mergeImg(img, maskImg, contourData.copy(), (250,400))

#     # 加载俩
#     # contourData = np.array([(0,0),(175,0), (175,154),(0,154)]) if insert_code == "W" else np.array([(0,0),(150,0), (150,150),(0,150)]) 
#     # outPutImg2,outContourData=mergeImg(outPutImg, maskImg, contourData.copy(), (0,200))
#     # print(contourData)
#     # cv2.imshow('4', outPutImg2)    

#     # 测试调用功能
#     pic_test = make_picture("W", imgStr, 150, 150)
#     cv2.imshow('9', pic_test)    

#     # 展示
#     cv2.imshow('2', outPutImg)
#     cv2.imshow('3', maskImg)

#     # 保存
#     cv2.imwrite('site_result_test.png', outPutImg)
#     cv2.waitKey(0)




# ————————————————
# 版权声明：本文为CSDN博主「captain_CasonCai」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/qq_33671888/article/details/89499311  

# 图像来源网址
# http://616pic.com/sucai/zq9ijmxmv.html