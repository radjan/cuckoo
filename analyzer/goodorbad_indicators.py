# -*- encoding: utf8 -*-
# !/usr/bin/env python

import json
import common


def _gather_info(finance, year):
    fields = (u'稅前淨利', u'營業收入淨額', u'營業毛利', u'營業費用', u'營業利益')
    info = {}
    for f in fields:
        info[f] = finance[year][common.field_var(f)]

    # Hack it 
    q_fields = (u'來自營運之現金流量', u'投資活動之現金流量')
    all_q = (u'.1Q', u'.2Q', u'.3Q', u'.4Q')
    if all((year + q in finance for q in all_q)):
        for f in q_fields:
            info[f] = sum(finance[year+q][common.field_var(f)] for q in (u'.1Q', u'.2Q', u'.3Q', u'.4Q'))
    else:
        raise Exception('missing finance report!')

    return info


def main():
    f = common.load_filter_results()

    todo_stocks = set()
    for _k, v in f.items():
        for s_no in v['stocks']:
            todo_stocks.add(s_no)
    sorted_stocks = sorted(todo_stocks)

    results = {}
    for s_no in sorted_stocks:
        try:
            s_info = common.load_stock(s_no)

            meta = s_info[common.META]
            s_name = meta[common.META_NAME]
            annuals = meta[common.ANNUALS]
            last_2y = annuals[:2] if len(annuals) >= 2 else annuals

            finance = s_info[common.FINANCE]

            extracted_info = {'name': s_name}
            for y in last_2y:
                extracted_info[y] = _gather_info(finance, y)
            results[s_no] = extracted_info
        except:
            print s_no, s_name, y, last_2y
            raise

    # print json.dumps(results)
    _ugly_output(results)


def _ugly_output(results):
    # XXX it works
    for s_no in sorted(results.keys()):
        s = results[s_no]
        name, y1, y2  = sorted(s.keys(), reverse=True)

        sy1 = {k:v/1000000 for k, v in s[y1].items()}
        sy2 = {k:v/1000000 for k, v in s[y2].items()}

        print '<table>'
        _ugly_print(s_no, s[name], '')
        _ugly_print(u'年度', y1, y2)
        _ugly_print('1', '', '')
        for f in (u'來自營運之現金流量', u'投資活動之現金流量',):
            _ugly_print(f, sy1[f], sy2[f])
        _ugly_print(u'營業現金流量維持成長',
                    sy1[u'來自營運之現金流量'] - sy2[u'來自營運之現金流量'] > 0,
                    'N/A')
        _ugly_print(u'營業現金流量>投資現金流量',
                    sy1[u'來自營運之現金流量'] - sy1[u'投資活動之現金流量'] > 0,
                    sy2[u'來自營運之現金流量'] - sy2[u'投資活動之現金流量'] > 0)
        _ugly_print('2', '', '')
        for f in (u'營業收入淨額', u'營業毛利', u'營業費用', u'營業利益',
                  u'稅前淨利'):
            _ugly_print(f, sy1[f], sy2[f])

        _ugly_print('3', '', '')
        _ugly_print(u'營業淨利 / 營業收入淨額',
                    sy1[u'營業利益'] / sy1[u'營業收入淨額'],
                    sy2[u'營業利益'] / sy2[u'營業收入淨額'])
        _ugly_print(u'稅前淨利 / 營業收入淨額',
                    sy1[u'稅前淨利'] / sy1[u'營業收入淨額'],
                    sy2[u'稅前淨利'] / sy2[u'營業收入淨額'])

        print '</table>'
        print '\n'

def _ugly_print(name, v1, v2):
    print (u'<tr><td>{}</td><td>{}</td><td>{}</td></tr>').format(name, v1, v2)

if '__main__' == __name__:
    main()
