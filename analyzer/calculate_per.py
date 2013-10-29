# -*- encoding: utf8 -*-

import common

def calculate(stock_no):
    '''
    calculate p/e ratio for last year and last 4Q
    '''
    stock_data = common.load_stock(stock_no)
    finance = stock_data[common.FINANCE]

    daily_prices = stock_data[common.DAILY]
    # day format exampe: 101/10/28
    latest_day = sorted((k for k in daily_prices.keys() if k[0].isdigit()), reverse=True)[0]
    latest_daily = daily_prices[latest_day]
    latest_price = latest_daily[_field_name(u'股價')]

    for y, field in ((common.LAST_4Q_YEAR, u'4Q本益比',),
                     (stock_data[common.META][common.LAST_YEAR], u'本益比')):
        try:
            f = None
            if y:
                f = finance[y]
            if f:
                # per 本益比 = 股價 / 每股盈餘(元)
                per = latest_price / f[_field_name(u'每股盈餘(元)')]
                if per < 0:
                    per = 0
                latest_daily[_field_name(field)] = per
        except Exception as e:
            msg = '%s: %s, per failed: %s %s' % (stock_no, y, type(e), e.message)
            common.report_error(msg)

    common.save_stock(stock_no, stock_data)

def _field_name(key):
    return common.FIELDS[key][0]

def main():
    common.save_errors([])
    catalog = common.load_catalog()
    for category, stocks in catalog.items():
        for stock_no in stocks:
            try:
                calculate(stock_no)
            except:
                print stock_no
                raise

if __name__ == '__main__':
    main()
