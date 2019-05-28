 # -*- coding: utf-8 -*-
import xplore
import json
from colorama import Fore, Back, Style,init
import os

def query_by_text(text,query):
    query.queryText(text)
    # data = query.callAPI()['articles'][0]
    data = query.callAPI()
    total_num = data['total_records']
    articles = data['articles']
    # js = json.dumps(articles, sort_keys=True, indent=4, separators=(',', ':'))
    # print(js)
    print('Totally '+str(total_num)+' articles')
    for item in articles:
        url = ''
        title = item['title']
        citing = item['citing_paper_count']
        publication_title = item['publication_title']
        year = item['publication_year']
        if 'html_url' in item.keys():
            url = item['html_url']
        authors = []
        for author in item['authors']['authors']:
            authors.append(author['full_name'])
        parsed_author = ','.join(authors)
        # print(Fore.RED + 'some red text')   
        try:
            print(Fore.YELLOW+title+Style.RESET_ALL)
            print('------------------')
            print(parsed_author)
            print(str(year)+' '+publication_title)
            print('cite: '+str(citing))
            print(url)
            print('')
        except:
            continue
    # print(js)
    # for item in data:
    #     js = json.dumps(item, sort_keys=True, indent=4, separators=(',', ':'))
    #     print(js)
        # try:
        #         print(item['title'])
        #         print(item['author'])
        # except:
        #     continue
    # print(json.dumps(data,sort_keys=True, indent=2))
def get_number(doi):
    number = 0
    # try:
    try:
        data = query.doi(doi)
        query.dataType('JSON')
        query.dataFormat('object')
        data = query.callAPI()
        data = data['articles'][0]
        title = data['title']
        number = data['article_number']
    except Error as e:
        print(e)
    return number,title

if __name__ == '__main__':
    init()
    key = '6rcf2h3cjuxy9c2m9zk9mh8e'
    query = xplore.xploreapi.XPLORE(key)
    # query.maximumResults(200)
    query.dataType('JSON')
    query.dataFormat('object')
    query.resultSetMax = 20
    while(1):
        text = raw_input('Input query text(Input "exit" to close): ')
        if(text=='exit'):
            break
        query_by_text(text,query)
    os.system('pause')
