import pygame as pg
import sys
import math

display = pg.display.set_mode((1280,720))
clock = pg.time.Clock()

player_walk = {"front":[pg.image.load("./ressources/images/player_front_"+str(x)+".png") for x in range(1,5)],
"back":[pg.image.load("./ressources/images/player_back_"+str(x)+".png") for x in range(1,5)],
"left":[pg.image.load("./ressources/images/player_left_"+str(x)+".png") for x in range(1,5)],
"right":[pg.image.load("./ressources/images/player_right_"+str(x)+".png") for x in range(1,5)]}

slime_animation = [pg.image.load("./ressources/images/slime_"+str(x)+".png") for x in range(1,5)]
slime_damage = pg.image.load("./ressources/images/slime_damage.png")

def checkAttack(ennemy,attack):

    l1=(ennemy.x-display_scroll[0],ennemy.y-display_scroll[1])
    r1=(ennemy.x+ennemy.width-display_scroll[0],ennemy.y+ennemy.height-display_scroll[1])
    l2=(attack.x,attack.y)
    r2=(attack.x+attack.width,attack.y+attack.height)

    if (l1[0] == r1[0] or l1[1] == r1[1] or l2[0] == r2[0] or l2[1] == r2[1]):
        return False
       
    if(l1[0] >= r2[0] or l2[0] >= r1[0]):
        return False

    if(r1[1] <= l2[1] or r2[1] <= l1[1]):
        return False
 
    return True

class Player:
    def __init__(self,x,y,width,height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = 10
        self.animation_count = 0
        self.orientation = "front"
        self.moving = False
        self.right_equip = "sword"
        self.left_equip = "fire_small"

    def main(self, display):
        if self.animation_count >= 31:
            self.animation_count = 0
        self.animation_count += 1

        if self.moving:
            display.blit(pg.transform.scale(player_walk[self.orientation][self.animation_count//8],(128,128)), (self.x, self.y))
            self.moving = False
        else:
            display.blit(pg.transform.scale(player_walk[self.orientation][1],(128,128)), (self.x, self.y))

class Ennemy:
    def __init__(self,x,y,width,height,type,level):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = type
        self.level = level
        self.stats = {
            "health":50+10*level,
            "attack":5+2*level,
            "armor":10+level,
            "mr":10+level
        }
        self.animation_count = 0
        self.damage_frames = 0

    def main(self, display):
        if self.damage_frames > 0:
            self.damage_frames -= 1
            display.blit(pg.transform.scale(slime_damage, (64,64)), (self.x-display_scroll[0], self.y-display_scroll[1]))
            return
        if self.animation_count >= 63:
            self.animation_count = 0
        self.animation_count += 1
        
        display.blit(pg.transform.scale(slime_animation[self.animation_count//16],(64,64)), (self.x-display_scroll[0], self.y-display_scroll[1]))
    
    def damage(self, player):
        display.blit(pg.transform.scale(slime_damage, (64,64)), (self.x-display_scroll[0], self.y-display_scroll[1]))
        self.damage_frames = 16

class Attack:
    def __init__(self,x,y,mouse_x,mouse_y,width,height,speed,duration,player):
        self.player = player
        self.x = x-(width//2)
        self.y = y-(height//2)
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.width = width
        self.height = height
        self.duration = duration
        self.speed = speed
        self.angle = math.atan2(y-mouse_y,x-mouse_x)
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed
        self.x-=int(self.x_vel)
        self.y-=int(self.y_vel)
    
    def __del__(self):
        print("deleted bullet")

    def main(self, display, keys):
        if self.duration == 0:
            return
        self.duration-=1
        self.x -= int(self.x_vel)
        self.y -= int(self.y_vel)
        if keys[pg.K_q]:
            self.x += player.speed
        if keys[pg.K_d]:
            self.x -= player.speed
        if keys[pg.K_z]:
            self.y += player.speed
        if keys[pg.K_s]:
            self.y -= player.speed
        pg.draw.rect(display, (255,255,255), (self.x, self.y, self.width, self.height))

player = Player(624,344,32,32)

display_scroll = [0,0]

player_attacks = []

ennemies = [Ennemy(0,0,64,64,"slime",1)]

items = {
    "sword":lambda player,mouse_x,mouse_y:Attack(player.x+64,player.y+64,mouse_x,mouse_y,200,200,15,1,player),
    "fire_small":lambda player,mouse_x,mouse_y:Attack(player.x+64,player.y+64,mouse_x,mouse_y,5,5,45,120,player)
}

while True:
    display.fill((0,0,0))

    mouse_x, mouse_y = pg.mouse.get_pos()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            player_attacks.append(items[player.right_equip](player,mouse_x,mouse_y))
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            player_attacks.append(items[player.left_equip](player,mouse_x,mouse_y))
    
    keys = pg.key.get_pressed()

    #pg.draw.rect(display, (255,255,255), (100-display_scroll[0], 100-display_scroll[1], 20, 20))

    if keys[pg.K_q]:
        display_scroll[0] -= player.speed
        player.orientation = "left"
        player.moving = True
    if keys[pg.K_d]:
        display_scroll[0] += player.speed
        player.orientation = "right"
        player.moving = True
    if keys[pg.K_z]:
        display_scroll[1] -= player.speed
        player.orientation = "back"
        player.moving = True
    if keys[pg.K_s]:
        display_scroll[1] += player.speed
        player.orientation = "front"
        player.moving = True

    for ennemy in ennemies:
        ennemy.main(display)

    for attack in player_attacks:
        if attack.duration == 0:
            del attack
            continue
        attack.main(display,keys)
        for ennemy in ennemies:
            #if ennemy.x-display_scroll[0] <= attack.x <= ennemy.x+ennemy.width-display_scroll[0] and ennemy.y-display_scroll[1] <= attack.y <= ennemy.y+ennemy.height-display_scroll[1]:
            if checkAttack(ennemy,attack):
                ennemy.damage(player)

    player.main(display)

    clock.tick(60)
    pg.display.update()