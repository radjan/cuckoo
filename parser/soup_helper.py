
def get_by_id(bs, idstr):
    return bs.find_all(id=idstr)[0]

def get_by_class(bs, classstr):
    return bs.find_all(class_=classstr)

def next_element_sibling(bs):
    n = bs.next_sibling
    while n != None and n.name == None:
        n = n.next_sibling
    return n

def list_elements(bslist):
    for c in bslist:
        if c.name != None:
            yield c

def expend_row(bstr):
    ret = []
    for c in list_elements(bstr.children):
        ret.append(c.string)
    return ret
