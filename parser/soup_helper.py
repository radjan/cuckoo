
def _get_by_id(bs, idstr):
    return bs.find_all(id=idstr)[0]

def _list_elements(bslist):
    for c in bslist:
        if c.name != None:
            yield c

def _expend_row(bstr):
    ret = []
    for c in _list_elements(bstr.children):
        ret.append(c.string)
    return ret
