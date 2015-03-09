#!/usr/bin/env python

import common


def _show(info):
    return '%s %s(%s/%s)' % info


f = common.load_filter_results()

for k, v in f.items():
    print 'filter:', k
    results = []
    for s_no in sorted(v['stocks']):
        s_info = common.load_stock(s_no)
        meta = s_info[common.META]
        s_name = meta[common.META_NAME]
        last_q = meta[common.QUARTERS][0]
        last_y = meta[common.LAST_YEAR]
        info = (s_no, s_name, last_q, last_y)
        results.append(info)

    # Order by (newer LAST_YEAR, newer LAST_QUARTER, smaller STOCK NO)
    results = sorted(results,
                     key=lambda x: (x[3]+x[2], 100000 - int(x[0])),
                     reverse=True)
    print '    ', ', '.join([_show(info) for info in results])
