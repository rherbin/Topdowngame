import pygame as pg
import sys
import math
import random as rd

display = pg.display.set_mode((1920,1080))
clock = pg.time.Clock()

player_walk = {
    "front":[pg.image.load("./ressources/images/player_front_"+str(x)+".png").convert() for x in range(1,5)]+[pg.image.load("./ressources/images/player_front_2.png")],
    "back":[pg.image.load("./ressources/images/player_back_"+str(x)+".png").convert() for x in range(1,5)]+[pg.image.load("./ressources/images/player_back_2.png")],
    "left":[pg.image.load("./ressources/images/player_left_"+str(x)+".png").convert() for x in range(1,5)]+[pg.image.load("./ressources/images/player_dash.png")],
    "right":[pg.image.load("./ressources/images/player_right_"+str(x)+".png").convert() for x in range(1,5)]+[pg.transform.flip(pg.image.load("./ressources/images/player_dash.png"),True,False)]
}

slime_animation = [pg.image.load("./ressources/images/slime_"+str(x)+".png").convert() for x in range(1,5)]
slime_damage = pg.image.load("./ressources/images/slime_damage.png").convert()

display_scroll = [0,0]
player_move = [0,0]

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

def checkHitscanAttack(f,ennemy):
    points = [
        (ennemy.x-display_scroll[0],ennemy.y-display_scroll[1]),
        (ennemy.x-display_scroll[0], ennemy.y+ennemy.height-display_scroll[1]),
        (ennemy.x+ennemy.width-display_scroll[0],ennemy.y-display_scroll[1]),
        (ennemy.x+ennemy.width-display_scroll[0],ennemy.y+ennemy.height-display_scroll[1])
    ]
    if f(points[0][0]) < points[0][1] and f(points[1][0]) < points[1][1] and f(points[2][0]) < points[2][1] and f(points[3][0]) < points[3][1]:
        return False
    elif f(points[0][0]) > points[0][1] and f(points[1][0]) > points[1][1] and f(points[2][0]) > points[2][1] and f(points[3][0]) > points[3][1]:
        return False
    return True

def getEquation(mouse_x,mouse_y):
    x2 = display.get_size()[0]//2
    y2 = display.get_size()[1]//2
    mouse_x-=0
    mouse_y-=0
    a = (y2-mouse_y)/(x2-mouse_x)
    b = mouse_y-a*mouse_x
    print(f"y={a}x+{b}")
    return lambda x:a*x+b

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
        self.isdashing = False
        self.right_equip = "fire_small"
        self.left_equip = "shotgun"

    def main(self, display):
        if self.animation_count >= 31:
            self.animation_count = 0
        self.animation_count += 1
        
        if self.isdashing:
            self.speed = 30
            display.blit(pg.transform.scale(player_walk[self.orientation][4],(128,128)), (self.x, self.y))
            global dash_count
            print(dash_count)
            dash_count -= 1
            if dash_count <= 0:
                self.isdashing = False
        elif self.moving:
            display.blit(pg.transform.scale(player_walk[self.orientation][self.animation_count//8],(128,128)), (self.x, self.y))
            self.moving = False
            self.speed = 10
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
            "basehealth":50+10*level,
            "attack":5+2*level,
            "armor":10+level,
            "mr":10+level
        }
        self.animation_count = 0
        self.damage_frames = 0

    def main(self, display):
        pg.draw.rect(display,(128,128,128),(self.x-display_scroll[0],self.y-20-display_scroll[1],self.width,10))
        pg.draw.rect(display,(255,0,0),(self.x-display_scroll[0],self.y-20-display_scroll[1],int(self.width*(self.stats["health"]/self.stats["basehealth"])),10))
        if self.damage_frames > 0:
            self.damage_frames -= 1
            display.blit(pg.transform.scale(slime_damage, (64,64)), (self.x-display_scroll[0], self.y-display_scroll[1]))
            return
        if self.animation_count >= 63:
            self.animation_count = 0
        self.animation_count += 1
        
        display.blit(pg.transform.scale(slime_animation[self.animation_count//16],(64,64)), (self.x-display_scroll[0], self.y-display_scroll[1]))
        

    
    def damage(self, player, attack):
        display.blit(pg.transform.scale(slime_damage, (64,64)), (self.x-display_scroll[0], self.y-display_scroll[1]))
        self.damage_frames = 16
        self.stats["health"] -= attack.stats["damage"]
        if self.stats["health"] < 0:
            self.stats["health"] = 0

class Attack:
    def __init__(self,mouse_x,mouse_y,range,duration,damage,player):
        stats = {"damage":damage}
        self.player = player
        self.width = range
        self.height = range
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.duration = duration
        self.baseduration = duration
        self.hitscan = False
        self.angle = math.atan2(player.y+64-mouse_y,player.x+64-mouse_x)
        self.exists = True
        if (3*math.pi)/4 >= self.angle >= math.pi/4:
            #top
            self.x = player.x-(range//2)+64
            self.y = player.y-range+64
        elif math.pi/4 >= self.angle >= -math.pi/4:
            #left
            self.x = player.x-range+64
            self.y = player.y-(range//2)+64
        elif -math.pi/4 >= self.angle >= -(3*math.pi)/4:
            #bottom
            self.x = player.x-(range//2)+64
            self.y = player.y+64
        else:
            #right
            self.x = player.x+64
            self.y = player.y-(range//2)+64
    
    def __del__(self):
        print("deleted bullet")

    def main(self, display, keys):
        if self.duration == 0:
            self.exists = False
            return
        self.duration-=1
        pg.draw.rect(display, (255,255,255), (self.x, self.y, self.width, self.height))
        

class Projectile(Attack):
#def __init__(self,mouse_x,mouse_y,range,duration,speed,size,player,particle,isgun=False,hitscan=False):
    def __init__(self,mouse_x,mouse_y,stats,player,particle,isgun=False,hitscan=False):
        Attack.__init__(self,mouse_x,mouse_y,stats["range"],stats["duration"],stats["damage"],player)
        self.x = player.x+64
        self.y = player.y+64
        self.width, self.height = stats["size"]
        self.stats = stats
        self.x_vel = math.cos(self.angle) * stats["speed"]
        self.y_vel = math.sin(self.angle) * stats["speed"]
        self.particle = particle
        self.isgun = isgun
        self.hitscan = hitscan
    
    def setAngle(self, angle):
        self.angle = angle
        self.x_vel = math.cos(self.angle) * self.stats["speed"]
        self.y_vel = math.sin(self.angle) * self.stats["speed"]
    
    def main(self, display, keys):
        if self.duration == 0:
            self.exists = False
            return
        if self.duration <= self.baseduration-3 and self.isgun:
            pg.draw.line(display, (255,255,255), (self.x+(self.x_vel)*2,self.y+(self.y_vel)*2), (self.x,self.y),4)
        self.x -= int(self.x_vel)
        self.x += player_move[0]
        self.y -= int(self.y_vel)
        self.y += player_move[1]
        """if keys[pg.K_q]:
            self.x += player.speed
        if keys[pg.K_d]:
            self.x -= player.speed
        if keys[pg.K_z]:
            self.y += player.speed
        if keys[pg.K_s]:
            self.y -= player.speed"""
        if not self.isgun:
            pg.draw.circle(display, (255,0,0), (self.x, self.y), self.width//2)
        particles.append(self.particle(self.x,self.y))

        self.duration-=1

def Particle(x,y,x_vel,y_vel,duration):
    return [[x,y],[x_vel,y_vel],duration]

def Shotgun(mouse_x,mouse_y,duration,speed,ammos,player,particle):
    bullets = [Projectile(mouse_x,mouse_y,{"range":0,"duration":duration,"speed":speed,"size":(5,5),"damage":10},player,particle,True) for _ in range(ammos)]
    for x in range(len(bullets)):
        bullets[x].setAngle( bullets[x].angle - (math.pi/16 - math.pi/(16*ammos)) + ( math.pi/(8*ammos) * x ) )
    return bullets

player = Player(display.get_size()[0]//2-64,display.get_size()[1]//2-64,32,32)

player_attacks = []

particles = []

ennemies = [Ennemy(0,0,64,64,"slime",1)]

items = {
    "sword":lambda player,mouse_x,mouse_y:Attack(mouse_x,mouse_y,200,4,30,player),
    "fire_small":lambda player,mouse_x,mouse_y:Projectile(mouse_x,mouse_y,{"range":0,"duration":120,"speed":45,"size":(20,20),"damage":20},player,lambda x,y:Particle(x,y,rd.randint(-2,2),rd.randint(-2,2),rd.randint(20,40))),
    "shotgun":lambda player,mouse_x,mouse_y:Shotgun(mouse_x,mouse_y,120,45,5,player,lambda x,y:Particle(x,y,rd.randint(-2,2),rd.randint(-2,2),rd.randint(5,20))),
    "sniper":lambda player,mouse_x,mouse_y:Projectile(mouse_x,mouse_y,{"range":0,"duration":60,"speed":180,"size":(3,3),"damage":60},player,lambda x,y:Particle(x,y,0,0,0),True,True)
}

dash_count = 0

while True:
    display.fill((0,0,0))

    mouse_x, mouse_y = pg.mouse.get_pos()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            attack = items[player.left_equip](player,mouse_x,mouse_y)
            if not(isinstance(attack,list)):
                player_attacks.append(attack)
            else:
                player_attacks += attack
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            attack = items[player.right_equip](player,mouse_x,mouse_y)
            if not(isinstance(attack,list)):
                player_attacks.append(attack)
            else:
                player_attacks += attack
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and dash_count == 0:
                dash_count = 10
                player.isdashing = True

    
    keys = pg.key.get_pressed()

    #pg.draw.rect(display, (255,255,255), (100-display_scroll[0], 100-display_scroll[1], 20, 20))

    player_move = [0,0]

    if keys[pg.K_q]:
        display_scroll[0] -= player.speed
        player_move[0] = player.speed
        player.orientation = "left"
        player.moving = True
    if keys[pg.K_d]:
        display_scroll[0] += player.speed
        player_move[0] = -player.speed
        player.orientation = "right"
        player.moving = True
    if keys[pg.K_z]:
        display_scroll[1] -= player.speed
        player_move[1] = player.speed
        player.orientation = "back"
        player.moving = True
    if keys[pg.K_s]:
        display_scroll[1] += player.speed
        player_move[1] = -player.speed
        player.orientation = "front"
        player.moving = True

    for ennemy in ennemies:
        ennemy.main(display)
    
    x=0
    while x < len(particles):
        if particles[x][2] <= 0:
            del particles[x]
            continue
        particles[x][0][0] += particles[x][1][0] + player_move[0]
        particles[x][0][1] += particles[x][1][1] + player_move[1]
        particles[x][2] -= 1
        pg.draw.circle(display, (255,255,255), [int(particles[x][0][0]), int(particles[x][0][1])], math.ceil(particles[x][2]/5))
        x+=1

    x=0
    while x < len(player_attacks):
        if not(player_attacks[x].exists):
            del player_attacks[x]
            continue
        player_attacks[x].main(display,keys)
        for ennemy in ennemies:
            if checkAttack(ennemy,player_attacks[x]) and not player_attacks[x].hitscan:
                ennemy.damage(player,player_attacks[x])
            elif player_attacks[x].hitscan and attack.duration == attack.baseduration:
                f = getEquation(mouse_x,mouse_y)
                if checkHitscanAttack(f,ennemy):
                    ennemy.damage(player,player_attacks[x])

        x+=1

    player.main(display)

    clock.tick(60)
    pg.display.update()