import common

f = common.load_filter_results()

for k, v in f.items():
    print k, v['stocks']
