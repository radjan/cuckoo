
def get_by_id(bs, idstr):
    return bs.find_all(id=idstr)[0]

def get_by_class(bs, classstr):
    return bs.find_all(class_=classstr)

def list_elements(bslist):
    for c in bslist:
        if c.name != None:
            yield c

def expend_row(bstr):
    ret = []
    for c in list_elements(bstr.children):
        ret.append(c.string)
    return ret
