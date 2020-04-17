from flask import Flask, render_template, url_for, redirect
from app.utils import get_video_urls, get_bullet_chat, word_cloud, get_video_info, get_words, get_comment
from app import app
from app.forms import Video_Url_Form


@app.route('/')
def index():
    videos = get_video_urls(20)
    return render_template('index.html', videos=videos, title='首页')


@app.route('/analyse_index/<bv>')
def analyse_index(bv):
    url = 'https://www.bilibili.com/video/' + bv
    video_info=get_video_info(bv)
    return render_template('analyse_index.html', url=url, bv=bv, video_info=video_info, title='分析')


@app.route('/bullet_analyse/<bv>')
def bullet_analyse(bv):
    url = 'https://www.bilibili.com/video/' + bv
    bullets = get_bullet_chat(url)
    title = get_video_info(bv)['data']['title']
    bullet_words = get_words(bullets)
    bullet_words_img_url, word_counts_top10 = word_cloud(bullet_words, title)
    bullets_img_url, bullet_counts_top10 = word_cloud(bullets, title)
    return render_template('bullet_analyse.html', url=url, title='分析',
                           bullet_words_img_url=bullet_words_img_url,
                           word_counts_top10=word_counts_top10, bullet_counts_top10=bullet_counts_top10,
                           bullets_img_url=bullets_img_url, video_title=title,bv=bv)


@app.route('/get_bv_for_bullet', methods=['GET', 'POST'])
def get_bv_for_bullet():
    form = Video_Url_Form()
    if form.validate_on_submit():
        bv = form.url.data.split('/')[-1]
        return redirect(url_for('analyse_index', bv=bv))
    return render_template('get_bv.html', form=form)

@app.route('/ranking')
def ranking():
    videos = get_video_urls(100)
    return render_template('ranking.html', videos=videos, title='排行榜')

@app.route('/comment_analyse/<bv>')
def comment_analyse(bv):
    url = 'https://www.bilibili.com/video/' + bv
    comments = get_comment(url)
    title = get_video_info(bv)['data']['title']
    comment_words = get_words(comments)
    comment_words_img_url, word_counts_top10 = word_cloud(comment_words, title)
    return render_template('comment_analyse.html', url=url, title='分析',
                           comment_words_img_url=comment_words_img_url,
                           word_counts_top10=word_counts_top10, video_title=title,bv=bv)