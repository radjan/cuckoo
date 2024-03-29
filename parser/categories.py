# -*- encoding: utf8 -*-

import traceback

import requests
from bs4 import BeautifulSoup
from progressbar import ProgressBar, FormatLabel

from parser import soup_helper
import common

SEPARATOR = '___'

LISTED_COMPANY = u'上市'
OVER_THE_COUNTER = u'上櫃'

CATELOG = {
    (LISTED_COMPANY, u'水泥'):
        'http://tw.finance.yahoo.com/s/list.php?c=%A4%F4%AAd',
    (LISTED_COMPANY, u'食品'):
        'http://tw.finance.yahoo.com/s/list.php?c=%AD%B9%AB%7E',
    (LISTED_COMPANY, u'塑膠'):
        'http://tw.finance.yahoo.com/s/list.php?c=%B6%EC%BD%A6',
    (LISTED_COMPANY, u'紡織'):
        'http://tw.finance.yahoo.com/s/list.php?c=%AF%BC%C2%B4',
    (LISTED_COMPANY, u'電機'):
        'http://tw.finance.yahoo.com/s/list.php?c=%B9q%BE%F7',
    (LISTED_COMPANY, u'電器電纜'):
        'http://tw.finance.yahoo.com/s/list.php?c=%B9q%BE%B9%B9q%C6l',
    (LISTED_COMPANY, u'化學'):
        'http://tw.finance.yahoo.com/s/list.php?c=%A4%C6%BE%C7',
    (LISTED_COMPANY, u'生技醫療'):
        'http://tw.finance.yahoo.com/s/list.php?c=%A5%CD%A7%DE%C2%E5%C0%F8',
    (LISTED_COMPANY, u'玻璃'):
        'http://tw.finance.yahoo.com/s/list.php?c=%AC%C1%BC%FE',
    (LISTED_COMPANY, u'造紙'):
        'http://tw.finance.yahoo.com/s/list.php?c=%B3y%AF%C8',
    (LISTED_COMPANY, u'鋼鐵'):
        'http://tw.finance.yahoo.com/s/list.php?c=%BF%FB%C5K',
    (LISTED_COMPANY, u'橡膠'):
        'http://tw.finance.yahoo.com/s/list.php?c=%BE%F3%BD%A6&',
    (LISTED_COMPANY, u'汽車'):
        'http://tw.finance.yahoo.com/s/list.php?c=%A8T%A8%AE',
    (LISTED_COMPANY, u'半導體'):
        'http://tw.finance.yahoo.com/s/list.php?c=%A5b%BE%C9%C5%E9',
    (LISTED_COMPANY, u'電腦週邊'):
        'http://tw.finance.yahoo.com/s/list.php?c=%B9q%B8%A3%B6g%C3%E4',
    (LISTED_COMPANY, u'光電'):
        'http://tw.finance.yahoo.com/s/list.php?c=%A5%FA%B9q',
    (LISTED_COMPANY, u'通信網路'):
        'http://tw.finance.yahoo.com/s/list.php?c=%B3q%ABH%BA%F4%B8%F4',
    (LISTED_COMPANY, u'電子零組件'):
        'http://tw.finance.yahoo.com/s/list.php?c=%B9q%A4l%B9s%B2%D5%A5%F3',
    (LISTED_COMPANY, u'電子通路'):
        'http://tw.finance.yahoo.com/s/list.php?c=%B9q%A4l%B3q%B8%F4',
    (LISTED_COMPANY, u'資訊服務'):
        'http://tw.finance.yahoo.com/s/list.php?c=%B8%EA%B0T%AAA%B0%C8',
    (LISTED_COMPANY, u'其它電子'):
        'http://tw.finance.yahoo.com/s/list.php?c=%A8%E4%A5%A6%B9q%A4l',
    (LISTED_COMPANY, u'營建'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C0%E7%AB%D8',
    (LISTED_COMPANY, u'航運'):
        'http://tw.finance.yahoo.com/s/list.php?c=%AF%E8%B9B',
    (LISTED_COMPANY, u'觀光'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C6%5B%A5%FA',
    (LISTED_COMPANY, u'金融'):
        'http://tw.finance.yahoo.com/s/list.php?c=%AA%F7%BF%C4',
    (LISTED_COMPANY, u'貿易百貨'):
        'http://tw.finance.yahoo.com/s/list.php?c=%B6T%A9%F6%A6%CA%B3f',
    (LISTED_COMPANY, u'油電燃氣'):
        'http://tw.finance.yahoo.com/s/list.php?c=%AAo%B9q%BFU%AE%F0',
    (LISTED_COMPANY, u'其他'):
        'http://tw.finance.yahoo.com/s/list.php?c=%A8%E4%A5L',

    (OVER_THE_COUNTER, u'食品'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%AD%B9%AB%7E',
    (OVER_THE_COUNTER, u'塑膠'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%B6%EC%BD%A6',
    (OVER_THE_COUNTER, u'紡織'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%AF%BC%C2%B4',
    (OVER_THE_COUNTER, u'電機'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%B9q%BE%F7',
    (OVER_THE_COUNTER, u'電器'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%B9q%BE%B9',
    (OVER_THE_COUNTER, u'化工'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%A4%C6%A4u',
    (OVER_THE_COUNTER, u'生技'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%A5%CD%A7%DE',
    (OVER_THE_COUNTER, u'油電'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%AAo%B9q',
    (OVER_THE_COUNTER, u'鋼鐵'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%BF%FB%C5K',
    (OVER_THE_COUNTER, u'橡膠'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%BE%F3%BD%A6',
    (OVER_THE_COUNTER, u'半導'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%A5b%BE%C9',
    (OVER_THE_COUNTER, u'電腦'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%B9q%B8%A3',
    (OVER_THE_COUNTER, u'光電'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%A5%FA%B9q',
    (OVER_THE_COUNTER, u'通信'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%B3q%ABH',
    (OVER_THE_COUNTER, u'電零'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%B9q%B9s',
    (OVER_THE_COUNTER, u'通路'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%B3q%B8%F4',
    (OVER_THE_COUNTER, u'資服'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%B8%EA%AAA',
    (OVER_THE_COUNTER, u'他電'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%A5L%B9q',
    (OVER_THE_COUNTER, u'營建'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%C0%E7%AB%D8',
    (OVER_THE_COUNTER, u'航運'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%AF%E8%B9B',
    (OVER_THE_COUNTER, u'觀光'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%C6%5B%A5%FA',
    (OVER_THE_COUNTER, u'金融'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%AA%F7%BF%C4',
    (OVER_THE_COUNTER, u'貿易'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%B6T%A9%F6',
    (OVER_THE_COUNTER, u'其他'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%A8%E4%A5L',
    (OVER_THE_COUNTER, u'管理'):
        'http://tw.finance.yahoo.com/s/list.php?c=%C2d%BA%DE%B2z',
}


STOCK_NO_IDX = 1
COLUMN_IDXES = {
    'price': 3,
    'amount': 7,
}


def get_category_stock_info(url):
    bs = BeautifulSoup(requests.get(url).text, 'lxml')
    # Get the form which contains stock list
    stock_list_form = _get_stock_list_form(bs)
    trs = stock_list_form.find_all('tr')
    data_date = None
    result = {}
    for tr in trs:
        try:
            tds = tr.find_all('td')
            if data_date is None and len(tds) == 2:
                txt = tds[1].text
                d_str = u'資料日期：'
                if d_str in txt:
                    data_date = txt[len(d_str):].strip()
            if len(tds) == 13 and len(tds[STOCK_NO_IDX].text.split(' ')) == 2:
                stock_info = tds[STOCK_NO_IDX].text.split(' ')
                stock_info = [txt.strip() for txt in stock_info]
                stock_no = stock_info[0]
                name = stock_info[1]
                stock_result = result.setdefault(stock_no, {})
                stock_result['name'] = name
                for var, idx in COLUMN_IDXES.items():
                    try:
                        stock_result[var] =\
                            soup_helper.to_float(tds[idx].text)
                    except ValueError:
                        # convert symbol － to 0
                        stock_result[var] = 0.0
                    except Exception:
                        print stock_no, var, tds[idx].text
                        raise
        except:
            print tr
            print url
            raise
    return data_date, result


def _get_stock_list_form(bs):
    forms = bs.find_all('form')
    for form in forms:
        if _is_stock_list_form(form):
            return form

def _is_stock_list_form(form):
    inputs = form.find_all('input')
    # for input in inputs:
    # print 'inputs', len(inputs)
    # print inputs
    for i in inputs:
        if 'name' in i.attrs and i.attrs['name'] == 'stknum':
            return True
    return False


def _total_stocks():
    total = 0
    catalog = common.load_catalog()
    for _c, stocks in catalog.items():
        for _stock in stocks:
            total += 1
    return total


def main():
    catalog = {}
    curr_data_date = None

    # Add some more to prevent error when new stocks found
    total = _total_stocks() + 10

    widgets = [FormatLabel('Processed: %(value)d / {0} (in: %(elapsed)s)'.
                           format(total))]
    pbar = ProgressBar(widgets=widgets, maxval=total)
    count = 0
    pbar.start()
    state = common.load_state()

    for catalog_key, url in CATELOG.items():
        data_date, result = get_category_stock_info(url)
        if not result:
            raise Exception('Empty parsing result, key: {}, url: {}'
                .foramt(catalog_key, url))
        if curr_data_date is None:
            curr_data_date = data_date
        elif curr_data_date != data_date:
            msg = 'Data date is not the same!'\
                ' curr_data_date: %s, data_date: %s, url: %s'\
                % (curr_data_date, data_date, url)
            common.report_error(msg)
            raise Exception(msg)

        stype, category = catalog_key
        for stock_no, data in result.items():
            stock_data = common.load_stock(stock_no)
            daily_report = stock_data.setdefault(common.DAILY, {})
            meta = stock_data.setdefault(common.META, {})
            daily_report[data_date] = data
            category_key = SEPARATOR.join(catalog_key)
            meta.update({
                common.META_STOCK_NO: stock_no,
                common.META_COMPANY_TYPE: stype,
                common.META_COMPANY_CATEGORY: category,
                common.META_CATEGORY_KEY: category_key,
                common.META_NAME: data.pop('name'),
                common.META_DAYS: sorted(daily_report.keys(), reverse=True),
            })
            stock_data.setdefault(common.META, {}).update(meta)
            common.save_stock(stock_no, stock_data)
            catalog.setdefault(category_key, []).append(stock_no)
            pbar.update(count)
            count += 1

        if not catalog.setdefault(SEPARATOR.join(catalog_key), []):
            common.report_error('NO STOCK FOUND!!!! %s, %s'
                                % (catalog_key, url))
    common.save_catalog(catalog)
    state[common.CURRENT_DATA_DATE] = curr_data_date
    common.save_state(state)
    pbar.finish()


if '__main__' == __name__:
    try:
        main()
    except Exception as e:
        common.report_error(traceback.format_exc(e))
        raise
