import os

try:
    import simplejson as json
except:
    print "simplejson not installed"
    import json

CURRENT_DATA_DATE = 'current_data_date'

ROOT = os.path.join(os.path.dirname(__file__), 'data')
FINANCE_REPORT = os.path.join(ROOT, 'stocks/%s.finance.json')
DAILY_REPORT = os.path.join(ROOT, 'stocks/%s.daily.json')
STOCK_CATALOG = os.path.join(ROOT, 'catalog.json')
STATE= os.path.join(ROOT, 'state.json')
CONFIG= os.path.join(ROOT, 'config.json')

DEFAULT_RAISE = 'DEFAULT_RAISE'

def report_error(msg):
    errors = load_error()
    errors.append(msg)
    save_error(errors)

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

def save_finance_report(stock_no, result_dict):
    _save_file(FINANCE_REPORT % stock_no, result_dict)

def load_finance_report(stock_no):
    return _load_file(FINANCE_REPORT, default={})

def save_daily_report(stock_no, data):
    _save_file(DAILY_REPORT % stock_no, data)

def load_daily_report(stock_no):
    return _load_file(DAILY_REPORT % stock_no, default={})

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

def load_error():
    return _load_file(ERROR, default={})

def save_error(data):
    _save_file(ERROR, data)

