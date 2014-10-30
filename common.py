# -*- encoding: utf8 -*-
import os
import sys
import atexit

try:
    import simplejson as json
except:
    print "simplejson not installed"
    import json

# Save/Load control flags
LOCAL = '_local_'
FIREBASE = '_firebase_'
READ_FROM = FIREBASE
SAVE_TO = (LOCAL,)

KEY_STOCKS = 'stocks'
KEY_MISSING_DATA = 'missing_data'

LAST_4Q_YEAR = 'last_4q_year'

META = 'meta'
LAST_YEAR = 'last_year'
LAST_4Q = 'last_4q'
ANNUALS = 'annuals'
QUARTERS = 'quarters'
META_STOCK_NO = 'stock_no'
META_NAME = 'name'
META_COMPANY_TYPE = 'company_type'
META_COMPANY_CATEGORY = 'company_category'
META_CATEGORY_KEY = 'category_key'
META_DAYS = 'days'

TOTAL = 'total'

AVG_COUNT = '__count'
AVG_SUM = '__sum'

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
        u'來自營運之現金流量': ('cash_flow_operating', MILLION),
        u'營業毛利率': ('gross_margin_percentage', PERCENTAGE),
        u'負債比率': ('debt_to_total_assets_ratio', PERCENTAGE),
        u'現金股利': ('dividend_cash', ONE),
        u'股票股利': ('dividend_stock', ONE),
        u'股利': ('dividend', ONE),

        u'總資產報酬率': ('roa', PERCENTAGE),
        u'權責發生額': ('accrual', MILLION),
        u'本益比': ('per', PERCENTAGE),
        u'4Q本益比': ('per_4q', PERCENTAGE),
        u'股價': ('price', ONE),
        u'成交量': ('amount', ONE),
        u'殖利率': ('yield_rate', PERCENTAGE),
}

FIELD_NAMES = dict(((v[0], k) for k, v in FIELDS.items()))

def field_var(unicode_str):
    return FIELDS.get(unicode_str, (None,))[0]

def field_name(var):
    return FIELD_NAMES.get(var, None)

def field_unit(var_or_name):
    name = field_name(var_or_name)
    if name is None:
        name = var_or_name
    return FIELDS.get(name, (None, None))[1]

def get_latest_day(stock_data):
    if META_DAYS in stock_data[META]:
        return stock_data[META][META_DAYS][0]
    return sorted(stock_data[DAILY].keys(), reverse=True)[0]

import firebase
FIREBASE_URL = 'https://resplendent-fire-6708.firebaseio.com'
fb = firebase.firebase.FirebaseApplication(FIREBASE_URL)

CURRENT_DATA_DATE = 'current_data_date'

FIREBASE_ROOT = '/cuckoo'
FIREBASE_ESCAPE = {
    '/': '%%slash%%',
    '.': '%%dot%%',
    }
def escape(s):
    for k, v in FIREBASE_ESCAPE.items():
        s = s.replace(k, v)
    return s

def unescape(s):
    for k, v in FIREBASE_ESCAPE.items():
        s = s.replace(v, k)
    return s

def escape_dict(d):
    if type(d) is not dict:
        return d
    kv = []
    for k, v in d.items():
        e_k = escape(k)
        if type(v) is dict:
            v = escape_dict(v)
        if k != e_k:
            kv.append((k, e_k, v))
    for k, e_k, v in kv:
        d[e_k] = v
        del d[k]
    return d

def unescape_dict(d):
    kv = []
    for e_k, v in d.items():
        k = unescape(e_k)
        if type(v) is dict:
            v = unescape_dict(v)
        if k != e_k:
            kv.append((k, e_k, v))
    for k, e_k, v in kv:
        d[k] = v
        del d[e_k]
    return d

ROOT = os.path.join(os.path.dirname(__file__), 'data')
STOCK_REPORT = os.path.join(ROOT, 'stocks/%s.json')
STOCK_CATALOG = os.path.join(ROOT, 'catalog.json')
AVERAGE_CATEGORY = os.path.join(ROOT, 'category_avg.json')
STATE = os.path.join(ROOT, 'state.json')
CONFIG = os.path.join(ROOT, 'config.json')
ERRORS = os.path.join(ROOT, 'erorrs.json')
FILTER_RESULTS = os.path.join(ROOT, 'filter_results.json')
INDICATOR_RESULTS = os.path.join(ROOT, 'indicator_results.json')

if not os.path.exists(os.path.join(ROOT, 'stocks')):
    os.mkdir(os.path.join(ROOT, 'stocks'))

DEFAULT_RAISE = 'DEFAULT_RAISE'

FINANCE = 'finance'
DAILY = 'daily'

error_tmp = None

def report_error(msg):
    print >> sys.stderr, msg
    global error_tmp
    if error_tmp is None:
        error_tmp = load_errors()
        atexit.register(save_errors, data=error_tmp)
    errors = error_tmp
    errors.append(msg)

def _save_file(path, data):
    if LOCAL in SAVE_TO:
        with open(path, 'wr') as f:
            json.dump(data, f)
    if FIREBASE in SAVE_TO:
        fb_path = path[len(ROOT)+1:-len('.json')]
        fb.put(FIREBASE_ROOT, fb_path, escape_dict(data))

def _load_file(path, default=DEFAULT_RAISE):
    if READ_FROM == FIREBASE:
        fb_path = path[len(ROOT)+1:-len('.json')]
        result = fb.get(os.path.join(FIREBASE_ROOT, fb_path), None)
        if result is None:
            if default == DEFAULT_RAISE:
                raise Exception('Data %s not fuound' % path)
            result = default
        return result
    elif READ_FROM == LOCAL:
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except IOError:
            if default == DEFAULT_RAISE:
                raise
            return default
    else:
        raise NotImplemented('Unknown data source: %s' % READ_FROM)

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
    return _load_file(STOCK_REPORT % stock_no,
                      default={DAILY:{'_': '_'},
                               FINANCE:{'_': '_'},
                               META: {'_': '_'}})

def save_stock(stock_no, data):
    try:
        assert FINANCE in data
        assert DAILY in data
        _save_file(STOCK_REPORT % stock_no, data)
    except:
        print >> sys.stderr, stock_no, data
        raise

def load_catalog():
    return _load_file(STOCK_CATALOG, default={})

def save_catalog(data):
    _save_file(STOCK_CATALOG, data)

def load_categories():
    return _load_file(AVERAGE_CATEGORY, default={})

def save_categories(data):
    _save_file(AVERAGE_CATEGORY, data)

def load_state():
    return _load_file(STATE, default={})

def save_state(data):
    _save_file(STATE, data)

def load_filter_results():
    return _load_file(FILTER_RESULTS, default={})

def save_filter_results(data):
    _save_file(FILTER_RESULTS, data)

def load_indicator_results():
    return _load_file(INDICATOR_RESULTS, default={})

def save_indicator_results(data):
    _save_file(INDICATOR_RESULTS, data)

def load_config():
    return _load_file(CONFIG, default={})

def save_config(data):
    _save_file(CONFIG, data)

def load_errors():
    return _load_file(ERRORS, default=[])

def save_errors(data):
    _save_file(ERRORS, data)

