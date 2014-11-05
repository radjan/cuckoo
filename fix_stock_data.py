import common


def fix_it(stock_no):
    data = common.load_stock(stock_no)
    for k, f in data[common.FINANCE].items():
        if 'cash_flow_operatinh' in f:
            f['cash_flow_operating'] = f.pop('cash_flow_operatinh')
    common.save_stock(stock_no, data)


def main():
    catalog = common.load_catalog()
    for category, stocks in catalog.items():
        for stock_no in stocks:
            fix_it(stock_no)

if __name__ == '__main__':
    main()
