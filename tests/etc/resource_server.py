import os
import bottle

_cd = os.path.realpath(__file__)

@bottle.route('/<path:path>')
def dir(path):
    return bottle.static_file(path, root=_cd)

if __name__ == '__main__':
    bottle.run(host='localhost', port=8000, debug=True)
