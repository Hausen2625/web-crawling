from crawling_web_v2 import get_announce
import pandas as pd

def main():
'''
parameters:   key_list:关键字列表 （列表类型）keyword list(list)
              webs:网页列表（列表类型）webs which need to be crawlled(list)
'''
    key_list = ['2021']
    webs = ['http://www.shfe.com.cn/news/notice/','http://www.cffex.com.cn/jysgg/','http://www.cffex.com.cn/jystz/','http://app.czce.com.cn/cms/pub/search/searchdt.jsp','http://www.dce.com.cn/dalianshangpin/yw/fw/jystz/ywtz/index.html']
    title_list,content_list,url_list = get_announce(key_list,webs)
    #export to the excel 输出到excel并保存
    dataframe = pd.DataFrame(content_list,index = title_list)
    dataframe.to_excel('./announcement_2.xls')
    print('crawl successfully!')
main()
