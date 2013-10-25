# -*- encoding: utf8 -*-

import common

def calculate(stock_no):
    stock_data = _prepare(stock_no)

    # XXX boom!
    lastest_finance = finance[annuals[0]]
    import pprint
    pprint.pprint(lastest_finance)
    # accrual 權責發生額
    accrual = lastest_finance['net_income_before_tax'] - lastest_finance['cash_flow_of_investment']
    print stock_no, accrual

    daily = common.load_daily_report(stock_no)

def _prepare(stock_no):
    '''
    calculate the missing annual cash_flow_of_investment from quarter report,
    calculate last 4Q data
    '''
    stock_data = common.load_stock(stock_no)
    finance = stock_data[common.FINANCE]

    def _to_number(s):
        if s[-1] == 'Q':
            s = s[:-1]
        return float(s)

    annuals = sorted([k for k in finance.keys() if k.isdigit()],
                     key=_to_number,
                     reverse=True)
    quarters = sorted([k for k in finance.keys() if k[-1] == 'Q'],
                      key=_to_number,
                      reverse=True)
    print stock_no, annuals, quarters
    for year in annuals:
        field_name = common.FIELDS[u'投資活動之現金流量'][0]
        if field_name in finance[year]:
            continue
        year_q = [year + q for q in ('.1Q', '.2Q', '.3Q', '.4Q')]
        if all([yq in quarters for yq in year_q]):
            cash_flow_of_investment = sum((finance[yq][field_name] for yq in year_q))
            finance[year][field_name] = cash_flow_of_investment

    last4Q = quarters[:4]
    last_year = {}
    for field in finance[last4Q[0]]:
        last_year[field] = sum((finance[q][field] for q in last4Q))
    finance[common.LAST_YEAR] = last_year

    import pprint
    pprint.pprint(finance[common.LAST_YEAR])

    return stock_data

def main():
    catalog = common.load_catalog()
    for category, stocks in catalog.items():
        for stock_no in stocks:
            calculate(stock_no)
            break

if __name__ == '__main__':
    main()
