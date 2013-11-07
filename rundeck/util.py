def child2dict(el):
    return {c.tag: c.text for c in el}


def attr2dict(el):
    # according to the ElementTree docs... using the Element.attrib attribute directly is not
    #    recommended - don't look at me
    return {k: v for k, v in el.items()}


