# encoding:UTF-8
import re, os
import jieba
import jieba.posseg as pseg
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from snownlp import SnowNLP
from PIL import Image
import numpy as np
from wordcloud import WordCloud,ImageColorGenerator
from collections import Counter
import jsonlines


def read_jsonl():
    comment_list = []
    newest_jsonl_path = 'D:/VSCODE/InformationContentSecurityLab/GUI/utils/weibospider/output/newest_jsonl.txt'
    with open(newest_jsonl_path, "r") as f:
        file_name = f.readline()
    file_path = os.path.join(os.path.dirname(newest_jsonl_path), file_name)
    # file_path = 'D:/VSCODE/InformationContentSecurityLab/GUI/utils/weibospider/output/comments.jsonl'
    with jsonlines.open(file_path) as reader:
        for obj in reader:
            comment_list.append(obj['content'])
    # print(comment_list)
    return comment_list

def wordtocloud(textlist):
    fulltext = ''
    isCN = 1
    back_coloring = np.array(Image.open("D:/VSCODE/InformationContentSecurityLab/GUI/utils/weibonlp/bg.jpg"))
    cloud = WordCloud(font_path='D:/VSCODE/InformationContentSecurityLab/GUI/utils/weibonlp/msyh.ttf', # 若是有中文的话，这句代码必须添加，不然会出现方框，不出现汉字
            background_color="white",  # 背景颜色
            max_words=20,  # 词云显示的最大词数
            mask=back_coloring,  # 设置背景图片
            max_font_size=100,  # 字体最大值
            random_state=42,
            width=700, height=702, margin=2,# 设置图片默认的大小,但是如果使用背景图片的话,那么保存的图片大小将会按照其大小保存,margin为词语边缘距离
            )
    for li in textlist:
        fulltext += ' '.join(jieba.cut(li,cut_all = False))
    wc = cloud.generate(fulltext)
    image_colors = ImageColorGenerator(back_coloring)
    plt.figure("词云")
    plt.imshow(wc.recolor(color_func=image_colors))
    wc.to_file('D:/VSCODE/InformationContentSecurityLab/GUI/utils/weibonlp/微博评论词云.png')

def snowanalysis(textlist):
    sentimentslist = []
    for li in textlist:
        s = SnowNLP(li)
        # print(li)
        # print(s.sentiments)
        sentimentslist.append(s.sentiments)
    fig1 = plt.figure("情感分析")
    plt.hist(sentimentslist,bins=np.arange(0,1,0.02))
    plt.show()

def emojilist(textlist):
    emojilist = []
    for li in textlist:
        emojis = re.findall(re.compile(u'(\[.*?\])',re.S),li)
        if emojis:
            for emoji in emojis:
                emojilist.append(emoji)
    emojidict = Counter(emojilist)
    # print(emojidict)
    labels = emojidict.keys()
    sizes = emojidict.values()
    # 绘制饼状图
    # 设置中文字体
    font = FontProperties(fname='D:/VSCODE/InformationContentSecurityLab/GUI/utils/weibonlp/msyh.ttf', size=8)  # 指定字体文件和字号
    plt.figure("微博表情统计")
    plt.rcParams['font.family'] = font.get_name()
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', textprops={'fontproperties': font})
    plt.axis('equal')  # 保证饼状图是正圆形
    # 设置标签字体
    plt.legend(prop=font)
    plt.show()


def analyze_comments():
    #运行
    textlist = read_jsonl()
    wordtocloud(textlist)
    snowanalysis(textlist)
    emojilist(textlist)


if __name__=='__main__':
    analyze_comments()
