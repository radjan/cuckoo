import urllib2
from bs4 import BeautifulSoup

def _get_by_id(bs, idstr):
    return bs.find_all(id=idstr)[0]

def _child_elements(bs):
    for c in bs.children:
        if c.name != None:
            yield c

def _expend_row(bstr):
    ret = []
    for c in _child_elements(bstr):
        ret.append(c.string)
    return ret

url = 'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcp/zcpa/zcpa_2412.djhtm'

bs = BeautifulSoup(urllib2.urlopen(url))

table = _get_by_id(bs, 'oMainTable')
head = _get_by_id(bs, 'oScrollMenu')
print _expend_row(head)
