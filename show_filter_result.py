#!/usr/bin/env python

import common


def _show(info):
    return '%s %s' % info

f = common.load_filter_results()

for k, v in f.items():
    print 'filter:', k
    results = {}
    for s_no in sorted(v['stocks']):
        s_info = common.load_stock(s_no)
        meta = s_info[common.META]
        s_name = meta[common.META_NAME]
        last_q = meta[common.QUARTERS][0]
        last_y = meta[common.LAST_YEAR]
        info = (s_no, s_name)
        fin_info = 'Y:%s Q:%s' % (last_y, last_q)
        if fin_info not in results:
            results[fin_info] = []
        results[fin_info].append(info)

    for fin_key in sorted(results.keys(), reverse=True):
        print '  %s' % fin_key
        print '    %s' % ', '.join([_show(info) for info in results[fin_key]])
