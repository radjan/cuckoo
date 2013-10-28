# -*- encoding: utf8 -*-
import os

try:
    import simplejson as json
except:
    print "simplejson not installed"
    import json

META = 'meta'
LAST_YEAR = 'last_year'
LAST_4Q = 'last_4q'
LAST_4Q_YEAR = 'last_4q_year'

MILLION = 1000000
ONE = 1
PERCENTAGE = 0.01

FIELDS = {
        # column_name: (variable_name, unit)
        u'資產總額': ('total_assets', MILLION),
        u'負債總額': ('total_debts', MILLION),
        u'稅前淨利': ('net_income_before_tax', MILLION),
        u'每股盈餘(元)': ('eps', ONE),
        u'稅後淨利': ('net_income_after_tax', MILLION),
        u'經常利益': ('net_income_afetr_tax', MILLION),
        u'本期稅後淨利': ('net_income_after_tax_this', MILLION),
        u'投資活動之現金流量': ('cash_flow_of_investment', MILLION),
        u'營業毛利率': ('gross_margin_percentage', PERCENTAGE),
        u'負債比率': ('debt_to_total_assets_ratio', PERCENTAGE),

        u'總資產報酬率': ('roa', PERCENTAGE),
        u'權責發生額': ('accrual', MILLION),
}

CURRENT_DATA_DATE = 'current_data_date'

ROOT = os.path.join(os.path.dirname(__file__), 'data')
STOCK_REPORT = os.path.join(ROOT, 'stocks/%s.json')
STOCK_CATALOG = os.path.join(ROOT, 'catalog.json')
STATE = os.path.join(ROOT, 'state.json')
CONFIG = os.path.join(ROOT, 'config.json')
ERRORS = os.path.join(ROOT, 'erorrsjson')

DEFAULT_RAISE = 'DEFAULT_RAISE'

FINANCE = 'finance'
DAILY = 'daily'

error_tmp = None

def report_error(msg):
    global error_tmp
    if error_tmp is None:
        error_tmp = load_errors()
    errors = error_tmp
    errors.append(msg)
    save_errors(errors)

def _save_file(path, data):
    with open(path, 'wr') as f:
        json.dump(data, f)

def _load_file(path, default=DEFAULT_RAISE):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except IOError:
        if default == DEFAULT_RAISE:
            raise
        return default

def save_finance_report(stock_no, data):
    path = STOCK_REPORT % stock_no
    d = _load_file(path, default={})
    d[FINANCE] = data
    _save_file(path, d)

def load_finance_report(stock_no):
    return _load_file(STOCK_REPORT % stock_no, default={}).get(FINANCE, {})

def save_daily_report(stock_no, data):
    path = STOCK_REPORT % stock_no
    d = _load_file(path, default={})
    d[DAILY] = data
    _save_file(path, d)

def load_daily_report(stock_no):
    return _load_file(STOCK_REPORT % stock_no, default={}).get(DAILY, {})

def load_stock(stock_no):
    return _load_file(STOCK_REPORT % stock_no)

def save_stock(stock_no, data):
    assert FINANCE in data
    assert DAILY in data
    _save_file(STOCK_REPORT % stock_no, data)

def load_catalog():
    return _load_file(STOCK_CATALOG, default={})

def save_catalog(data):
    _save_file(STOCK_CATALOG, data)

def load_state():
    return _load_file(STATE, default={})

def save_state(data):
    _save_file(STATE, data)

def load_config():
    return _load_file(CONFIG, default={})

def save_config(data):
    _save_file(CONFIG, data)

def load_errors():
    return _load_file(ERRORS, default=[])

def save_errors(data):
    _save_file(ERRORS, data)

