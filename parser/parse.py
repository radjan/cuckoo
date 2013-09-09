# -*- encoding: utf8 -*-

import urllib2
from bs4 import BeautifulSoup

MILLION = 1000000
ONE = 1
PERCENTAGE = 0.01
COL_PERIOD = u'期別'

STOCK_NO = '2412'

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

MAPPING = {
    # url: (wanted_column_names)
    # QUARTER_MAPPING
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcp/zcpa/zcpa_%s.djhtm': # 資產負債表季表
        (u'資產總額', u'負債總額'),
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcq/zcq_%s.djhtm': # 損益季表
        (u'稅前淨利', u'每股盈餘(元)', u'經常利益', u'本期稅後淨利'),
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zc3/zc3_%s.djhtm': # 現金流量季表
        #(u'稅後淨利', u'投資活動之現金流量'),
        (u'投資活動之現金流量',),
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcr/zcr_%s.djhtm': # 財務比率季表
        (u'營業毛利率', u'負債比率'),
    # ANNUAL_MAPPING
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcp/zcpb/zcpb_%s.djhtm': # 資產負債表年表
        (u'資產總額', u'負債總額'),
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcq/zcqa/zcqa_%s.djhtm': # 損益年表
        (u'稅前淨利', u'每股盈餘(元)', u'經常利益', u'本期稅後淨利'),
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcr/zcra/zcra_%s.djhtm': # 財務比率季表
        (u'營業毛利率', u'負債比率'),
}

FIELDS = {
        # column_name: (variable_name, unit)
        u'資產總額': ('total_assets', MILLION),
        u'負債總額': ('total_debts', MILLION),
        u'稅前淨利': ('net_income_before_tax', MILLION),
        u'每股盈餘(元)': ('eps', ONE),
        u'稅後淨利': ('net_income_after_tax', MILLION),
        u'經常利益': ('net_income_afetr_tax', MILLION),
        u'本期稅後淨利': ('net_income_after_tax_this', MILLION),
        u'投資活動之現金流量': ('cash_flow_of_investment', MILLION),
        u'營業毛利率': ('gross_margin_percentage', PERCENTAGE),
        u'負債比率': ('debt_to_total_assets_ratio', PERCENTAGE),
}

def parse_fubon_url_id(url, wanted):
    # deprecated: use parse_fubon_url instead
    bs = BeautifulSoup(urllib2.urlopen(url), 'lxml')

    #table = _get_by_id(bs, 'oMainTable')
    head = _get_by_id(bs, 'oScrollMenu')
    periods =  _expend_row(head)[1:]

    result = {}

    for tr in _list_elements(head.next_siblings):
        items = _expend_row(tr)
        if len(items) - 1 != len(periods):
            continue
        col_name = items[0].strip()
        if col_name in wanted:
            for i, data in enumerate(items[1:]):
                value = float(data.replace(',', ''))
                var_name, unit = FIELDS[col_name]
                result.setdefault(periods[i], {})[var_name] = value * unit
    return result

def parse_fubon_url(url, wanted):
    bs = BeautifulSoup(urllib2.urlopen(url), 'lxml')

    periods = None
    result = {}

    trs = bs.find_all('tr')
    for tr in trs:
        items = _expend_row(tr)
        if items and items[0]:
            col_name = items[0].strip()
            # assume period title is above the values
            if col_name == COL_PERIOD:
                # there is .1~4Q in value
                periods = [x.replace('.1~4Q', '') for x in items[1:]]
            elif col_name in wanted and periods:
                for i, data in enumerate(items[1:]):
                    value = float(data.replace(',', ''))
                    var_name, unit = FIELDS[col_name]
                    result.setdefault(periods[i], {})[var_name] = value * unit
    return result

def run_once():
    result = {}
    for url, wanted in MAPPING.items():
        url = url % STOCK_NO
        parsed = parse_fubon_url(url, wanted)
        for period, values in parsed.items():
            result.setdefault(period, {}).update(values)
    import pprint
    pprint.pprint(result)

if __name__ == '__main__':
    run_once()
