import requests
import re
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd


session = HTMLSession()


#get all the links of announcements on the four websites  获取四大交易所公告通知中所有链接
def get_url():
    links_all = []
    url = ['http://www.shfe.com.cn/news/notice/','http://www.cffex.com.cn/jysgg/','http://www.cffex.com.cn/jystz/','http://app.czce.com.cn/cms/pub/search/searchdt.jsp','http://www.dce.com.cn/dalianshangpin/yw/fw/jystz/ywtz/index.html']

    for i in range(len(url)):
        
        res = session.get(url[i])

        links_all += res.html.absolute_links

    #result=re.findall(r'<td><a href='(/.*?)'\starget=_blank',res_text,re.DOTALL)

    return links_all
links = list(get_url())


#exclude some useless links排除干扰项链接
for item in links[:]:
    judgment1 = re.findall(r'./(\d*).htm',item)#sh czce cffex
    judgment2 = re.findall(r'./(\d*)/index.html',item) #dce
    if judgment1:
        links = links
    elif judgment2:
        links = links
    else:
        links.remove(item)


#Crawl announcements containing certain keywords from the announcement columns of several websites爬取包含关键字关联网页地址
pairlist = ['交割有效期限','涨跌停板幅度','股指期货','股指期权','PTA交割'] #keywords list 关键字列表
important_urls = []
for i in range(len(links)):
    pair = []
    url = links[i]

    res1 = session.get(url)
    res2 = requests.get(url)
    res2.encoding = 'utf-8' #encoding for chinese if you use English, just remove this line
    soup = BeautifulSoup(res2.text, 'lxml')
    title=soup.title.string
    
    for item in pairlist:
        pair_single=re.findall(item,title)
        if pair_single:
            pair = pair_single       
    if pair:
        important_urls.append(url)
    #print('pair:',pair)
    #print('important_urls:',important_urls)
    
print(important_urls)

#crawl the content of website(different website,different processing methods) 抓取网页文本(每个网页的内容爬取需要特别定制)
main_addresslist = ['http://www.shfe.com.cn','http://www.cffex.com.cn','http://app.czce.com.cn','http://www.dce.com.cn']
content_list = []
for i in range(len(important_urls)):
    res1 = session.get(important_urls[i])
    if 'http://www.shfe.com.cn' in important_urls[i]:
        content_list.append(list(map(lambda x: x.text,res1.html.find('div.article-detail-text p'))))
    elif 'http://app.czce.com.cn' in important_urls[i]:
        content_list.append(list(map(lambda x: x.text,res1.html.find('div.zw_content span'))))
    elif 'http://www.cffex.com.cn' in important_urls[i]:
        content_list.append(list(map(lambda x: x.text,res1.html.find('div.jysggnr p'))))
    elif 'http://www.dce.com.cn' in important_urls[i]:
        content_list.append(list(map(lambda x: x.text,res1.html.find('div.detail_content p'))))        
#print(content_list)

#export to the excel 输出到excel并保存
dataframe = pd.DataFrame(content_list)
dataframe.to_excel('./announcement.xls')
    

'''
初始版本待后续更新 waiting for updating
'''
