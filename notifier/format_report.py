# -*- encoding: utf8 -*-
import traceback
import common
import config

class PresentData:
    """ manipulate data """
    def __init__(self, title, data=None):
        self.title = title
        if data is None:
            self.data = []

    def add(self, title, value):
        if title not in [d[0] for d in self.data if isinstance(d, tuple)]:
            self.data.append((title, value))

    def add_section(self, obj):
        if isinstance(obj, str) or isinstance(obj, unicode):
            obj = PresentData(obj)
        for item in self.data:
            if isinstance(item, PresentData) and item.title == obj.title:
                return item
        self.data.append(obj)
        return obj

    def output(self):
        def _output():
            out = []
            for item in self.data:
                if isinstance(item, PresentData):
                    out.append(item.output())
                else:
                    out.append(item)
            return out
        return self.title, _output()

def _get(d, k):
    return d.get(k, 'N/A')

def _pass(yn, title=u'符合'):
    return (title, 'Y' if yn else 'N')

def _format_float(v):
    if isinstance(v, float):
        return '{:,.4f}'.format(v)
    return v

def format_basic(stock_data, data=None):
    """ format basic info """
    meta = stock_data[common.META]
    daily = stock_data[common.DAILY]

    latest_day = common.get_latest_day(stock_data)
    day = daily[latest_day]

    data = data if data is not None else PresentData(u'股票')
    data.add(u'號碼', _get(meta, common.META_STOCK_NO))
    data.add(u'名稱', _get(meta, common.META_NAME))
    data.add(u'資料日期', latest_day)
    for f in (u'股價', u'成交量'):
        var = common.field_var(f)
        data.add(f, _format_float(_get(day, var)))
    return data

def format_by_indicator(indicators, stock_data, share_data=None, data=None, verbose=False):
    """" format by indicator """
    data = data if data is not None else PresentData(u'股票')
    for name, yn in indicators.items():
        MAPPINGS[name](data, yn, stock_data, share_data, verbose=verbose)
    return data

def _add_finance_field(section, finance, field_name):
    section.add(field_name, _format_float(_get(finance,
                                               common.field_var(field_name))))

def kazuyo_katsuma(data, yn, stock_data, share_data, verbose=False):
    meta = stock_data[common.META]
    daily = stock_data[common.DAILY]
    finance = stock_data[common.FINANCE]

    section = data.add_section(u'勝間和代')
    section.add(*_pass(yn))

    for y in (common.LAST_4Q_YEAR, meta[common.LAST_YEAR]):
        y_f = finance[y]
        y_sec = section
        if verbose:
            y_sec = section.add_section(y)
        _add_finance_field(y_sec, y_f, u'權責發生額')
        if verbose:
            for f in (u'本期稅後淨利', u'來自營運之現金流量'):
                _add_finance_field(y_sec, y_f, f)

    for q in meta[common.QUARTERS][:5]:
        q_f = finance[q]
        if verbose:
            roa_sec = section.add_section(q)
            var_name = u'總資產報酬率'
        else:
            roa_sec = section.add_section(u'總資產報酬率')
            var_name = q
        roa_sec.add(var_name, _get(q_f, common.field_var(u'總資產報酬率')))
        if verbose:
            for f in (u'稅前純利', u'資產總額'):
                _add_finance_field(roa_sec, q_f, f)

def old_brother(data, yn, stock_data, share_data, verbose=False):
    meta = stock_data[common.META]
    daily = stock_data[common.DAILY]
    finance = stock_data[common.FINANCE]

    section = data.add_section(u'老哥綜合')
    section.add(*_pass(yn))

    for y in (common.LAST_4Q_YEAR, meta[common.LAST_YEAR]):
        y_f = finance[y]
        y_sec = section
        if verbose:
            y_sec = section.add_section(y)
        _add_finance_field(y_sec, y_f, u'權責發生額')
        if verbose:
            for f in (u'本期稅後淨利', u'來自營運之現金流量'):
                _add_finance_field(y_sec, y_f, f)

    latest_day = common.get_latest_day(stock_data)
    _add_finance_field(section, daily[latest_day], u'殖利率')

    recent_years = meta[common.ANNUALS][:3]
    recent_years.insert(0, common.LAST_4Q_YEAR)
    for y in recent_years:
        y_f = finance[y]
        y_sec = section.add_section(y)
        for f in (u'營業毛利率', u'負債比率', u'每股盈餘(元)'):
            _add_finance_field(y_sec, y_f, f)

def _per(data, yn, stock_data, share_data, title, verbose=False):
    meta = stock_data[common.META]
    daily = stock_data[common.DAILY]

    section = data.add_section(u'本益比')
    section.add(*_pass(yn, title=title))
    if verbose:
        day = common.get_latest_day(stock_data)
        var_per = common.field_var(u'本益比')
        c_key = meta[common.META_CATEGORY_KEY]

        per = daily[day][var_per]
        avg_per = share_data['categories'][c_key][day][var_per]
        section.add(u'本益比', _format_float(per))
        section.add(u'分類平均', _format_float(avg_per))
        section.add(u'比例', _format_float(per / avg_per))
        section.add(u'分類', c_key)

def per_low(data, yn, stock_data, share_data, verbose=False):
    _per(data, yn, stock_data, share_data, u'本益比低', verbose=verbose)

def per_high(data, yn, stock_data, share_data, verbose=False):
    _per(data, yn, stock_data, share_data, u'本益比高', verbose=verbose)

def _amount(data, yn, stock_data, share_data, title, verbose=False):
    meta = stock_data[common.META]
    daily = stock_data[common.DAILY]

    section = data.add_section(u'成交量')
    section.add(*_pass(yn, title=title))

    days = meta[common.META_DAYS]
    latest_day = days[0]
    exam_days = days[1:6]

    var_amount = common.field_var(u'成交量')

    avg_amount = sum((daily[d][var_amount] for d in exam_days))/len(exam_days)
    latest_amount = daily[latest_day][var_amount]

    section.add(latest_day, _format_float(latest_amount))
    section.add(u'前五日平均', _format_float(avg_amount))
    section.add(u'比例', _format_float(latest_amount / avg_amount))
    if verbose:
        for d in exam_days:
            section.add(d, _format_float(daily[d][var_amount]))

def amount_low(data, yn, stock_data, share_data, verbose=False):
    _amount(data, yn, stock_data, share_data, u'成交量趨緩', verbose=verbose)

def amount_high(data, yn, stock_data, share_data, verbose=False):
    _amount(data, yn, stock_data, share_data, u'成交量大增', verbose=verbose)

def format(stock_data, indicators, categories):
    data = format_basic(stock_data)
    format_by_indicator(indicators, stock_data, share_data={'categories': categories}, data=data)
    return data

MAPPINGS = {
    config.KAZUYO_KATSUMA: kazuyo_katsuma,
    config.OLD_BROTHER: old_brother,
    config.PER_LOW: per_low,
    config.PER_HIGH: per_high,
    config.AMOUNT_LOW: amount_low,
    config.AMOUNT_HIGH: amount_high,
    }

if __name__ == '__main__':
    """ for test """
    import sys
    no = sys.argv[1]
    sd = common.load_stock(no)
    data = format_basic(sd)
    format_by_indicator({config.KAZUYO_KATSUMA: True, config.OLD_BROTHER: True, config.AMOUNT_LOW: True}, sd, data=data)
    import pprint
    pprint.pprint(data.output())
