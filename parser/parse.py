# -*- encoding: utf8 -*-

import urllib2
from bs4 import BeautifulSoup

def _get_by_id(bs, idstr):
    return bs.find_all(id=idstr)[0]

def _list_elements(bslist):
    for c in bslist:
        if c.name != None:
            yield c

def _expend_row(bstr):
    ret = []
    for c in _list_elements(bstr.children):
        ret.append(c.string)
    return ret

url = 'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcp/zcpa/zcpa_2412.djhtm'
wanted = (u'資產總額', u'負債總額')

bs = BeautifulSoup(urllib2.urlopen(url))

#table = _get_by_id(bs, 'oMainTable')
head = _get_by_id(bs, 'oScrollMenu')
periods =  _expend_row(head)[1:]

result = {}

for td in _list_elements(head.next_siblings):
    items = _expend_row(td)
    title = items[0].strip()
    if title in wanted:
        for i, data in enumerate(items[1:]):
            result.setdefault(periods[i], {})[title] = int(data.replace(',', ''))

import pprint
pprint.pprint(result)
