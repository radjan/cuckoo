# -*- encoding: utf8 -*-

import sys
import traceback
import urllib2
from bs4 import BeautifulSoup
from progressbar import ProgressBar, FormatLabel

import soup_helper
import common

COL_PERIOD = u'期別'

MAPPING = {
    # url: (wanted_column_names)
    # QUARTER_MAPPING
    # 資產負債表季表
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcp/zcpa/zcpa_%s.djhtm':
        (u'資產總額', u'負債總額'),
    # 損益季表
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcq/zcq_%s.djhtm':
        (u'稅前淨利', u'每股盈餘(元)', u'經常利益', u'本期稅後淨利'),
    # 現金流量季表
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zc3/zc3_%s.djhtm':
        # (u'稅後淨利', u'投資活動之現金流量'),
        (u'投資活動之現金流量', u'來自營運之現金流量'),
    # 財務比率季表
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcr/zcr_%s.djhtm':
        (u'營業毛利率', u'負債比率'),

    # ANNUAL_MAPPING
    # 資產負債表年表
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcp/zcpb/zcpb_%s.djhtm':
        (u'資產總額', u'負債總額'),
    # 損益年表
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcq/zcqa/zcqa_%s.djhtm':
        (u'稅前淨利', u'每股盈餘(元)', u'經常利益', u'本期稅後淨利'),
    # 財務比率季表
    'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcr/zcra/zcra_%s.djhtm':
        (u'營業毛利率', u'負債比率'),
}

DIVIDEND_URL = 'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zcc/zcc_%s.djhtm'


def parse_fubon_url(url, wanted):
    bs = BeautifulSoup(urllib2.urlopen(url), 'lxml')

    periods = None
    result = {}

    trs = bs.find_all('tr')
    for tr in trs:
        items = soup_helper.expend_row(tr)
        if items and items[0]:
            col_name = items[0].strip()
            # assume period title is above the values
            if col_name == COL_PERIOD:
                # there is .1~4Q in value
                periods = [x.replace('.1~4Q', '') for x in items[1:]]
            elif col_name in wanted and periods:
                for i, data in enumerate(items[1:]):
                    value = soup_helper.to_float(data)
                    var_name, unit = common.FIELDS[col_name]
                    result.setdefault(periods[i], {})[var_name] = value * unit
    return result


def parse_dividend(stock_no):
    def _key(s):
        return s if s != u'合計' else u'股利'

    bs = BeautifulSoup(urllib2.urlopen(DIVIDEND_URL % stock_no), 'lxml')

    titles = None
    result = {}

    trs = bs.find_all('tr')
    for tr in trs:
        items = soup_helper.expend_row(tr)
        if len(items) != 7:
            continue
        # title first
        if titles is None:
            # 年度, 現金股利, 盈餘配股, 公積配股, 股票股利, 合計, 員工配股率%
            titles = [_key(k) for k in items]
        else:
            wanted = (1, 4, 5)
            d = {}
            for idx in wanted:
                var_name, unit = common.FIELDS[titles[idx]]
                d[var_name] = soup_helper.to_float(items[idx]) * unit
            result[items[0]] = d
    return result


def run_once(stock_no):
    result = common.load_finance_report(stock_no)
    for url, wanted in MAPPING.items():
        url = url % stock_no
        parsed = parse_fubon_url(url, wanted)
        for period, values in parsed.items():
            result.setdefault(period, {}).update(values)
    for period, values in parse_dividend(stock_no).items():
            result.setdefault(period, {}).update(values)

    common.save_finance_report(stock_no, result)


def main(no=-1):
    catalog = common.load_catalog()
    todo = []
    if no == -1:
        for _c, s in catalog.items():
            todo.extend(s)
    else:
        for i, (_c, s) in enumerate(catalog.items()):
            if no == i:
                todo.extend(s)
    total = len(todo)
    count = 0
    widgets = [FormatLabel('Processed: %(value)d / {0} (in: %(elapsed)s)'.
                           format(total))]
    pbar = ProgressBar(widgets=widgets, maxval=total)
    pbar.start()
    for stock_no in todo:
        run_once(stock_no)
        pbar.update(count)
        count += 1
    pbar.finish()


if __name__ == '__main__':
    try:
        no = -1
        if len(sys.argv) == 2:
            no = int(sys.argv[1])
            if no >= 100:
                run_once(no)
                sys.exit()
        main(no)
    except Exception as e:
        common.report_error(traceback.format_exc(e))
        raise


# deprecated: use parse_fubon_url instead
def parse_fubon_url_id(url, wanted):
    bs = BeautifulSoup(urllib2.urlopen(url), 'lxml')

    # table = _get_by_id(bs, 'oMainTable')
    head = soup_helper.get_by_id(bs, 'oScrollMenu')
    periods = soup_helper.expend_row(head)[1:]

    result = {}

    for tr in soup_helper.list_elements(head.next_siblings):
        items = soup_helper.expend_row(tr)
        if len(items) - 1 != len(periods):
            continue
        col_name = items[0].strip()
        if col_name in wanted:
            for i, data in enumerate(items[1:]):
                value = soup_helper.to_float(data)
                var_name, unit = common.FIELDS[col_name]
                result.setdefault(periods[i], {})[var_name] = value * unit
    return result
