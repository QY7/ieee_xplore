 # -*- coding: utf-8 -*-
import xplore
import json
from colorama import Fore, Back, Style,init
import os
import requests
import re

class IEEEXPLORE():
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}
        self.key = '6rcf2h3cjuxy9c2m9zk9mh8e'
        self.query = xplore.xploreapi.XPLORE(self.key)
        self.query.dataType('JSON')
        self.query.dataFormat('object')
        self.query.resultSetMax = 2
        self.item_per_turn = 1

    def query_by_text(self,text):
        self.query.queryText(text)
        # data = query.callAPI()['articles'][0]
        data = self.query.callAPI()
        total_num = data['total_records']
        articles = data['articles']
        # js = json.dumps(articles, sort_keys=True, indent=4, separators=(',', ':'))
        # print(js)
        print('Totally '+str(total_num)+' articles')
        self.list_articles(articles)
        
    def list_articles(self,articles):
        turns = len(articles)/(self.item_per_turn)
        for i in range(turns):
            for item in articles[i*self.item_per_turn:(i+1)*self.item_per_turn]:
                url = ''
                title = item['title']
                citing = item['citing_paper_count']
                publication_title = item['publication_title']
                year = item['publication_year']
                number = item['is_number']
                authors = []
                for author in item['authors']['authors']:
                    authors.append(author['full_name'])
                parsed_author = ','.join(authors)
                if('pdf_url' in item.keys()):
                    url = item['pdf_url']
                    number = re.findall(r'.*?=(\d+)',url)[0]
                # print(Fore.RED + 'some red text')
                try:
                    print(Fore.YELLOW+title+Style.RESET_ALL)
                    print('------------------')
                    print(parsed_author)
                    print(str(year)+' '+publication_title)
                    print('cite: '+str(citing))
                    print(number)
                    print(url)
                    print('')
                except:
                    continue
                down_flag = raw_input('download?')
                if(down_flag == 'no'):
                    continue
                else:
                    title = title.replace('/',' ')
                    
                    self.download_pdf(number,title)
    def download_pdf(self,num,title):
        title = title.replace('"','')
        url = 'http://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&isnumber=&arnumber='+str(num)
        filename = title+'.pdf'
        # filename = 'ts.pdf'
        print('Start downloading "'+title+'"...')
        with open(filename,'wb') as f:
            f.write(self.session.get(url).content)

        print('Complete')

    def test_download(self,num):
        url = 'http://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&isnumber=&arnumber='+str(num)
        with open('test.pdf','wb') as f:
            f.write(self.session.get(url).content)


if __name__ == '__main__':
    ieee = IEEEXPLORE()
    init()
    while(1):
        text = raw_input('Input query text(Input "exit" to close): ')
        if(text=='exit'):
            break
        ieee.query_by_text(text)
    os.system('pause')
