#! /usr/bin/env python2.7

# Rune Warz
# Created 2013-03-11 by Olle Kvarnstrom
# Images by Sofie Aid

import os
from random import randint, shuffle
from sys import exit
from time import sleep

import pygame
from pygame.locals import *

VERSION = 'v0.1.3'

def root_init():

    """ Window Width, Height and Tilesize """
    global ROOT_W, ROOT_H, ROOT_T
    ROOT_W, ROOT_H, ROOT_T = 800, 600, 15

    """ Root window, Tile image, Blit list """
    global ROOT, TILE, LAUNDRY
    pygame.init()
    pygame.display.set_caption('Rune Warz '+VERSION)
    ROOT = pygame.display.set_mode((ROOT_W, ROOT_H))
    TILE = pygame.image.load('data/tiles.jpeg').convert()
    LAUNDRY = []
    

def make_map(filename, debugmode = False):

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

    """ Game Map, Player List """
    global MAP, PLAYERS
    global X, Y
    global OFFSET_X, OFFSET_Y
    
    """ Load mapfile """
    fromfile = load_mapfile(str(filename), debugmode)
    if fromfile[0] == 'ERR':
        print('make_make: Error received. Exiting')
        return('ERR', 0)
    else:
        fromfile = fromfile[1]
        X, Y = fromfile[0]
        lines = fromfile[1]

    """ Make loaded mapfile into map
    # = ground, @ = player
    """
    PLAYERS = []
    try:
        MAP = [[ Cap() for y in range( Y )] for x in range( X )]
        x, y = 0, 0
        for lno in range( Y ):
            for tile in range( X ):
                if tile <  len(lines[lno]):
                    if debugmode:
                        print('MAP[%s][%s] == %s' % (x, y, lines[lno][tile]))
                    if lines[lno][tile] == '#':
                        MAP[x][y].active = True
                    elif lines[lno][tile] == '@':
                        MAP[x][y].active = True
                        new_player = Player(len(PLAYERS)+1, MAP[x][y].color)
                        new_player.caps.append((x, y))
                        PLAYERS.append(new_player)
                    x += 1
            x, y = 0, y + 1
            
        if debugmode:
            print('make_map: made map OK')
    except:
        print('make_map: failed to make a map from file: %s' % filename)
        return('ERR', 0)

    # Adjust RES config after X/Y in map:
    OFFSET_X = (ROOT_W-(X*ROOT_T))/2
    OFFSET_Y = (ROOT_H-(Y*ROOT_T))/2

    ROOT.fill((0, 0, 0))
    # Draw all tiles:
    for x in range( X ):
        for y in range( Y ):
            MAP[x][y].draw(x, y)

    # And redraw player's to add a nice rune:
    for player in PLAYERS:
        player.draw_caps()

    return 'OK'

class Cap:

    def __init__ ( self ):

        self.active = False
        self.color = randint( 0, 7 )

    def draw(self, x, y, sym=None, force=False):
        
        if self.active or force:
            x = OFFSET_X + x*ROOT_T
            y = OFFSET_Y + y*ROOT_T
            if sym is None:
                ROOT.blit(TILE, (x, y), (self.color*15, 0, 15, 15))
            else:
                ROOT.blit(TILE, (x, y), (self.color*15, sym*15, 15, 15))
            LAUNDRY.append((x, y, 15, 15))
            
class Player:

    def __init__( self, sym, color):
        self.sym = sym
        self.color = color
        self.caps = []

        self.action = None
        if self.sym == 1:
            self.player = True
            self.MPOS = (0,0)
            self.oList = []
        else: self.player = False

    def capture( self ):
        self.color = self.hColor
        for cap in self.oList:
            self.caps.append(cap)
        self.draw_caps()
        self.oList = []
        UpdateScore()

    def fancyCapture( self ):
        self.color = self.hColor
        while self.oList:
            shuffle(self.oList)
            cx, cy = self.oList[0]
            self.caps.append(( cx, cy ))
            MAP[cx][cy].color = self.color
            MAP[cx][cy].draw( cx, cy, self.sym, True )
            MAP[cx][cy].active = False
            del self.oList[0]
            pygame.display.update(LAUNDRY)
            LAUNDRY[:] = []
            UpdateScore()
            sleep(0.1)
            
    def draw_caps( self ):
        for cx, cy in self.caps:
            MAP[cx][cy].color = self.color
            MAP[cx][cy].draw( cx, cy, self.sym, True )
            MAP[cx][cy].active = False
        pygame.display.update(LAUNDRY)
        LAUNDRY[:] = []

    def take_turn( self, read_only = False ):
        ai_debug = False

        optColor = [ r for r in range( 8 ) ]
        best = (None, [])
        
        for color in optColor:
            self.hColor = color
            checkColor( self, False )
            if len(self.oList) > len(best[1]):
                best = ( color, self.oList)

            elif ai_debug: print 'Disregard %s (%s)' % ( color, len(self.oList))

        if len(best[1]) > 0:
            if ai_debug: print 'Best choice is %s (%s)' % (best[0], len(best[1]))
            self.hColor = best[0]
            self.oList = best[1]
            if not read_only: sleep(0.5)
            if not read_only: self.capture()
            self.action = 'CAPT'
            return 'OK'

        elif ai_debug: print 'No good option :('
        else:
            self.action = 'NONE'
            return 'DONE'

def UpdateScore():
#    MaxScore = RES['map_tw']*RES['map_th']

    y = OFFSET_Y + Y*ROOT_T + 20
    
    for player in PLAYERS:
        x = OFFSET_X
        score = len(player.caps)
        ROOT.blit(TILE, (x, y), (player.color*15, player.sym*15, 15, 15))
        LAUNDRY.append((x, y, 15, 15))
        x += 15
        while score > 0:
            ROOT.blit(TILE, (x, y, 1, 15), (player.color*15, player.sym*15, 1, 15))
            LAUNDRY.append((x, y, 1, 15))
            score -= 1
            x += 1
        LAUNDRY.append((x, y, score, 15))
        y += 20
    pygame.display.update(LAUNDRY)
    LAUNDRY[:] = []


def isLegalCap( cx, cy ):
    if 0 <= cx < X:
        if 0 <= cy < Y:
            if MAP[cx][cy].active:
                return True
    return False

def getCloseCaps( cx, cy, color, lst):
    tmp_list = [(cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)]
    for x, y in tmp_list:
        if isLegalCap( x, y ):
            if MAP[x][y].color == color:
                if (x, y) not in lst:
                    lst.append((x, y))

def isCloseToPlayer( cx, cy, player ):
    tmp_list = [(cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)]
    for cap in player.caps:
        if cap in tmp_list:
            return True
    return False

def checkColor( player, draw ):
    for pl in PLAYERS:
        if pl.color == player.hColor:
            player.oList = []
            return

    FancyList = []
    for cx, cy in player.caps:
        getCloseCaps( cx, cy, player.hColor, FancyList )
        if FancyList:
            for cx, cy in FancyList:
                if draw: MAP[cx][cy].draw( cx, cy, player.sym )
                getCloseCaps( cx, cy, player.hColor, FancyList )
            if draw:
                pygame.display.update(LAUNDRY)
                LAUNDRY[:] = []
            player.oList = FancyList
        else:
            player.oList = []

def event( player ):
    event = pygame.event.wait()

    if event.type == pygame.MOUSEMOTION:
        mx, my = pygame.mouse.get_pos()
        pos = ((mx-OFFSET_X)/ROOT_T, (my-OFFSET_Y)/ROOT_T)
        if pos != player.MPOS:
            player.MPOS = pos
            for cx, cy in player.oList: MAP[cx][cy].draw( cx, cy )
            if isLegalCap( pos[0], pos[1] ) and isCloseToPlayer( pos[0], pos[1], player ):
                player.hColor = MAP[pos[0]][pos[1]].color
                checkColor( player, True )

            else:
                if player.oList:
                    player.oList = []
                    pygame.display.update()
                    LAUNDRY[:] = []

    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE: return 'DONE'
        elif event.key == pygame.K_q: return 'break'

    elif event.type == pygame.MOUSEBUTTONDOWN:
        if player.oList:
            player.capture()
            return 'DONE'

def run_game(XIT):
    
    while not XIT:
        DONE = False
        for faction in PLAYERS:
            if faction.player:
                if faction.take_turn(True) != 'DONE':
                    while not DONE:
                        act = event( faction )
                        if act == 'DONE':
                            DONE = True
                        elif act == 'break':
                            #exit()
                            return
                            #DONE = True
                            #XIT = True
            else:
                faction.take_turn()

        nonelist = []
        for player in PLAYERS:
            if player.action == 'NONE': nonelist.append(1)
        if len(nonelist) == len(PLAYERS):
            print 'Game over!'
            for player in PLAYERS:
                for x in range(X):
                    for y in range(Y):
                        if MAP[x][y].active and MAP[x][y].color == player.color:
                            player.oList.append(( x, y ))
                player.hColor = player.color
                player.fancyCapture()
            while not XIT:
                act = event( PLAYERS[0] )
                if act == 'break':
                    XIT = True
        
def main(argv):

    root_init()
    
    try: mapname = argv[1]
    except: mapname = 'map'
    response = make_map('maps/' + mapname)

    if argv[0]: PLAYERS[0].player = False
    
    XIT = False
    if response == 'FAIL':
        print 'Quitting game! Reason: Failed map'
        XIT = True
    if 1 > len(PLAYERS) or len(PLAYERS) > 4:
        print 'Quitting game! Reason: Cannot have %s players' % len(PLAYERS)
        XIT = True

    if not XIT: UpdateScore()
    run_game(XIT)

    pygame.quit()

def term_main():

    maps = [filename for filename in os.listdir('maps')]
    argv = [False, 'map2_2']
    msg = ''
    while 1:


        os.system(['clear', 'cls'][os.name == 'nt'])
        print('Rune Warz %s\n' % VERSION)
        print('Commands:')
        print(' play\t\t- Play!')
        print(' map set\t- Set map (currently: %s)' % argv[1])
        print(' map list\t- View available maps')
        print(' ai\t\t- Let AI play for you (currently: %s)' % argv[0])
        print(' exit\t\t- Exit game\n')
        print(msg + '\n')
        
        cmd = raw_input('> ')

        if cmd == 'play':
            if argv[1] is None:
                msg = 'You need to set a map to play'
            else:
                main(argv)
        if cmd == 'map list':
            msg = 'Available maps: \n' + '\n'.join(maps)
        elif cmd[:8] == 'map set ':
            if cmd[8:] in maps:
                argv[1] = cmd[8:]
                msg = 'Map set to '+ argv[1]
            else:
                msg = 'Map "'+ cmd[8:] +'" not found'
        elif cmd == 'ai':
            if argv[0]:
                msg = 'Player1 is now controlled by human'
                argv[0] = False
            else:
                msg = 'Player1 is now controlled by computer'
                argv[0] = True
        elif cmd == 'exit': break
        else: msg = 'Unknown command'
    
    
if __name__ == '__main__':
    #main()
    term_main()
