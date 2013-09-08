# -*- encoding: utf8 -*-

import urllib2
from bs4 import BeautifulSoup

MILLION = 1000000
ONE = 1
PERCENTAGE = 0.01
PERIOD = u'期別'

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

SEASON_MAPPING = {
    # url: (wanted_column_names)
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcp/zcpa/zcpa_2412.djhtm': # 資產負債表季表
        (u'資產總額', u'負債總額'),
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcq/zcq_2412.djhtm': # 損益季表
        (u'稅前淨利', u'每股盈餘(元)'),
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zc3/zc3_2412.djhtm': # 現金流量季表
        (u'稅後淨利', u'投資活動之現金流量'),
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcr/zcr_2412.djhtm': # 財務比率季表
        (u'營業毛利率', u'負債比率'),
}

YEAR_MAPPING = {
    # url: (wanted_column_names)
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcp/zcpb/zcpb_2412.djhtm': # 資產負債表年表
        (u'資產總額', u'負債總額'),
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcq/zcqa/zcqa_2412.djhtm': # 損益年表
        (u'稅前淨利', u'每股盈餘(元)'),
}

FIELDS = {
        # column_name: (variable_name, unit)
        u'資產總額': ('total_assets', MILLION),
        u'負債總額': ('total_debts', MILLION),
        u'稅前淨利': ('net_profit_before_tax', MILLION),
        u'每股盈餘(元)': ('eps', ONE),
        u'稅後淨利': ('net_profit_after_tax', MILLION),
        u'投資活動之現金流量': ('cash_flow_of_investment', MILLION),
        u'營業毛利率': ('gross_margin_percentage', PERCENTAGE),
        u'負債比率': ('debt_to_total_assets_ratio', PERCENTAGE),
}

def parse_fubon_url(url, wanted):
    bs = BeautifulSoup(urllib2.urlopen(url), 'lxml')

    #table = _get_by_id(bs, 'oMainTable')
    head = _get_by_id(bs, 'oScrollMenu')
    periods =  _expend_row(head)[1:]

    result = {}

    for td in _list_elements(head.next_siblings):
        items = _expend_row(td)
        if len(items) - 1 != len(periods):
            continue
        title = items[0].strip()
        if title in wanted:
            for i, data in enumerate(items[1:]):
                value = float(data.replace(',', ''))
                var_name, unit = FIELDS[title]
                result.setdefault(periods[i], {})[var_name] = value * unit
    return result

def run_once():
    result = {}
    for url, wanted in SEASON_MAPPING.items():
        parsed = parse_fubon_url(url, wanted)
        for period, values in parsed.items():
            result.setdefault(period, {}).update(values)
    import pprint
    pprint.pprint(result)

if __name__ == '__main__':
    run_once()
