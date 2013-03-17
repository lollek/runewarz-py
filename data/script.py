#! /usr/bin/env python2.7

def load_mapfile(filename, debugmode = False):
    
    if debugmode:
        print('load_mapfile: attempting to load mapfile: %s' % filename)
    try:
        with open(filename) as mapfile:
            lines = mapfile.readlines()
        X, Y = lines[0].split('x')
        del lines[0]
        if debugmode:
            print('load_mapfile: successfully loaded %s' % filename)
        return('OK', ((int(X), int(Y)), lines))
    except:
        print('load_mapfile: failed to load %s' % filename)
        return('ERR', 0)

