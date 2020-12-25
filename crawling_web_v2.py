import requests
import re
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import xlwt
import difflib

#get all the links of announcements on the four websites  获取四大交易所公告通知中所有链接
def get_url(webs):
    session = HTMLSession()
    links_all = []
    try:
        for i in range(len(webs)):
            res = session.get(webs[i])
            links_all += res.html.absolute_links
    except requests.exceptions.ConnectionError:
        get_url(webs)
    return links_all

def time_trans(time_str): #['年','月','日'] 用于解析网页日期形式 used to transform the format of date to ['Y','M','D']
    date_list = re.findall(r"\d+\.?\d*",time_str)
    return date_list
def compare_date(time_get): #用于直接比较网页日期与当前系统日期 used to compare the date of announcement and system
     stp = time.strftime('%Y-%m-%d')
    stp_list = time_trans(stp)
    time_getlist = time_trans(time_get)
    if stp_list == time_getlist:
        return True
    else:
        return False

def content_deal(content_temp,title,content_list,title_list): #用于处理公告内容除噪 used to remove noise of content
    content_temp = "".join(content_temp)
    content_temp = "".join(content_temp.split())
    content_list.append(content_temp)
    title_list.append(title)
    return title_list,content_list

def simi_rate(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()

def get_announce(key_list,webs): #获取当日有用的公告通知标题与内容 used to obtain the needed titles and content
    session = HTMLSession()
    links = list(get_url(webs))
    #exclude some useless links排除干扰项链接
    for item in links[:]:
        judgment1 = re.findall(r'./(\d*).htm',item)#sh czce cffex
        judgment2 = re.findall(r'./(\d*)/index.html',item) #dce
        if judgment1 or judgment2:
            pass
        else:
            links.remove(item)

    #Crawl announcements containing certain keywords from the announcement columns of several websites爬取包含关键字关联网页地址
    pairlist = key_list
    important_urls = []
    for i in range(len(links)):
        pair = []
        url = links[i]
        res1 = session.get(url)
        res2 = requests.get(url)
        res2.encoding = 'utf-8' #encoding for chinese if you use English, just remove this line
        soup = BeautifulSoup(res2.text, 'lxml')
        if soup.title:
            title=soup.title.string
        else:
            print('No update today!')        
        for item in pairlist:
            pair_single=re.findall(item,title)
            if pair_single:
                pair = pair_single
            else:
                pass
        if pair:
            important_urls.append(url)

    #crawl the content of website(different website,different processing methods) 抓取网页文本(每个网页的内容爬取需要特别定制)
    content_list = []
    title_list = []
    url_list = []
    print(important_urls)
    for item in important_urls:
        res1 = session.get(item)
        res1.encoding = 'utf-8' #encoding for chinese if you use English, just remove this line
        soup = BeautifulSoup(res1.text, 'lxml')
        title=soup.title.string
        #网页标题去重 remove duplicates
        highest_simi = 0
        simi_list = []
        if title and len(title_list)>=1:
            for i in range(len(title_list)):
                simi_list.append(simi_rate(title,title_list[i]))
            highest_simi = max(simi_list)
        else:
            pass
        if list(map(lambda x: x.text,res1.html.find('p.article-date'))): #获取文章日期 obtain date of the announcement
            time_sh = list(map(lambda x: x.text,res1.html.find('p.article-date')))[0]
        elif list(map(lambda x: x.text,res1.html.find('p.noice_date'))):
            time_dl = list(map(lambda x: x.text,res1.html.find('p.noice_date')))[0]
        elif list(map(lambda x: x.text,res1.html.find('div.fxleft a'))):
            time_zj = list(map(lambda x: x.text,res1.html.find('div.fxleft a')))[0]
        elif list(map(lambda x: x.text,res1.html.find('div.fl span:nth-child(2)'))):
            time_zz = list(map(lambda x: x.text,res1.html.find('div.fl span:nth-child(2)')))[0]
        else:
            pass
            
        if 'www.shfe.com.cn/news/notice' in item and highest_simi<=0.75 and compare_date(time_sh): #去重与日期比较功能  remove duplicates and compare the date，if you need not only today's infomations, just remove the compare_date modules. 
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
        print('No update today!')
        return title_list,content_list,url_list
    else:
        return title_list,content_list,url_list
