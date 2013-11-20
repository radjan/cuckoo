# -*- encoding: utf8 -*-

import traceback

import common

def calculate(stock_no, average_data):
    '''
    calculate p/e ratio for last year and last 4Q
    '''
    stock_data = common.load_stock(stock_no)
    finance = stock_data.get(common.FINANCE, None)
    if not finance:
        common.report_error('%s does not have finance report!!' % stock_no)
        # XXX new stock no, trigger parse finance report and calculate
        return

    daily_prices = stock_data[common.DAILY]
    # day format exampe: 101/10/28
    latest_day = sorted((k for k in daily_prices.keys() if k[0].isdigit()), reverse=True)[0]
    latest_daily = daily_prices[latest_day]
    latest_price = latest_daily[common.field_var(u'股價')]

    average_day = average_data.setdefault(latest_day, {})

    last_year = stock_data[common.META].get(common.LAST_YEAR, None)

    for y in (common.LAST_4Q_YEAR, last_year):
        f = finance.get(y, None)
        if not f:
            continue
        for field in (u'本益比', u'4Q本益比'):
            try:
                # per 本益比 = 股價 / 每股盈餘(元)
                eps = f.get(common.field_var(u'每股盈餘(元)'), 0)
                if eps > 0:
                    per = latest_price / f[common.field_var(u'每股盈餘(元)')]
                else:
                    per = 0
                field_name = common.field_var(field)
                latest_daily[field_name] = per

                # data for average per
                for postfix in (common.AVG_SUM, common.AVG_COUNT):
                    k = field_name + postfix
                    if k not in average_day:
                        average_day[k] = 0
                if per > 0:
                    average_day[field_name + common.AVG_SUM] += per
                    average_day[field_name + common.AVG_COUNT] += 1
            except Exception as e:
                msg = '%s: %s, per failed: %s %s' % (stock_no, y, type(e), e.message)
                common.report_error(msg)

    # 殖利率 = 股價 / 最近一年股利
    f = finance.get(last_year, None)
    if f:
        dividend = f.get(common.field_var(u'股利'), 0)
        if dividend:
            yield_rate = latest_price / dividend
            latest_daily[common.field_var(u'殖利率')] = yield_rate

    common.save_stock(stock_no, stock_data)

    return latest_day

def calculate_average_per(average_day, total):
    average_day[common.TOTAL] = total
    for field in (u'4Q本益比', u'本益比'):
        field_name = common.field_var(field)
        count = average_day[field_name + common.AVG_COUNT]
        if count:
            avg = average_day[field_name + common.AVG_SUM] / count
        else:
            avg = 0
        average_day[field_name] = avg

def main():
    common.save_errors([])
    catalog = common.load_catalog()
    categories = common.load_categories()
    for category, stocks in catalog.items():
        average_data = categories.setdefault(category, {})
        for stock_no in stocks:
            try:
                latest_day = calculate(stock_no, average_data)
            except:
                print stock_no
                raise
        calculate_average_per(average_data[latest_day], len(stocks))
    common.save_categories(categories)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        common.report_error(traceback.format_exc(e))
        raise
