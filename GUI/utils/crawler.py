import json
import re
import requests
from bs4 import BeautifulSoup
from scrapy import Spider, Request
# from spiders.common import parse_tweet_info, parse_long_tweet
from datetime import datetime, timedelta
from urllib.parse import quote


def find_hot_topics(self):
    """
    寻找当日的热点话题
    """
    keywords = []
    url = "https://weibo.cn/pub/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    links = soup.find_all("a")
    pattern = r"#[^#]*#"
    for link in links:
        # print(link.text)
        matches = re.findall(pattern, link.text)
        if matches:
            for str in matches:
                keywords.append(str)
    # keywords = ['#终于知道为什么老说猴急了#', '#阿根廷国家队关于中国行声明#']
    return keywords