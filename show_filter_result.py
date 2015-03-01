#!/usr/bin/env python

import common

f = common.load_filter_results()

for k, v in f.items():
    print 'filters:', k
    display = []
    for s_no in v['stocks']:
        s_info = common.load_stock(s_no)
        info = (s_no, s_info[common.META][common.META_NAME])
        display.append(info)

    print '    ', ', '.join(['%s %s' % (info[0], info[1]) for info in display])
