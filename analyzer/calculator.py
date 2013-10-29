# -*- encoding: utf8 -*-

import common

def calculate(stock_no):
    '''
    calculate accrual for last year and last 4Q
    calculate roa for every finance report
    '''
    stock_data = _prepare(stock_no)
    finance = stock_data[common.FINANCE]

    key_net_income_after_tax = _field_name(u'本期稅後淨利')
    key_cash_flow_of_investment = _field_name(u'投資活動之現金流量')
    key_net_income_before_tax = _field_name(u'稅前淨利')
    key_total_assets = _field_name(u'資產總額')

    for y in (common.LAST_4Q_YEAR, stock_data[common.META][common.LAST_YEAR]):
        try:
            f = None
            if y:
                f = finance[y]
            if f:
                # accrual 權責發生額 = 稅後純利 - 投資活動之現金流量
                accrual = f[_field_name(u'本期稅後淨利')] - f[_field_name(u'投資活動之現金流量')]
                f[_field_name(u'權責發生額')] = accrual
        except Exception as e:
            msg = '%s: %s, accrual failed: %s %s' % (stock_no, y, type(e), e.message)
            common.report_error(msg)

    for period, f in finance.items():
        try:
            # ROA ＝ 稅前純利 / 資產總額
            roa = f[_field_name(u'稅前淨利')] / f[_field_name(u'資產總額')]
            f[_field_name(u'總資產報酬率')] = roa
        except Exception as e:
            msg = '%s: %s, ROA failed: %s %s' % (stock_no, period, type(e), e.message)
            common.report_error(msg)

    common.save_stock(stock_no, stock_data)

def _prepare(stock_no):
    '''
    calculate the missing annual cash_flow_of_investment from quarter report,
    calculate last 4Q data
    '''
    stock_data = common.load_stock(stock_no)
    finance = stock_data[common.FINANCE]

    annuals = sorted([k for k in finance.keys() if k.isdigit()],
                     key=_to_number,
                     reverse=True)
    quarters = sorted([k for k in finance.keys() if k[-1] == 'Q' and '~' not in k],
                      key=_to_number,
                      reverse=True)

    last_year = None
    for year in annuals:
        field_name = _field_name(u'投資活動之現金流量')
        if field_name in finance[year]:
            if last_year is None:
                last_year = year
            continue
        year_q = [year + q for q in ('.1Q', '.2Q', '.3Q', '.4Q')]
        # not calculate if there is data missing
        if all([yq in quarters and field_name in finance[yq] for yq in year_q]):
            cash_flow_of_investment = sum((finance[yq][field_name] for yq in year_q))
            finance[year][field_name] = cash_flow_of_investment
            if last_year is None:
                last_year = year

    last4Q = quarters[:4]
    last_4q_year = {}
    if last4Q and _continous_q(last4Q):
        fields = finance[last4Q[0]].keys()
        # not calculate if there is data missing
        if all((f in finance[q] for q in last4Q for f in fields)):
            for field in fields:
                last_4q_year[field] = sum((finance[q][field] for q in last4Q))
    finance[common.LAST_4Q_YEAR] = last_4q_year

    stock_data[common.META] = {
        common.LAST_YEAR: last_year,
        common.LAST_4Q: last4Q,
        }
    return stock_data

def _to_number(s):
    if s[-1] == 'Q':
        s = s[:-1]
    return float(s)

def _continous_q(quarters):
    # XXX it works
    for i in range(len(quarters) - 1):
        curr = quarters[i].split('.')
        next_ = quarters[i+1].split('.')
        if curr[0] == next_[0]:
            if (curr[1], next_[1]) not in (('4Q', '3Q'), ('3Q', '2Q'), ('2Q', '1Q'),):
                return False
        else:
            if not ((int(curr[0]) - int(next_[0])) == 1 and \
                    (curr[1], next_[1]) == ('1Q', '4Q')):
                return False
    return True

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
