 # -*- coding: utf-8 -*-
from __future__ import print_function
import xplore
import json
from colorama import Fore, Back, Style,init
import os,sys
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
        self.query.resultSetMax = 20
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
        for item in articles:
            url = ''
            title = item['title']
            citing = item['citing_paper_count']
            publication_title = item['publication_title']
            year = item['publication_year']
            is_number = str(item['is_number'])
            publication_number = str(item['publication_number'])
            authors = []
            for author in item['authors']['authors']:
                authors.append(author['full_name'])
            parsed_author = ','.join(authors)
            if('pdf_url' in item.keys()):
                url = item['pdf_url']
                ar_number = re.findall(r'.*?=(\d+)',url)[0]
            # print(Fore.RED + 'some red text')
            try:
                print(Fore.YELLOW+title+Style.RESET_ALL)
                print('------------------')
                print(parsed_author)
                print(str(year)+' '+publication_title)
                print('cite: '+str(citing))
                print(is_number)
                print(url)
                print('')
            except:
                continue
            down_flag = raw_input('download?')
            if(down_flag == 'yes'):
                title = title.replace('/',' ')
                self.download_pdf(publication_number,is_number,ar_number,title)
            elif(down_flag=='exit'):
                break
            else:
                continue
    def get_length_url(self,version,p_num,i_num,a_num):
        return('https://ieeexplore.ieee.org/ielx'+str(version)+'/'+str(p_num)+'/'+str(i_num)+'/'+'0'*(8-len(str(a_num)))+str(a_num)+'.pdf?tp=&arnumber='+str(a_num)+'&isnumber='+str(i_num)+'&ref=')
    def download_pdf(self,p_num,i_num,a_num,title):
        title = title.replace('"','')
        url = 'http://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&isnumber=&arnumber='+a_num
        url_length = self.get_length_url(5,p_num,i_num,a_num)
        url_length2 = self.get_length_url(7,p_num,i_num,a_num)
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3',
            'Refer':'https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber='+a_num+'&tag=1',
            'DNT':'1'
        }
        filename = title+'.pdf'
        print('Locating File')
        response_length = str(requests.get(url_length,headers = headers,stream = True).headers.get('Content-Length'))
        if(response_length == '203'):
            response_length = str(requests.get(url_length2,headers = headers,stream = True).headers.get('Content-Length'))
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
                        print("[%s%s]" % ('=' * done, ' ' * (100-done)), end='\r')
                        # sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (100-done)) )    
                        # sys.stdout.flush()
        print()
        print(Back.GREEN+'Complete'+Style.RESET_ALL)

    def test_download(self,num):
        url = 'http://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&isnumber=&arnumber='+str(num)
        with open('test.pdf','wb') as f:
            f.write(self.session.get(url).content)


if __name__ == '__main__':
    ieee = IEEEXPLORE()
    init()
    while(1):
        print('Input query text(Input "exit" to close): ')
        lines = []
        count = 0
        while True:
            line = raw_input()
            if line:
                lines.append(line)
                if(line == 'exit'):
                    break
            else:
                break
            count = count+1
            if(count ==2):
                break
        
        text = ' '.join(lines)
        if(text=='exit'):
            break
        print(Back.GREEN+'Start Searching'+Style.RESET_ALL)
        ieee.query_by_text(text)
