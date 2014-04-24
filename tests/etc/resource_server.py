"""
:summary: A very simple HTTP server to serve a request from Rundeck server for a resource file

:license: Creative Commons Attribution-ShareAlike 3.0 Unported
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2013

:requires: bottle
"""
__docformat__ = "restructuredtext en"

import os
import bottle

_cd = os.path.realpath(__file__)

@bottle.route('/<path:path>')
def dir(path):
    return bottle.static_file(path, root=_cd)

if __name__ == '__main__':
    bottle.run(host='localhost', port=8000, debug=True)
