"""
:summary: Utility functions for the package

:license: Apache License, Version 2.0
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2015
"""
__docformat__ = "restructuredtext en"


def child2dict(el):
    """Turns an ElementTree.Element's children into a dict using the node names as dict keys and
    and the node text as dict values

    :Parameters:
        el : ElementTree.Element

    :return: a dictionary of element key(tag name)/value(node text) pairs
    :rtype: dict
    """
    return {c.tag: c.text for c in el}


def attr2dict(el):
    """Turns an elements attrib dict into... wait for it... a dict. Yea, it's silly to me too.
    But, according to the ElementTree docs, using the Element.attrib attribute directly
    is not recommended - don't look at me - I just work here.

    :Parameters:
        el : ElementTree.Element

    :return: a dictionary of element attrib key/value pairs
    :rtype: dict
    """
    return {k: v for k, v in el.items()}


def node2dict(el):
    """Combines both the attr2dict and child2dict functions
    """
    return dict(list(attr2dict(el).items()) + list(child2dict(el).items()))


def cull_kwargs(api_keys, kwargs):
    """Strips out the api_params from kwargs based on the list of api_keys
    !! modifies kwargs inline

    :Parameters:
        api_keys : list | set | tuple
            an iterable representing the keys of the key value pairs to pull out of kwargs
        kwargs : dict
            a dictionary of kwargs

    :return: a dictionary the API params
    :rtype: dict
    """
    return {k: kwargs.pop(k) for k in api_keys if k in kwargs}


def dict2argstring(argString):
    """Converts an argString dict into a string otherwise returns the string unchanged

    :Parameters:
        argString : str | dict
            argument string to pass to job - if str, will be passed as-is else if dict will be
            converted to compatible string

    :return: an argString
    :rtype: str
    """
    if isinstance(argString, dict):
        return ' '.join(['-' + str(k) + ' ' + str(v) for k, v in argString.items()])
    else:
        return argString


try:
    if isinstance('', basestring):
        pass
except NameError:
    # python 3
    StringType = type('')
else:
    # python 2
    StringType = basestring
