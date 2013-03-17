#! /usr/bin/env python2.7

# Rune Warz
# Created 2013-03-11 by Olle Kvarnstrom
# Images by Sofie Aid

VERSION = 'v0.1.4'

""" Standard libraries """
import os
from random import randint, shuffle
from time import sleep

""" Custom libraries, see data/__init__.py folder """
from data import *

"""GLOBALS:
MAP, PLAYERS
X, Y
OFFSET_X, OFFSET_Y
ROOT_W, ROOT_H, ROOT_T
"""

def make_map(filename, debugmode = False):

    """ Game Map, Player List """
    global MAP, PLAYERS
    global X, Y
    global OFFSET_X, OFFSET_Y
    
    """ Load mapfile """
    map_response = script.load_mapfile(filename, debugmode)
    if map_response[0] == 'ERR':
        print('make_map: Error received. Exiting')
        return('ERR', 0)
    else:
        map_data = map_response[1]
        X, Y = map_data[0]
        lines = map_data[1]

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
                        new_player = Player(len(PLAYERS)+2, MAP[x][y].color)
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

    sdl.root_clean()
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
        self.color = randint( 1, 8 )

    def draw(self, x, y, sym=None, force=False, is_unlocked=True):
        
        if self.active or force:
            x = OFFSET_X + x*ROOT_T
            y = OFFSET_Y + y*ROOT_T
            if is_unlocked:
                if sym is None:
                    sdl.root_blit((x, y, 15, 15), (self.color*15, 0, 15, 15))
                else:
                    sdl.root_blit((x, y, 15, 15), (self.color*15, sym*15, 15, 15))
            else:
                sdl.root_blit((x, y, 15, 15), (self.color*15, 15, 15, 15))
class Player:

    def __init__( self, sym, color):
        self.sym = sym
        self.color = color
        self.caps = []
        self.caps_in_focus = []

        self.action = None
        if self.sym == 2:
            self.player = True
            self.MPOS = (0,0)
        else:
            self.player = False

    def capture( self ):

        """ Capture all caps currently in caps_in_focus: """
        self.color = self.color_in_focus
        for cap in self.caps_in_focus:
            self.caps.append(cap)
        self.draw_caps()
        self.caps_in_focus[:] = []
        
        sdl.update_scores(OFFSET_X, OFFSET_Y, Y, PLAYERS)

    def fancyCapture( self ):

        """ Capture all caps in caps_in_focus on random at a time"""
        self.color = self.color_in_focus
        while self.caps_in_focus:
            shuffle(self.caps_in_focus)
            cx, cy = self.caps_in_focus[0]
            self.caps.append((cx, cy))
            MAP[cx][cy].color = self.color
            MAP[cx][cy].draw( cx, cy, self.sym, True )
            MAP[cx][cy].active = False
            del self.caps_in_focus[0]
            
            sdl.root_flip()
            sdl.update_scores(OFFSET_X, OFFSET_Y, Y, PLAYERS)
            sleep(0.1)
            
    def draw_caps( self ):
        for cx, cy in self.caps:
            MAP[cx][cy].color = self.color
            MAP[cx][cy].draw( cx, cy, self.sym, True )
            MAP[cx][cy].active = False
        sdl.root_flip()

    def take_turn( self, read_only = False ):
        ai_debug = False

        optColor = [r for r in range(1,9)]
        best = (None, [])
        
        for color in optColor:
            self.hover_over_color( color, True)
            if len(self.caps_in_focus) > len(best[1]):
                free_color = True
                for player in PLAYERS:
                    if player.color == color:
                        free_color = False
                if free_color:
                    best = ( color, self.caps_in_focus)

        if len(best[1]) > 0:
            self.color_in_focus = best[0]
            self.caps_in_focus = best[1]
            if not read_only: sleep(0.5)
            if not read_only: self.capture()
            self.action = 'CAPT'
            return 'OK'

        else:
            self.action = 'NONE'
            return 'DONE'

    def hover_over_color(self, color, read_only = False):

        """ Check if any other player is currently the wanted color: """
        color_is_available = True
        for other_player in PLAYERS:
            if other_player.color == color:
                color_is_available = False

        """ Find all caps of the selected color and show hover-effect """
        nearby_caps = []
        for cx, cy in self.caps:
            get_nearby_caps(cx, cy, color, nearby_caps)
            if nearby_caps:
                for cx, cy in nearby_caps:
                    if not read_only:
                        MAP[cx][cy].draw(cx, cy, self.sym, True, color_is_available)
                    get_nearby_caps(cx, cy, color, nearby_caps)
                if not read_only:
                    sdl.root_flip()

        self.caps_in_focus = nearby_caps
        self.color_in_focus = color

    def is_close_to_cap(self, cx, cy):
        """ Function to check if the cap is neighboring the player's """
        
        tmp_list = [(cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)]
        for cap in self.caps:
            if cap in tmp_list:
                return True
        return False


def is_cappable(cx, cy):

    """ True if Cap can be captured """
    if 0 <= cx < X:
        if 0 <= cy < Y:
            if MAP[cx][cy].active:
                return True
    return False

def get_nearby_caps(cx, cy, color, list_of_caps):
    tmp_list = [(cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)]
    for x, y in tmp_list:
        if is_cappable(x, y):
            if MAP[x][y].color == color:
                if (x, y) not in list_of_caps:
                    list_of_caps.append((x, y))

def event( player ):
    
    """ Event handling (keyboard/mouse input) """
    event = sdl.root_event()

    if event[0] == 'MOUSEMOTION':
        
        """ First, check if mouse has moved to a new tile: """
        mx, my = event[1]
        pos = ((mx-OFFSET_X)/ROOT_T, (my-OFFSET_Y)/ROOT_T)
        if pos != player.MPOS:
            player.MPOS = pos
            
            """ If it has, remove the hover-effect from old focused tiles: """
            for cx, cy in player.caps_in_focus:
                    MAP[cx][cy].draw(cx, cy)
            player.caps_in_focus[:] = []

            
            """ Then; check if the the tile that the mouse hovers
            over is close to the player and captureable: """
            if player.is_close_to_cap(pos[0], pos[1]):
                if is_cappable(pos[0], pos[1]):
                    color = MAP[pos[0]][pos[1]].color
                    player.hover_over_color(color)

            """ Finally, update the screen: """
            sdl.root_flip()

        
    elif event[0] == 'KEYDOWN':
        
        if event[1] == 'q': return 'break'

    elif event[0] == 'MOUSEBUTTONDOWN':

        for other_player in PLAYERS:
            if other_player.color == player.color_in_focus:
                return
        if player.caps_in_focus:
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
                            return
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
                            player.caps_in_focus.append(( x, y ))
                player.color_in_focus = player.color
                player.fancyCapture()
            while not XIT:
                act = event( PLAYERS[0] )
                if act == 'break':
                    XIT = True
        
def main(ai, mapname):

    global ROOT_W, ROOT_H, ROOT_T

    """ Init Graphics """
    ROOT_W, ROOT_H, ROOT_T = 800, 600, 15
    sdl.root_init(ROOT_W, ROOT_H, VERSION)

    """ Make map """
    XIT = False
    map_status = make_map('maps/' + mapname)

    """ Check everything went OK: """
    if map_status == 'FAIL':
        print 'Quitting game! Reason: Failed map'
        XIT = True
    elif 1 > len(PLAYERS) or len(PLAYERS) > 4:
        print 'Quitting game! Reason: Cannot have %s players' % len(PLAYERS)
        XIT = True

    """ Settings: """
    if ai: PLAYERS[0].player = False

    """ If all went well, game will start """
    if not XIT:
        sdl.update_scores(OFFSET_X, OFFSET_Y, Y, PLAYERS)
        run_game(XIT)

    """ Finally: kill the screen """
    sdl.root_exit()

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
                main(argv[0], argv[1])
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
