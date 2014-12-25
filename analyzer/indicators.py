# -*- encoding: utf8 -*-
import traceback
import common
import config


def _prepare_per(stock_data, share_data):
    daily_data = stock_data[common.DAILY]
    day = sorted(daily_data.keys(), reverse=True)[0]
    var_per = common.field_var(u'本益比')
    c_key = stock_data[common.META][common.META_CATEGORY_KEY]

    per = daily_data[day][var_per]
    avg_per = share_data['categories'][c_key][day][var_per]
    return per, avg_per


def per_low(stock_data, share_data):
    try:
        per, avg_per = _prepare_per(stock_data, share_data)
    except KeyError as err:
        meta = stock_data['meta']
        common.report_error(u'ERROR: {} {} KeyError: {}'.format(
            meta['stock_no'], meta['name'], err))
        return False
    else:
        return per < avg_per


def per_high(stock_data, share_data):
    try:
        per, avg_per = _prepare_per(stock_data, share_data)
    except KeyError as err:
        meta = stock_data['meta']
        common.report_error(u'ERROR: {} {} KeyError: {}'.format(
            meta['stock_no'], meta['name'], err))
    else:
        return per > avg_per * 2.0


def _prepare_amount(stock_data, share_data):
    daily_data = stock_data[common.DAILY]
    days = sorted(daily_data.keys(), reverse=True)
    latest_day = days[0]
    exam_days = days[1:6]

    var_amount = common.field_var(u'成交量')

    avg_amount = sum((daily_data[d][var_amount]
                      for d in exam_days)) / len(exam_days)
    latest_amount = daily_data[latest_day][var_amount]
    return latest_amount, avg_amount


def amount_low(stock_data, share_data):
    latest_amount, avg_amount = _prepare_amount(stock_data, share_data)
    return latest_amount < avg_amount * 0.7


def amount_high(stock_data, share_data):
    latest_amount, avg_amount = _prepare_amount(stock_data, share_data)
    return latest_amount > avg_amount * 1.5

MAPPINGS = {
    config.PER_LOW: per_low,
    config.PER_HIGH: per_high,
    config.AMOUNT_LOW: amount_low,
    config.AMOUNT_HIGH: amount_high,
    }


def _gather_stocks():
    s = []
    filter_results = common.load_filter_results()
    for n, f in filter_results.items():
        s.extend(f[common.KEY_STOCKS])
    for n, c in config.preferences.items():
        s.extend(c['stocks'])
    return set(s)


def main():
    stocks = _gather_stocks()
    share_data = {
        'categories': common.load_categories()
    }
    indicators = {}
    for no in stocks:
        indicators[no] = {}
        stock_data = common.load_stock(no)
        for n, func in MAPPINGS.items():
            indicators[no][n] = func(stock_data, share_data)
    common.save_indicator_results(indicators)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        common.report_error(traceback.format_exc(e))
        raise
