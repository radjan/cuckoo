# -*- encoding: utf8 -*-
import sys
import traceback

from bs4 import BeautifulSoup, Tag

import common
import config
from notifier import format_report

_css = """
<style>
table { border: 1px solid black;}
td { border: 1px solid black;}
</style>
"""

def main(fn=None, out_format='text'):
    output(fn, out_format=out_format)
    # TODO format html

def output(fn, out_format):
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


    if out_format == 'text':
        format_text(results, fn)
    else:
        format_html(results, fn)

def format_text(results, fn):
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

    final = u'\n'.join([u'%s'] * len(results))
    final_str = final % texts
    _out_file(fn, final_str)

def format_html(results, fn):
    def _rows_n_cols(dataobj):
        rows = 1
        colspan = sub_rows = sub_colspan = 0
        for d in dataobj.data:
            if isinstance(d, format_report.PresentData):
                sub_rows, sub_colspan = _rows_n_cols(d)
                colspan += sub_colspan
            else:
                colspan += 1
        rows += sub_rows
        dataobj.rows = rows
        dataobj.colspan = colspan
        return rows, colspan

    def _append_tag(bs, parent, name):
        tag = bs.new_tag(name)
        parent.append(tag)
        return tag

    bs = BeautifulSoup("<html><head>%s</head><body></body></html>" % _css, 'lxml')
    table = _append_tag(bs, bs.body, 'table')

    def _l(dataobj, trs, curr_row):
        for d in dataobj.data:
            if isinstance(d, format_report.PresentData):
                title_td = _append_tag(bs, trs[curr_row], 'td')
                if d.colspan > 0:
                    title_td['colspan'] = d.colspan
                title_td.append(d.title)
                _l(d, trs, curr_row+1)
            else:
                title_td = _append_tag(bs, trs[curr_row], 'td')
                title_td.append(d[0])
                rowspan = len(trs) - curr_row - 1
                if rowspan > 1:
                    title_td['rowspan'] = rowspan
                value_td = _append_tag(bs, trs[-1], 'td')
                value_td.string = unicode(d[1])

    for r in results:
        rows, colspan = _rows_n_cols(r)
        trs = []
        for _row in range(rows+1):
            tr = _append_tag(bs, table, 'tr')
            trs.append(tr)
        _l(r, trs, 0)

    _output_file(fn, bs.prettify())

def _output_file(fn, s):
    import codecs
    f = codecs.open(fn, 'w', 'utf-8')
    f.write(s)

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
        format_ = sys.argv[2] if len(sys.argv) > 2 else 'text'
        main(fn, format_)
    except Exception as e:
        common.report_error(traceback.format_exc(e))
        raise

