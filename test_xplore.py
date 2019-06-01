 # -*- coding: utf-8 -*-
from __future__ import print_function
import xplore
import json
from colorama import Fore, Back, Style,init
import os,sys
import requests
import re

key = '6rcf2h3cjuxy9c2m9zk9mh8e'
query = xplore.xploreapi.XPLORE(key)
query.dataType('JSON')
query.dataFormat('object')
query.resultSetMax = 6
query.startRecord =4
query.queryText('buck')

data = query.callAPI()['articles']

titles = [x['title'] for x in data]

# js = json.dumps(data, sort_keys=True, indent=4, separators=(',', ':'))
# print(js)
print(titles)