# -*- encoding: utf8 -*-

import traceback

import common
import config


ERROR = common.logger.error
INFO = common.logger.info
COUNTS = {}
def _c(key, c=1):
    if key in COUNTS:
        COUNTS[key] += c
    else:
        COUNTS[key] = c

def _o():
    for key in sorted(COUNTS.keys()):
        INFO('{} = {}'.format(key, COUNTS[key]))


class NoData(Exception):
    pass


def kazuyo_katsuma(s_no, stock_data):
    finance = stock_data[common.FINANCE]
    meta = stock_data[common.META]
    if common.LAST_YEAR not in meta:
        m = '[KK] %s: missing last_year finance report' % s_no
        ERROR(m)
        raise NoData(m)
    wanted = (common.LAST_4Q_YEAR, meta[common.LAST_YEAR])
    # wanted = (meta[common.LAST_YEAR],)
    for y in wanted:
        if not y:
            m = "[KK] %s: Missing last_year report" % s_no
            ERROR(m)
            raise NoData(m)
        if not enough_value(finance[y], u'本期稅後淨利', 0.0, period=y,
                            s_no=s_no):
            return False
        if not negative_accrual(finance[y], period=y, s_no=s_no):
            return False
    quarters = meta[common.QUARTERS]
    var_roa = common.field_var(u'總資產報酬率')

    def roa_growth(q, last_q):
        qf = finance[q]
        last_qf = finance[last_q]
        if var_roa in qf and var_roa in last_qf:
            return qf[var_roa] - last_qf[var_roa] > 0
        m = '[[KK] %s: Missing ROA data for %s or %s' % (s_no, q, last_q)
        ERROR(m)
        raise NoData(m)

    try:
        return continous(quarters[:5], roa_growth)
    except Exception, e:
        print s_no, e
        raise


def old_brother(s_no, stock_data):
    finance = stock_data[common.FINANCE]
    meta = stock_data[common.META]
    if common.LAST_YEAR not in meta:
        m = '[OB] %: missing last_year finance report' % s_no
        raise NoData('missing last_year finance report')
    last_year = meta[common.LAST_YEAR]

    # wanted = (common.LAST_4Q_YEAR, last_year) XXX LAST_4Q_YEAR broken
    wanted = (last_year, )
    for y in wanted:
        if not y:
            m = "[OB] %s Missing last_year report" % s_no
            ERROR(m)
            raise NoData(m)
        if not enough_value(finance[y], u'本期稅後淨利', 0.0, period=y,
                            s_no=s_no):
            return False
        # if not enough_value(finance[y], u'權責發生額', 0.0, period=y,
        #                     reverse=True, s_no=s_no):
        if not negative_accrual(finance[y], period=y, s_no=s_no):
            return False

    recent_years = meta[common.ANNUALS][:3]
    # recent_years.insert(0, common.LAST_4Q_YEAR) XXX LAST_4Q_YEAR broken
    for y in recent_years:
        report = finance[y]
        if not all((enough_value(report, u'營業毛利率', 0.3, period=y,
                                 s_no=s_no),
                    enough_value(report, u'負債比率', 0.3, period=y,
                                 reverse=True, s_no=s_no),
                    enough_value(report, u'每股盈餘(元)', 0.0, period=y,
                                 s_no=s_no))):
            return False

    def loose_eps_growth(y1, _y2, y3):
        var = common.field_var(u'每股盈餘(元)')
        f1 = finance[y1]
        f3 = finance[y3]
        return f1[var] - f3[var] > 0

    if not continous(recent_years, loose_eps_growth, window=3):
        return False

    daily_reports = stock_data[common.DAILY]
    latest_day = sorted(daily_reports.keys(), reverse=True)[0]
    latest_report = daily_reports[latest_day]
    if not enough_value(latest_report, u'殖利率',
                        0.05, period=latest_day, s_no=s_no):
        return False
    return True


def negative_accrual(finance_report, period=None, s_no=None):
    accrual = common.field_var(u'權責發生額')
    if accrual in finance_report:
        return finance_report[accrual] < 0
    m = '[negative_accrual] %s: Missing accrual data for %s' % (s_no, period)
    ERROR(m)
    raise NoData(m)


def enough_value(finance_report, field, threshold, period=None, reverse=False,
                 s_no=None):
    var_name = common.field_var(field)
    if var_name in finance_report:
        ret = finance_report[var_name] >= threshold
        if reverse:
            ret = not ret
        return ret
    m = '[enough_value] %s: Missing %s(%s) data for %s' % (s_no, field, var_name, period)
    ERROR(m)
    raise NoData(m)


def continous(l, func, window=2):
    if l:
        interval = window - 1
        return all([func(*(l[i] for i in xrange(x, x + window)))
                    for x in xrange(len(l) - interval)])
    return False


def main():
    result = {}
    catalog = common.load_catalog()
    for category, stocks in catalog.items():
        for s_no in stocks:
            stock_data = common.load_stock(s_no)
            for filter_name, filter_func in filters.items():
                data = result.setdefault(filter_name, {})
                data.setdefault(common.KEY_STOCKS, [])
                data.setdefault(common.KEY_MISSING_DATA, [])
                try:
                    if filter_func(s_no, stock_data):
                        data[common.KEY_STOCKS].append(s_no)
                except NoData as e:
                    data[common.KEY_MISSING_DATA].append(s_no)
                except Exception as e:
                    print s_no
                    raise

    for k, v in result.items():
        print k, len(v[common.KEY_STOCKS]), len(v[common.KEY_MISSING_DATA])
    common.save_filter_results(result)


filters = {
    config.KAZUYO_KATSUMA: kazuyo_katsuma,
    config.OLD_BROTHER: old_brother,
}

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        ERROR(traceback.format_exc(e))
        raise
