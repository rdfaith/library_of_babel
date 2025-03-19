import pygame
import time
from time import *
from pygame import *

pygame.init()

window_height = 640
window_width = 1200

class Player:
    def __init__(self, speed, px, py, sprite, sizex,sizey,jumpheight, state):
        self.speed = speed
        self.px = px
        self.py = py
        self.sprite = sprite
        self.sizex = sizex
        self.sizey = sizey
        self.jumpheight = jumpheight
        self.state = state
    

dino = Player(10,window_width/2, window_height-200,"nah",40,40,20,"stand")
dinorg = Player(10,window_width/2, window_height-200,"nah",40,40,20,"stand")
player_hitbox = Rect(dino.px,dino.py,dino.sizex,dino.sizey)

    

floor = Rect(0, window_height-10, window_width, 1)
platform = Rect(40,window_height-40,60,20)
platform2 = Rect(200,window_height-100,60,20)
hitboxes = [
    
    floor,
    platform,
    platform2
]



screen = pygame.display.set_mode((window_width,window_height))

clock = pygame.time.Clock()
run = True
white = (255,255,255)
blue = (0,0,255)
black = (0,0,0)
gah = (255,0,0)
dah = (0,255,0)
camera_offset_x = 0
player_speed_x = 10
velocity = 500*0.5
deg = 0.5
jumpy = True
jumptime = 0
jumping = False
falling = True
player_landbox = Rect(dino.px,dino.py+10,dino.sizex,dino.sizey)
sideboxleft = Rect(dino.px-10,dino.py,dino.px,dino.sizey)
sideboxright = Rect(dino.px+20,dino.py,dino.sizex+20,dino.sizey)
pushboxes = [Rect(150,20,20,20)]
pushbox_landbox = [Rect(150,20+10,20,20)]

while run:
    for event in pygame.event.get():
        if event.type == KEYUP:
            if event.key == K_w:
                jumptime = 6

        
    
        # if event is of type quit then  
        # set running bool to false 
        if event.type == pygame.QUIT: 
            run = False
    keys = pygame.key.get_pressed()
    if keys[K_d]:
        if Rect.collidelist(sideboxright, hitboxes) == -1:
            dino.px += dino.speed
    if keys [K_w]:
        if falling != True:
            if Rect.collidelist(Rect(dino.px,dino.py-20,dino.sizex,dino.sizey), hitboxes) == -1:
                jumping = True
            else:
                jumping = False

    if keys[K_a]:
        if Rect.collidelist(sideboxleft, hitboxes) == -1:
            dino.px -= dino.speed


            
 
    if jumping == True:
        if jumpy == True:
            if jumptime <= 5:
                dino.py -= dino.speed
                jumptime += 1
            else:
                jumpy = False
                
        else:
            if jumptime == 6:
                
                jumptime = 0
            if Rect.collidelist(player_landbox, hitboxes) == -1:
                
                dino.py += dino.speed
            else:
                jumping = False
                jumptime = 0
                jumpy = True
    if jumping == False:
        if Rect.collidelist(player_landbox, hitboxes) == -1: 
            dino.py += dino.speed
            falling = True
            
        else:
            falling = False

    pygame.display.update()
    player_hitbox = Rect(dino.px,dino.py,dino.sizex,dino.sizey)
    player_landbox = Rect(dino.px,dino.py+10,dino.sizex,dino.sizey)
    sideboxleft = Rect(dino.px-10,dino.py,dino.sizex-10,dino.sizey)
    sideboxright = Rect(dino.px+10,dino.py,dino.sizex,dino.sizey)
    clock.tick(30)
    screen.fill(black)
    draw.rect(screen, white,floor,10)
    draw.rect(screen,blue,player_hitbox,25)
    draw.rect(screen,white,platform2, 1)
    #draw.rect(screen,gah,player_landbox,2)
    #draw.rect(screen,gah,sideboxleft,2)
    #draw.rect(screen,gah,sideboxright,2)
    draw.rect(screen,white,platform,2)