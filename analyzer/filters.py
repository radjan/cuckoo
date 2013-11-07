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
    pass

def negative_accrual(finance_report, period=None):
    accrual = common.field_var(u'權責發生額')
    if accrual in finance_report:
        return finance_report[accrual] < 0
    raise NoData('Missing accrual data for %s' % period)
    return False

def continous(l, func):
    if l:
        return all((func(l[i], l[i+1]) for i in xrange(len(l) - 1)))
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
                    print stock_no, e.message
                    #pass

    for k, v in result.items():
        print k, len(v[common.KEY_STOCKS])
    common.save_filter_results(result)

filters = {
    config.KAZUYO_KATSUMA: kazuyo_katsuma,
    config.OLD_BROTHER: old_brother,
}

if __name__ == '__main__':
    main()
