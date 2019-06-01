 # -*- coding: utf-8 -*-
from __future__ import print_function
import xplore
import json
from colorama import Fore, Back, Style,init
import os,sys
import requests
import re
import math

class Article():
    def __init__(self,info):
        self.downable = True
        self.__url = ''
        # removing invalid characters
        self.__title = re.sub(r"[\/\\\:\*\?\"\<\>\|]",' ',info['title'])
        self.__citing = str(info['citing_paper_count'])
        self.__arnum = ''
        self.__year = str(info['publication_year'])
        self.__pub_title = info['publication_title']
        try:
            self.__pub_num = str(info['publication_number'])
            self.__is_num = str(info['is_number'])
        except KeyError as e:
            self.downable = False

        if('pdf_url' in info.keys()):
            self.__url = info['pdf_url']
            self.__arnum = str(re.findall(r'.*?=(\d+)',self.__url)[0])
        authors = []
        for author in info['authors']['authors']:
            authors.append(author['full_name'])
        self.__author = ','.join(authors)

    def print_info(self,i):
        try:
            if(self.downable):
                print('['+str(i+1)+'] '+Fore.YELLOW+self.__title+Style.RESET_ALL)
            else:
                print(Fore.YELLOW+self.__title+Style.RESET_ALL+' '+Back.RED+'Forbidden to download'+Style.RESET_ALL)
            print('------------------------------------------')
            print(self.__author)
            print(self.__year+' '+self.__pub_title)
            print('cite: '+self.__citing)
            # print(self.__url)
            print('')
        except UnicodeEncodeError as e:
            print('Unicode Encode Error')


    def get_length_url(self,version):
        return('https://ieeexplore.ieee.org/ielx'+str(version)+'/'+self.__pub_num+'/'+self.__is_num+'/'+'0'*(8-len(self.__arnum))+self.__arnum+'.pdf?tp=&arnumber='+self.__arnum+'&isnumber='+self.__is_num+'&ref=')
    
    @property
    def title(self):
        return self.__title
    
    @property
    def download_url(self):
        return 'http://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&isnumber=&arnumber='+self.__arnum
    
    @property
    def headers(self):
        return({
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3',
            'Refer':'https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber='+self.__arnum+'&tag=1',
            'DNT':'1'
        })
    @property
    def filename(self):
        return self.__title+'.pdf'

class IEEEXPLORE():
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}
        self.key = '6rcf2h3cjuxy9c2m9zk9mh8e'
        self.query = xplore.xploreapi.XPLORE(self.key)
        self.query.dataType('JSON')
        self.query.dataFormat('object')
        self.query.resultSetMax = 20
        self.item_per_turn = 1

    def start_query(self,text):
        start = 1
        step = self.query.resultSetMax
        result_max = 10000
        con_flag = True
        while(start < result_max and con_flag):
            self.query.startRecord = start
            con_flag = self.query_by_text(text,start)
            start = start + step
    
    def down_list_mode(self):
        down_list = []
        while(1):
            print(Back.CYAN+'Input query text(Input "start" to start download): '+Style.RESET_ALL)
            text = raw_input()
            if(text == 'start'):
                break
            elif(text == 'exit'):
                sys.exit(0)
            print(Back.GREEN+'Start Searching'+Style.RESET_ALL)
            self.query.queryText(text)
            data = self.query.callAPI()
            total_num = data['total_records']
            articles = data['articles']
            # js = json.dumps(articles, sort_keys=True, indent=4, separators=(',', ':'))
            print('Totally '+str(total_num))
            for i in range(len(articles)):
                article = Article(articles[i])
                # print(Fore.RED + 'some red text')
                article.print_info(i)
                flag = raw_input("Download it? y/n")
                if(flag == 'y' or flag =='Y' or flag =='Yes' or flag =='yes'):
                    down_list.append(article)
                elif(flag == 'exit'):
                    break
                else:
                    continue
            
        print(Back.GREEN+'Start Downloading'+Style.RESET_ALL)
        
        for i in range(len(down_list)):
            item = down_list[i]
            print('Downloading ['+str(i+1)+'] article')
            self.download_pdf(item)
            print(Back.GREEN+'['+str(i+1)+']'+' complete!'+Style.RESET_ALL)

    def query_by_text(self,text,pos):
        self.query.queryText(text)
        # data = query.callAPI()['articles'][0]
        data = self.query.callAPI()
        total_num = data['total_records']
        articles = data['articles']
        # js = json.dumps(articles, sort_keys=True, indent=4, separators=(',', ':'))

        print('Totally '+str(total_num)+' articles ['+str(pos)+'-'+str(pos+self.query.resultSetMax-1)+']')
        con_flag = self.list_articles(articles)
        return con_flag
        
    def list_articles(self,articles):
        articles_list = []
        for i in range(len(articles)):
            article = Article(articles[i])
            # print(Fore.RED + 'some red text')
            article.print_info(i)
            articles_list.append(article)
        down_flag = raw_input('Input num to start downloading: [type exit to end]')
        if(down_flag == 'exit'):
            return False
        elif(down_flag == 'no'):
            return True
        elif(not down_flag):
            return True
        else:
            positions = map(int,down_flag.strip().split(' '))
            for i in positions:
                print('Start downloading article ['+str(i)+']')
                self.download_pdf(articles_list[i-1])
                print(Back.GREEN+'['+str(i)+']'+' complete!'+Style.RESET_ALL)
            # self.download_pdf(articles_list[0])
        return True
    def download_pdf(self,article):
        title = article.title
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
        if (not os.path.isfile('filename')):
            with open(filename,'wb') as f:
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
        

    def test_download(self,num):
        url = 'http://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&isnumber=&arnumber='+str(num)
        with open('test.pdf','wb') as f:
            f.write(self.session.get(url).content)


if __name__ == '__main__':
    ieee = IEEEXPLORE()
    init()

    # list download mode
    ieee.down_list_mode()
    # query mode
    # while(1):
    #     print(Back.CYAN+'Input query text(Input "exit" to close): '+Style.RESET_ALL)
    #     # lines = []
    #     # count = 0
    #     # while True:
    #     #     line = raw_input()
    #     #     if line:
    #     #         lines.append(line)
    #     #         if(line == 'exit'):
    #     #             break
    #     #     else:
    #     #         break
    #     #     count = count+1
    #     #     if(count ==1):
    #     #         break
        
    #     # text = ' '.join(lines)
    #     text = raw_input()
    #     if(text=='exit'):
    #         break
    #     print(Back.GREEN+'Start Searching'+Style.RESET_ALL)
    #     ieee.start_query(text)
