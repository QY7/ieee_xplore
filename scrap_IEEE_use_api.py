 # -*- coding: utf-8 -*-
from __future__ import print_function
import xplore
import json
from colorama import Fore, Back, Style,init
import os,sys
import requests
import re
import math
from configparser import ConfigParser

class Article():
    def __init__(self,info):
        self.attrs = {
            'downable':None,
            'url':None,
            'title':None,
            'citing':None,
            'ar_num':None,
            'pub_num':None,
            'is_num':None,
            'year':None,
            'pub_title':None,
            'abstract':None
        }
        self.parser_info(info)
 

    def __getitem__(self, key):
        if key in self.attrs:
            return self.attrs[key]
        return None

    def __len__(self):
        return len(self.attrs)

    def __setitem__(self, key, item):
        self.attrs[key] = item

    def parser_info(self,info):
        '''
        parse json info to properties
        '''
        self['downable'] = True
        
        # removing invalid characters
        self['title'] = re.sub(r"[\/\\\:\*\?\"\<\>\|]",' ',info['title'])
        self['citing'] = str(info['citing_paper_count'])

        try:
            self['pub_num'] = str(info['publication_number'])
            self['is_num'] = str(info['is_number'])
            self['url'] = info['pdf_url']
            self['ar_num'] = str(re.findall(r'.*?=(\d+)',info['pdf_url'])[0])
        except KeyError:
            self['pub_num'] = ''
            self['is_num'] = ''
            self['url'] = ''
            self['ar_num'] = ''
            self['downable'] = False
        self['year'] = str(info['publication_year'])
        self['pub_title'] = info['publication_title']
        try:
            self['abstract'] = info['abstract']
        except KeyError:
            pass

        authors = []
        for author in info['authors']['authors']:
            authors.append(author['full_name'])
        self['author'] = ', '.join(authors)

    def print_info(self,i):
        try:
            if(self['downable']):
                print('['+str(i+1)+'] '+Fore.YELLOW+self['title']+Style.RESET_ALL)
            else:
                print(Fore.YELLOW+self['title']+Style.RESET_ALL+' '+Back.RED+'Forbidden to download'+Style.RESET_ALL)
            print('------------------------------------------')
            print(self['author'])
            print(self['year']+' '+self['pub_title'])
            print('cite: '+self['citing'])
            # print(self.__url)
            print('')
        except UnicodeEncodeError as e:
            print('Unicode Encode Error')


    def get_length_url(self,version):
        return('https://ieeexplore.ieee.org/ielx'+str(version)+'/'+self['pub_num']+'/'+self['is_num']+'/'+'0'*(8-len(self['ar_num']))+self['ar_num']+'.pdf?tp=&arnumber='+self['ar_num']+'&isnumber='+self['is_num']+'&ref=')
    
    @property
    def download_url(self):
        return 'http://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&isnumber=&arnumber='+self['ar_num']
    
    @property
    def headers(self):
        return({
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3',
            'Refer':'https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber='+self['ar_num']+'&tag=1',
            'DNT':'1'
        })
    @property
    def filename(self):
        return self['title']+'.pdf'

class IEEEXPLORE():
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}
        self.key = '6rcf2h3cjuxy9c2m9zk9mh8e'
        self.query = xplore.xploreapi.XPLORE(self.key)
        self.query.dataType('JSON')
        self.query.dataFormat('object')
        self.query.resultSetMax = 10
        self.query.sortField = 'publication_year'
        self.end = False
        self.download_path = ''
        self.read_from_setting()

    def read_from_setting(self):
        cfg = ConfigParser()
        cfg.read('settings.ini')
        self.filterYear(cfg.get('search','start_year'))
        down_path = cfg.get('download','download_path')

        if(down_path and not os.path.isdir(down_path)):
                os.makedirs(down_path)

        self.download_path = down_path

    def start_query(self,text):
        start = 1
        step = self.query.resultSetMax
        result_max = 10000
        while(start < result_max and not self.end):
            res_articles = self.query_from_pos(text,start)
            self.list_articles(res_articles)
            start = start + step

        # prepare for the next search
        self.end = False
    
    # def down_list_mode(self):
    #     down_list = []
    #     while(1):
    #         print(Back.CYAN+'Input query text(Input "start" to start download): '+Style.RESET_ALL)
    #         text = input()
    #         if(text == 'start'):
    #             break
    #         elif(text == 'exit'):
    #             sys.exit(0)
    #         print(Back.GREEN+'Start Searching'+Style.RESET_ALL)
    #         self.query.queryText(text)
    #         data = self.query.callAPI()
    #         total_num = data['total_records']
    #         articles = data['articles']
    #         # js = json.dumps(articles, sort_keys=True, indent=4, separators=(',', ':'))
    #         print('Totally '+str(total_num))
    #         for i in range(len(articles)):
    #             article = Article(articles[i])
    #             # print(Fore.RED + 'some red text')
    #             article.print_info(i)
    #             flag = input("Download it? y/n")
    #             if(flag == 'y' or flag =='Y' or flag =='Yes' or flag =='yes'):
    #                 down_list.append(article)
    #             elif(flag == 'exit'):
    #                 break
    #             else:
    #                 continue
            
    #     print(Back.GREEN+'Start Downloading'+Style.RESET_ALL)
        
    #     for i in range(len(down_list)):
    #         item = down_list[i]
    #         print('Downloading ['+str(i+1)+'] article')
    #         self.download_pdf(item)
    #         print(Back.GREEN+'['+str(i+1)+']'+' complete!'+Style.RESET_ALL)

    def query_from_pos(self,text,start = 0):
        self.query.startRecord = start
        self.query.queryText(text)
        # data = query.callAPI()['articles'][0]
        data = self.query.callAPI()
        total_num = data['total_records']
        if('articles' in data.keys()):
            articles = data['articles']
        else:
            print("No article found")
            return False
        # js = json.dumps(articles, sort_keys=True, indent=4, separators=(',', ':'))

        print('Totally '+str(total_num)+' articles ['+str(start)+'-'+str(start+self.query.resultSetMax-1)+']')
        
        if(start+self.query.resultSetMax>=total_num):
            # end searching
            self.end = True

        return(articles)
        
    def list_articles(self,data):
        '''
        receive raw json data and parse them into articles list and query to download
        '''
        articles_list = []
        for i in range(len(data)):
            article = Article(data[i])
            # print(Fore.RED + 'some red text')
            article.print_info(i)
            articles_list.append(article)
        down_input = input('Input num to start downloading: [type exit to end]')
        if(down_input == 'exit'):
            self.end = True
        elif(down_input == 'no'):
            return
        elif(not down_input):
            return
        else:
            try:
                positions = map(int,down_input.strip().split(' '))
                for i in positions:
                    try:
                        print('Start downloading article ['+str(i)+']')
                        self.download_pdf(articles_list[i-1])
                        print(Back.GREEN+'['+str(i)+']'+' complete!'+Style.RESET_ALL)
                    except:
                        print("Download fail")
            except ValueError:
                print('Input Error')                
                
            # self.download_pdf(articles_list[0])
        return
    def download_pdf(self,article):
        title = article['title']
        url = article.download_url
        headers = article.headers
        filename = article.filename
        print('Locating File')
        i = 7
        response_length ='203'
        while(response_length == '203'):
            url_length = article.get_length_url(i)
            i = i-1
            response_length = str(requests.get(url_length,headers = headers,stream = True).headers.get('Content-Length'))
            if(i==0):
                break
        # print(response_length)
        # filename = 'ts.pdf'
        print('Start downloading "'+title+'"...')
        # print(response_length)
        file_path = self.download_path+'\\'+filename

        if (not os.path.isfile(file_path)):
            with open(file_path,'wb') as f:
                response = self.session.get(url, stream=True)
                
                if response_length =='203': # no content length header
                    print('fail to find size')
                    f.write(response.content)
                    print('no length')
                else:
                    dl = 0
                    total_length = int(response_length)
                    for data in response.iter_content(chunk_size=4096):
                        dl += len(data)
                        f.write(data) 
                        done = int(100 * dl / total_length)
                        cur = int(math.ceil(done/2))
                        print("%2s"%(str(done))+"%%[%s%s]" % ('=' * cur, ' ' * int(50-cur)), end='\r')
                        # sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (100-done)) )    
                        # sys.stdout.flush()
        print()
    def filterYear(self,year):
        self.query.resultsFilter('start_year',str(year))


if __name__ == '__main__':
    ieee = IEEEXPLORE()
    init()
    
            
    # list download mode
    # ieee.down_list_mode()
    # query mode
    while(1):
        print(Back.CYAN+'Input query text(Input "exit" to close): '+Style.RESET_ALL)

        text = input()
        if(text=='exit'):
            break
        print(Back.GREEN+'Start Searching'+Style.RESET_ALL)
        ieee.start_query(text)
