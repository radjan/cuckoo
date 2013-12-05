# -*- encoding: utf8 -*-
import sys
import traceback
import common
import config
from notifier import format_report

def main(fn):
    format_text(fn)
    # TODO format html

def format_text(fn):
    filter_results = common.load_filter_results()
    indicators = common.load_indicator_results()
    categories = common.load_categories()

    stocks = _gather_stocks(filter_results)
    results = []
    for s in stocks:
        sd = common.load_stock(s)
        ind = indicators[s]
        for n, v in filter_results.items():
            ind[n] = s in v['stocks']
        results.append(format_report.format(sd, ind, categories))

    final = u'\n'.join([u'%s'] * len(results))

    def _to_text(title, values, idents=0):
        new_idents = idents + 4
        if isinstance(values, list):
            indent_spaces = u' '*(idents+3)
            result_str = u'[\n'
            for item in values:
                result_str += (indent_spaces + _to_text(*item, idents=new_idents))
            result_str += (indent_spaces + u']')
        else:
            result_str = values
        return u'%s: %s\n' % (title, result_str)

    texts = tuple((_to_text(*d.output()) for d in results))

    import codecs
    f = codecs.open(fn, 'w', 'utf-8')
    final_str = final % texts
    f.write(final_str)

def _gather_stocks(filter_results):
    s = []
    for n, f in filter_results.items():
        s.extend(f[common.KEY_STOCKS])
    # filtered stock first
    # for n, c in config.preferences.items():
    #     s.extend(c['stocks'])
    return set(s)

if __name__ == '__main__':
    try:
        fn = sys.argv[1]
        main(fn)
    except Exception as e:
        common.report_error(traceback.format_exc(e))
        raise
