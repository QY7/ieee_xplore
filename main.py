import requests
import re

def query(key):
    session=requests.Session()
    proxy_dict = {
    "http": "http://username:password@hogehoge.proxy.jp:8080/",
    "https": "http://username:password@hogehoge.proxy.jp:8080/"
} 
    key = key.replace(' ','%20')
    url = 'https://www.google.com'
    
    html = requests.get(url).text

    return(html)

print(query('capacitor'))

