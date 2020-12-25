import requests
import re
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import xlwt
import difflib

#获取四大交易所公告通知中所有链接
def get_url(webs):
    session = HTMLSession()
    links_all = []
    url = ['http://www.shfe.com.cn/news/notice/','http://www.cffex.com.cn/jysgg/','http://www.cffex.com.cn/jystz/','http://app.czce.com.cn/cms/pub/search/searchdt.jsp','http://www.dce.com.cn/dalianshangpin/yw/fw/jystz/ywtz/index.html']
    try:
        for i in range(len(webs)):
            res = session.get(webs[i])
            links_all += res.html.absolute_links
    except requests.exceptions.ConnectionError:
        get_url(webs)
    return links_all

def time_trans(time_str): #['年','月','日'] 用于解析网页日期形式
    date_list = re.findall(r"\d+\.?\d*",time_str)
    return date_list
def compare_date(time_get): #用于直接比较网页日期与当前系统日期
    stp = time.strftime('%Y-%m-%d')
    stp_list = time_trans(stp)
    time_getlist = time_trans(time_get)
    if stp_list == time_getlist:
        return True
    else:
        return False

def content_deal(content_temp,title,content_list,title_list): #用于处理公告内容除噪
    content_temp = "".join(content_temp)
    content_temp = "".join(content_temp.split())
    content_list.append(content_temp)
    title_list.append(title)
    return title_list,content_list

def simi_rate(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()

def get_announce(key_list,webs): #获取当日有用的公告通知标题与内容
    session = HTMLSession()
    links = list(get_url(webs))
    #排除干扰项，提高运行效率
    for item in links[:]:
        judgment1 = re.findall(r'./(\d*).htm',item)#sh czce cffex
        judgment2 = re.findall(r'./(\d*)/index.html',item) #dce
        if judgment1 or judgment2:
            pass
        else:
            links.remove(item)

    #爬取关键字关联网页地址
    pairlist = key_list
    important_urls = []
    for i in range(len(links)):
        pair = []
        url = links[i]
        res1 = session.get(url)
        res2 = requests.get(url)
        res2.encoding = 'utf-8'
        soup = BeautifulSoup(res2.text, 'lxml')
        if soup.title:
            title=soup.title.string
        else:
            print('今日网站部分无更新！')        
        for item in pairlist:
            pair_single=re.findall(item,title)
            if pair_single:
                pair = pair_single
            else:
                pass
        if pair:
            important_urls.append(url)

    #抓取网页文本
    content_list = []
    title_list = []
    url_list = []
    print(important_urls)
    for item in important_urls:
        res1 = session.get(item)
        res1.encoding = 'utf-8'
        soup = BeautifulSoup(res1.text, 'lxml')
        title=soup.title.string
        #网页标题去重
        highest_simi = 0
        simi_list = []
        if title and len(title_list)>=1:
            for i in range(len(title_list)):
                simi_list.append(simi_rate(title,title_list[i]))
            highest_simi = max(simi_list)
        else:
            pass
        if list(map(lambda x: x.text,res1.html.find('p.article-date'))): #获取文章日期
            time_sh = list(map(lambda x: x.text,res1.html.find('p.article-date')))[0]
        elif list(map(lambda x: x.text,res1.html.find('p.noice_date'))):
            time_dl = list(map(lambda x: x.text,res1.html.find('p.noice_date')))[0]
        elif list(map(lambda x: x.text,res1.html.find('div.fxleft a'))):
            time_zj = list(map(lambda x: x.text,res1.html.find('div.fxleft a')))[0]
        elif list(map(lambda x: x.text,res1.html.find('div.fl span:nth-child(2)'))):
            time_zz = list(map(lambda x: x.text,res1.html.find('div.fl span:nth-child(2)')))[0]
        else:
            pass
            
        if 'www.shfe.com.cn/news/notice' in item and highest_simi<=0.75 and compare_date(time_sh): #去重与日期比较功能
            content_temp = list(map(lambda x: x.text,res1.html.find('div.article-detail-text p')))            
            title_list,content_list = content_deal(content_temp,title,content_list,title_list)
            url_list.append(item)
        elif 'http://www.czce.com.cn' in item and highest_simi<=0.75 and compare_date(time_zz):
            content_temp = list(map(lambda x: x.text,res1.html.find('div.zw_content span')))
            title_list,content_list = content_deal(content_temp,title,content_list,title_list)
            url_list.append(item)
        elif 'www.cffex.com.cn' in item and highest_simi<=0.75 and compare_date(time_zj):
            content_temp = list(map(lambda x: x.text,res1.html.find('div.jysggnr p')))
            title_list,content_list = content_deal(content_temp,title,content_list,title_list)
            url_list.append(item)
        elif 'http://www.dce.com.cn' in item and highest_simi<=0.75 and compare_date(time_dl):
            content_temp = list(map(lambda x: x.text,res1.html.find('div.detail_content p')))        
            title_list,content_list = content_deal(content_temp,title,content_list,title_list)
            url_list.append(item)
        else:
            pass

    if not title_list:
        print('今日网站无新通知！')
        return title_list,content_list,url_list
    else:
        return title_list,content_list,url_list
