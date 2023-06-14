from os import path
from . import chnSegment
from . import plotWordcloud


def draw_word_cloud_picture():
    # 读取文件
    d = path.dirname(__file__)
    with open(path.join(d, "doc//temp.txt"), "r", encoding="utf-8") as f:
        text = f.read()

    # with open(path.join(d, 'doc//alice.txt'), 'r', encoding='utf-8') as f:
    # text = f.read()

    # text = open(path.join(d,'doc//alice.txt')).read()

    # 若是中文文本，则先进行分词操作
    text = chnSegment.word_segment(text)

    # 生成词云
    plotWordcloud.generate_wordcloud(text)


if __name__ == "__main__":
    draw_word_cloud_picture()
