# -*- encoding: utf8 -*-
import common
import config

class NoData(Exception):
    pass

def kazuyo_katsuma(stock_no, stock_data):
    finance = stock_data[common.FINANCE]
    meta = stock_data[common.META]
    wanted = (common.LAST_4Q_YEAR, meta[common.LAST_YEAR])
    #wanted = (meta[common.LAST_YEAR],)
    for y in wanted:
        if not y:
            raise NoData("Missing last_year report")
        if not negative_accrual(finance[y], period=y):
            return False
    quarters = meta[common.QUARTERS]
    var_roa = common.field_var(u'總資產報酬率')

    def roa_growth(q, last_q):
        qf = finance[q]
        last_qf = finance[last_q]
        if var_roa in qf and var_roa in last_qf:
            return qf[var_roa] - last_qf[var_roa] > 0
        raise NoData('Missing ROA data for %s or %s' % (q, last_q))

    return continous(quarters[:5], roa_growth)

def old_brother(stock_no, stock_data):
    finance = stock_data[common.FINANCE]
    meta = stock_data[common.META]
    last_year = meta[common.LAST_YEAR]

    wanted = (common.LAST_4Q_YEAR, last_year)
    for y in wanted:
        if not y:
            raise NoData("Missing last_year report")
        if not enough_value(finance[y], u'權責發生額', 0, period=y,
                            reverse=True):
            return False

    if not enough_value(finance[last_year], u'股利',
                        0.05, period=last_year):
        return False

    recent_years = meta[common.ANNUALS][:3]
    recent_years.insert(0, common.LAST_4Q_YEAR)
    for y in recent_years:
        report = finance[y]
        if not all((enough_value(report, u'營業毛利率', 0.3, period=y),
                    enough_value(report, u'負債比率', 0.3, period=y,
                                 reverse=True))):
            return False

    def loose_eps_growth(y1, _y2, y3):
        var = common.field_name(u'每股盈餘(元)')
        f1 = finance[y1]
        f3 = finance[y3]
        return f1[var] - f3[var] > 0

    return continous(recent_years, losseps_growth, window=3)

def negative_accrual(finance_report, period=None):
    accrual = common.field_var(u'權責發生額')
    if accrual in finance_report:
        return finance_report[accrual] < 0
    raise NoData('Missing accrual data for %s' % period)

def enough_value(finance_report, field, threshold, period=None, reverse=False):
    var_name = common.field_var(field)
    if var_name in finance_report:
        ret = finance_report[var_name] >= threshold
        if reverse:
            ret = not ret
        return ret
    raise NoData('Missing %s data for %s' % (var_name, period))

def continous(l, func, window=2):
    if l:
        interval = window - 1
        return all([func(*(l[i] for i in xrange(x, x + window))) for x in xrange(len(l) - interval)])
    return False

def main():
    result = {}
    catalog = common.load_catalog()
    for category, stocks in catalog.items():
        for stock_no in stocks:
            stock_data = common.load_stock(stock_no)
            for filter_name, filter_func in filters.items():
                try:
                    if filter_func(stock_no, stock_data):
                        data = result.setdefault(filter_name, {})
                        data.setdefault(common.KEY_STOCKS, []).append(stock_no)
                except NoData as e:
                    data = result.setdefault(filter_name, {})
                    data.setdefault(common.KEY_MISSING_DATA, []).append(stock_no)
                except Exception as e:
                    print stock_no
                    raise

    for k, v in result.items():
        print k, len(v[common.KEY_STOCKS]), len(v[common.KEY_MISSING_DATA])
    common.save_filter_results(result)

filters = {
    config.KAZUYO_KATSUMA: kazuyo_katsuma,
    config.OLD_BROTHER: old_brother,
}

if __name__ == '__main__':
    main()
