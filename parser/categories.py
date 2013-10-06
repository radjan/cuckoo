# -*- encoding: utf8 -*-

import urllib2
from bs4 import BeautifulSoup

from parser import soup_helper
import common

SEPARATOR = '___'

LISTED_COMPANY = u'上市'
OVER_THE_COUNTER = u'上櫃'

CATELOG = {
    (LISTED_COMPANY, u'水泥'): 'http://tw.stock.yahoo.com/s/list.php?c=%A4%F4%AAd',
    (LISTED_COMPANY, u'食品'): 'http://tw.stock.yahoo.com/s/list.php?c=%AD%B9%AB%7E',
}

STOCK_NO_IDX = 1
COLUMN_IDXES = {
    'price': 3,
    'amount': 7,
}

def _float(s):
    return float(s.strip().replace(',', ''))

def get_category_stock_info(url):
    bs = BeautifulSoup(urllib2.urlopen(url), 'lxml')
    trs = bs.find_all('tr')
    data_date = None
    result = {}
    for tr in trs:
        tds = list(soup_helper.list_elements(tr.children))
        if data_date is None and len(tds) == 2:
            txt = tds[1].text
            d_str = u'資料日期：'
            if d_str in txt:
                data_date = txt[len(d_str):].strip()
        if len(tds) == 13 and len(tds[STOCK_NO_IDX].text.split(' ')) == 2:
            stock_info = tds[STOCK_NO_IDX].text.split(' ')
            stock_no = stock_info[0]
            name = stock_info[1] 
            for var, idx in COLUMN_IDXES.items():
                result.setdefault(stock_no, {})[var] = _float(tds[idx].text)
            result[stock_no]['name'] = name
    return data_date, result

if '__main__' == __name__:
    catalog = {}
    for catalog_key, url in CATELOG.items():
        data_date, result = get_category_stock_info(url)
        stype, category = catalog_key
        for stock_no, data in result.items():
            daily_report = common.load_daily_report(stock_no)
            daily_report['type'] = stype
            daily_report['category'] = category
            daily_report['name'] = data.pop('name')
            daily_report[data_date] = data
            common.save_daily_report(stock_no, daily_report)
            catalog.setdefault(SEPARATOR.join(catalog_key), []).append(stock_no)
    common.save_catalog(catalog)
