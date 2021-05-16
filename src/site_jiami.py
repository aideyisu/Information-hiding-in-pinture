import cv2
import random
import numpy as np

# 每行的间距
strand_site_col = 180
# 每个单词的间距
strand_site_row = 200
# 字母映射表
zi = {
    0:"0",
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
    return zi[random.randrange(1, 26)]
    # while True:
    #     num = random.randrange(1, 26)
    #     if num not in [2, 3, 9, 12, 16]:
    #         # 这几个效果不好...
    #         break
    # return zi[num]


def detect_zi(english_zi):
    if ord(english_zi) > 96 and ord(english_zi) < 123:
        return ord(english_zi) - 96
    elif  ord(english_zi) > 64 and ord(english_zi) < 91:
        return ord(english_zi) - 64


# 加密
def site_jiami(secret_text, save_path):
    # 输入 1密文 
    # 2明文(明文长度必须大于密文长度 * 1.2 + 1)保证换行可用 
    
    # 起始位置
    length = len(secret_text)
    x_start = 40
    y_start = 40

    # 生成全黑底图 全黑的灰度图
    gray0=np.zeros((220*(length//10+1),2500),dtype=np.uint8)
    print(f'黑底尺寸为 {(220*(length//10+1),2500)}')
    gray0[:,:]=255
    gray255=gray0[:,:]
    Picture=cv2.cvtColor(gray255,cv2.COLOR_GRAY2RGB)
    #将RGB通道全部置成0
    Picture[:,:,0:3]=0
    # cv2.imshow('0', Img_rgb)
    # cv2.waitKey(0)

    # # 先打印一个字
    # Picture = make_picture(ran_zi(), Img_rgb, x_start, y_start)

    num = 1
    for sec_item in secret_text:
        if num == 1:
            # y_start += strand_site_col
            x_start = 40
            # 每行一个字
            print(f'当前坐标位置为 {x_start}, {y_start}')            
            Picture = make_picture(ran_zi(), Picture, x_start, y_start)

        # 对空格的特殊解析
        x_start += (strand_site_row + detect_zi(sec_item)) if sec_item != " " else strand_site_row
        # 打印一个字
        print(f'当前坐标位置为 {x_start}, {y_start}')
        Picture = make_picture(ran_zi(), Picture, x_start, y_start)
        
        # 收尾
        num += 1
        if num %10 == 1:
            num = 1
            y_start += strand_site_col
            # x_start = 20
    
    cv2.imwrite(save_path, Picture)
    # cv2.imshow('3', Picture)
    # 保存
    # cv2.imwrite('site_result.png', Picture)
    # cv2.waitKey(0)    

    # return Picture
    # 输出 加密图片一张

# site_jiami("hellothankwhatismybestbadcatinthehome")
# site_jiami("hello thank you")


# ————————————————
# 版权声明：本文为CSDN博主「captain_CasonCai」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/qq_33671888/article/details/89499311  

# 图像来源网址
# http://616pic.com/sucai/zq9ijmxmv.html