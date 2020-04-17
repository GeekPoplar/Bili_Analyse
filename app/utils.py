from requests import get
from bs4 import BeautifulSoup
import json
from flask import flash, url_for, current_app
import re
import jieba
import collections
import matplotlib.pyplot
from PIL import Image
import numpy as np
import wordcloud
# import matplotlib.pyplot as plt
from time import time

'''
输入：列表长度（整形）
返回：视频信息列表，列表由一系列列表组成，每个二级列表的第一项为视频标题，第二项为视频链接
'''


def get_video_urls(num=10):
    """
    输入：列表长度（整形）
    返回：视频信息列表，列表由一系列列表组成，每个二级列表的第一项为视频标题，第二项为视频链接
    """
    base_url = 'https://www.bilibili.com/ranking'
    try:
        r = get(base_url)
        print(r.status_code)
        soup = BeautifulSoup(r.text, 'html.parser')
        titles = soup.find_all(name='a', attrs={'class': 'title'})
        videos = []
        print(titles[:5])
        for title in titles[:num]:
            video = {'title': title.text, 'url': title.attrs['href']}
            videos.append(video)
        if not videos:
            raise Exception
        # flash('视频列表获取成功！')
        return videos
    except ConnectionError:
        flash("网络连接超时，请检查网络连接后重试！")
    except Exception:
        flash('视频列表获取失败，请稍后再试!')


def get_cid(url):
    """
    输入视频url,返回其cid
    """
    # try:
    bv = url.split('/')[-1]
    url = 'https://api.bilibili.com/x/web-interface/view?bvid=' + bv
    res = get(url)
    res_text = res.text
    res_dict = json.loads(res_text)
    cid = res_dict['data']['cid']
    #flash("视频cid获取成功！")
    return cid
    # except:
    #    flash("视频cid获取失败，请稍后再试！")


def get_bullet_chat(url):
    """
    输入视频url,返回其弹幕列表
    """
    # try:
    cid = get_cid(url)
    bullet_url = 'https://api.bilibili.com/x/v1/dm/list.so?oid=' + str(cid)
    res = get(bullet_url)
    res.xml = res.content.decode('utf-8')
    patt = re.compile('<d.*?>(.*?)</d>')
    bullet_list = patt.findall(res.xml)
    #flash("弹幕获取成功！")
    return bullet_list
    # except:
    #    flash("弹幕获取失败，请稍后再试！")


def word_cloud(segment, title):
    """
    生成词云
    :param bullets: 弹幕列表
    :return: 图片url和排名前10的词
    """

    word_counts = collections.Counter(segment)
    word_counts_top10 = word_counts.most_common(10)
    print(word_counts_top10)

    # mask = np.array(Image.open(url_for('static',filename='background.jpg')))  # 定义词频背景
    # mask = np.array(Image.open('D:/Python Projects/BilibiliRank/app/static/background.jpg'))  # 定义词频背景
    root_dir = current_app.config['ROOT_DIR']
    mask = np.array(Image.open(root_dir + '/static/background.jpg'))  # 定义词频背景
    wc = wordcloud.WordCloud(
        font_path=root_dir+'/static/STFQLBYTJW.ttf',  # 设置字体格式
        mask=mask,  # 设置背景图
        max_words=200,  # 最多显示词数
        max_font_size=100  # 字体最大值
    )

    wc.generate_from_frequencies(word_counts)  # 从字典生成词云
    image_colors = wordcloud.ImageColorGenerator(mask)  # 从背景图建立颜色方案
    wc.recolor(color_func=image_colors)  # 将词云颜色设置为背景图方案
    # wc.to_file(url_for('static',filename='wordcloud/wordcloud.png'))
    r_img_url = '/static/wordcloud/wordcloud' + str(time()) + '.png'
    wc.to_file(root_dir + r_img_url)
    print('图片生成成功！')
    # plt.imshow(wc)  # 显示词云
    # plt.axis('off')  # 关闭坐标轴
    # plt.show()  # 显示图像
    return r_img_url, word_counts_top10


def get_video_info(bv):
    url = 'https://api.bilibili.com/x/web-interface/view?bvid=' + bv
    r = get(url)
    j = json.loads(r.text)
    return j


def get_words(bullets):
    segment = []
    for line in bullets:
        try:
            segs = jieba.cut_for_search(line)  # 用jieba对每条弹幕内容进行分词
            segs = [v for v in segs if not str(v).isdigit()]  # 去数字
            segs = list(filter(lambda x: x.strip(), segs))  # 去左右空格
            for seg in segs:
                if len(seg) > 1 and seg != '\r\n':
                    segment.append(seg)
        except:
            print(line, '提取失败！')
            continue
    return segment

def get_comment(url):
    """
    输入视频url,返回其弹幕列表
    """
    # try:
    bv=bv = url.split('/')[-1]
    aid=get_video_info(bv)['data']['stat']['aid']
    print('aid',aid)
    comment_url = 'https://api.bilibili.com/x/v2/reply?pn=2&type=1&oid=' + str(aid) + "&pn=1&nohot=1&sort=0"
    res = get(comment_url)
    j=json.loads(res.text)
    count=j['data']['page']['count']
    n_page=count//20 + 1
    print('页数',n_page)
    comment_list=[]
    #for n in range(1, n_page):
    for n in range(1, 6):
        url = "https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn=" + str(n) + "&type=1&oid=" + str(
            aid) + "&sort=1&nohot=1"
        req = get(url)
        text = req.text
        json_text_list = json.loads(text)
        for i in json_text_list["data"]["replies"]:
            comment_list.append(i["content"]["message"])
        print('此页爬完',n)
    #flash("弹幕获取成功！")
    return comment_list
    # except:
    #    flash("弹幕获取失败，请稍后再试！")