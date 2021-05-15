import cv2
import numpy as np
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


if(__name__=="__main__"):
    imgStr = '12.png' # 大的那个
    imgMaskStr = '123.png' # 小的那个
    img=cv2.imread(imgStr)
    maskImg=cv2.imread(imgMaskStr)
    contourData=np.array([(0,0),(169,0), (169,209),(0,209)]) # 此处逻辑为一次 
    outPutImg,outContourData=mergeImg(img, maskImg, contourData, (250,400))

    cv2.imshow('2',outPutImg)
    cv2.imshow('3', maskImg)

    cv2.imwrite('result.png', outPutImg)
    cv2.waitKey(0)

# ————————————————
# 版权声明：本文为CSDN博主「captain_CasonCai」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/qq_33671888/article/details/89499311