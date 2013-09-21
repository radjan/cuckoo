import os

try:
    import simplejson as json
except:
    import json

ROOT = os.path.join(os.path.dirname(__file__), 'data')
FINANCE_REPORT = os.path.join(ROOT, 'finance.%s.json')

def save_finance_report(stock_no, result_dict):
    with open(FINANCE_REPORT % stock_no, 'wr') as f:
        json.dump(result_dict, f)

def load_finance_report(stock_no):
    with open(FINANCE_REPORT % stock_no, 'r') as f:
        return json.load(f)
