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
    (LISTED_COMPANY, u'塑膠'): 'http://tw.stock.yahoo.com/s/list.php?c=%B6%EC%BD%A6',
    (LISTED_COMPANY, u'紡織'): 'http://tw.stock.yahoo.com/s/list.php?c=%AF%BC%C2%B4',
    (LISTED_COMPANY, u'電機'): 'http://tw.stock.yahoo.com/s/list.php?c=%B9q%BE%F7',
    (LISTED_COMPANY, u'電器電纜'): 'http://tw.stock.yahoo.com/s/list.php?c=%B9q%BE%B9%B9q%C6l',
    (LISTED_COMPANY, u'化學'): 'http://tw.stock.yahoo.com/s/list.php?c=%A4%C6%BE%C7',
    (LISTED_COMPANY, u'生技醫療'): 'http://tw.stock.yahoo.com/s/list.php?c=%A5%CD%A7%DE%C2%E5%C0%F8',
    (LISTED_COMPANY, u'玻璃'): 'http://tw.stock.yahoo.com/s/list.php?c=%AC%C1%BC%FE',
    (LISTED_COMPANY, u'造紙'): 'http://tw.stock.yahoo.com/s/list.php?c=%B3y%AF%C8',
    (LISTED_COMPANY, u'鋼鐵'): 'http://tw.stock.yahoo.com/s/list.php?c=%BF%FB%C5K',
    (LISTED_COMPANY, u'橡膠'): 'http://tw.stock.yahoo.com/s/list.php?c=%BE%F3%BD%A6&',
    (LISTED_COMPANY, u'汽車'): 'http://tw.stock.yahoo.com/s/list.php?c=%A8T%A8%AE',
    (LISTED_COMPANY, u'半導體'): 'http://tw.stock.yahoo.com/s/list.php?c=%A5b%BE%C9%C5%E9',
    (LISTED_COMPANY, u'電腦週邊'): 'http://tw.stock.yahoo.com/s/list.php?c=%B9q%B8%A3%B6g%C3%E4',
    (LISTED_COMPANY, u'光電'): 'http://tw.stock.yahoo.com/s/list.php?c=%A5%FA%B9q',
    (LISTED_COMPANY, u'通信網路'): 'http://tw.stock.yahoo.com/s/list.php?c=%B3q%ABH%BA%F4%B8%F4',
    (LISTED_COMPANY, u'電子零組件'): 'http://tw.stock.yahoo.com/s/list.php?c=%B9q%A4l%B9s%B2%D5%A5%F3',
    (LISTED_COMPANY, u'電子通路'): 'http://tw.stock.yahoo.com/s/list.php?c=%B9q%A4l%B3q%B8%F4',
    (LISTED_COMPANY, u'資訊服務'): 'http://tw.stock.yahoo.com/s/list.php?c=%B8%EA%B0T%AAA%B0%C8',
    (LISTED_COMPANY, u'其它電子'): 'http://tw.stock.yahoo.com/s/list.php?c=%A8%E4%A5%A6%B9q%A4l',
    (LISTED_COMPANY, u'營建'): 'http://tw.stock.yahoo.com/s/list.php?c=%C0%E7%AB%D8',
    (LISTED_COMPANY, u'航運'): 'http://tw.stock.yahoo.com/s/list.php?c=%AF%E8%B9B',
    (LISTED_COMPANY, u'觀光'): 'http://tw.stock.yahoo.com/s/list.php?c=%C6%5B%A5%FA',
    (LISTED_COMPANY, u'金融'): 'http://tw.stock.yahoo.com/s/list.php?c=%AA%F7%BF%C4',
    (LISTED_COMPANY, u'貿易百貨'): 'http://tw.stock.yahoo.com/s/list.php?c=%B6T%A9%F6%A6%CA%B3f',
    (LISTED_COMPANY, u'油電燃氣'): 'http://tw.stock.yahoo.com/s/list.php?c=%AAo%B9q%BFU%AE%F0',
    (LISTED_COMPANY, u'其他'): 'http://tw.stock.yahoo.com/s/list.php?c=%A8%E4%A5L',

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
      try:
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
      except:
        print tr
        print url
        raise
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
