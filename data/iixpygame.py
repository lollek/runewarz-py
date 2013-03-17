#! /usr/bin/env python2.7

import pygame
from pygame.locals import *

def root_init(ROOT_W, ROOT_H, VERSION):

    """ Root window, Tile image, Blit list """
    global ROOT, TILE, LAUNDRY
    pygame.init()
    pygame.display.set_caption('Rune Warz '+VERSION)
    ROOT = pygame.display.set_mode((ROOT_W, ROOT_H))
    TILE = pygame.image.load('data/tiles_new.png').convert()
    LAUNDRY = []

def root_exit():
    pygame.quit()
    
def root_blit(source, target):

    """ Blitting images on top of each other """
    ROOT.blit(TILE, source, target)
    LAUNDRY.append(source)

def root_flip():

    """ Updating the screen """
    pygame.display.update(LAUNDRY)
    LAUNDRY[:] = []

def root_clean():

    """ Filling the whole screen with black """
    ROOT.fill((0, 0, 0))

def root_event():
    event = pygame.event.wait()

    if event.type == pygame.MOUSEMOTION:
        return('MOUSEMOTION', pygame.mouse.get_pos())

    elif event.type == pygame.MOUSEBUTTONDOWN:
        return('MOUSEBUTTONDOWN', pygame.mouse.get_pressed())

    elif event.type == pygame.KEYDOWN:
        return('KEYDOWN', pygame.key.name(event.key))

    else:
        return('UNKNOWN', 0)
        

def update_scores(OFFSET_X, OFFSET_Y, Y, PLAYERS):
    y = OFFSET_Y + Y*15 + 20
    
    for player in PLAYERS:
        x = OFFSET_X
        score = len(player.caps)
        root_blit((x, y, 15, 15), (player.color*15, player.sym*15, 15, 15))
        x += 15
        while score > 0:
            root_blit((x, y, 1, 15), (player.color*15, player.sym*15, 1, 15))
            score -= 1
            x += 1
        y += 20
    root_flip()
