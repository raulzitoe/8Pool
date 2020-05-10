import pygame
import pygame.gfxdraw
import sys
from math import *
import cmath
import random

# Colors used
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (127, 127, 127)
colors = [BLACK, BLUE, RED, GRAY]

MARGIN_TOP = 26
MARGIN_BOTTOM = 27
MARGIN_LEFT = 26
MARGIN_RIGHT = 27
WIDTH = 800
HEIGHT = 448
LEFT_CLICK = 1
RIGHT_CLICK = 3

background_img = pygame.image.load(r"C:\Users\raul-\Documents\Python projects\8Pool\table.png")
stick_img = pygame.image.load(r"C:\Users\raul-\Documents\Python projects\8Pool\stick.png")


class Ball:

    def __init__(self, x=50, y=50):
        self.x = x
        self.y = y
        self.friction = 0.02
        self.velocity = 0.0
        self.angle = 0
        self.radius = 10
        self.color = WHITE
        self.collided = False

    def set_force_angle(self, force, angle):
        self.velocity = force
        self.angle = angle

    def move(self):
        self.x = self.x + self.velocity*cos(radians(self.angle))
        self.y = self.y + self.velocity*sin(radians(self.angle))
        
        #pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, self.color)
        pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, self.color)

        if self.x > (WIDTH - MARGIN_RIGHT) - self.radius:
            self.x = (WIDTH - MARGIN_RIGHT) - self.radius
            self.angle = 180 - self.angle
        if self.x < self.radius + MARGIN_LEFT:
            self.x = self.radius + MARGIN_LEFT
            self.angle = 180 - self.angle
        if self.y > HEIGHT - MARGIN_BOTTOM - self.radius:
            self.y = HEIGHT - MARGIN_BOTTOM - self.radius
            self.angle = 360 - self.angle
        if self.y < self.radius + MARGIN_TOP:
            self.y = self.radius + MARGIN_TOP
            self.angle = 360 - self.angle

        self.velocity -= self.friction
        if self.velocity < 0:
           self.velocity = 0

class Put:

    def __init__(self, x, y, r=16):
        self.x = x
        self.y = y
        self.color = WHITE
        self.radius = r
    
    def draw(self):
        #pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, self.color)
        #pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, self.color)
        pass
    
    def check_put(self, balls):
        for ball in balls:
            distance = calc_distance(ball, self)
            if distance < self.radius:
                if ball == balls[0]:
                    ball.x = 600
                    ball.y = 220
                    ball.velocity = 0
                else:
                    balls.remove(ball)
class Stick:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.angle = 0
        self.image = stick_img
        self.rect = self.image.get_rect()
        self.rect.center = (300, 300)
        self.original_image = self.image
        self.dist_to_ball = 180
        self.is_charging = False
        self.hit = False
        self.hit_force = 0

    def set_angle(self, ball_obj):
        position = pygame.mouse.get_pos()
        #print(position)
        self.x = position[0]
        self.y = position[1]
        self.angle = degrees(atan2(ball_obj.y - self.y ,  ball_obj.x - self.x))
        print(self.angle)

    def update(self):
        if self.is_charging:
            self.dist_to_ball += 0.5
            if self.dist_to_ball > 250:
                self.dist_to_ball = 250
        else:
            self.dist_to_ball -= 8
            if self.dist_to_ball < 180:
                self.dist_to_ball = 180
        
        if self.hit and self.dist_to_ball == 180:
            self.hit = False
            balls[0].set_force_angle(self.hit_force, self.angle)

        self.image = pygame.transform.rotate(self.original_image, -self.angle - 90)
        #self.angle += 1 % 360  # Value will reapeat after 359. This prevents angle to overflow.
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        

        #y = x * tan(radians(self.angle))
        #(x - balls[0].x)**2 + (y - balls[1].y)**2 = r**2
        angle = self.angle
        self.x = balls[0].x - self.dist_to_ball * cos(radians(angle))
        self.y = balls[0].y - self.dist_to_ball * sin(radians(angle))

        self.rect.center = (self.x, self.y)  # Put the new rect's center at old center.
        screen.blit(self.image, self.rect)

        


def ball_collided(ball1, ball2):
    distance = calc_distance(ball1, ball2)
    #print("Distance: " + str(distance))
    #print(ball1.x, ball1.y, ball2.x, ball2.y)
    if distance <= (ball1.radius + ball2.radius + 1):
        return True
    else:
        return False

def has_movement(objs):
    for obj in objs:
        if obj.velocity > 0:
            return True
    return False

def calc_distance(a, b):
    return ((a.x - b.x)**2 + (a.y - b.y)**2)**(0.5)


def check_collisions():
    for a in balls:
        for b in balls:
            if a is not b and ball_collided(a, b) and not a.collided and not b.collided:
                #print("COLLIDED: " + str(degrees(atan2(a.x-b.x, a.y-b.y))))
               
                a.collided = True
                b.collided = True
                p1 = complex(a.x, a.y)
                v1 = complex(a.velocity*cos(radians(a.angle)), a.velocity*sin(radians(a.angle)))
                p2 = complex(b.x, b.y)
                v2 = complex(b.velocity*cos(radians(b.angle)), b.velocity*sin(radians(b.angle)))
                
                p12 = p1 - p2
                d = ((v1 - v2) / p12).real * p12
                pa = v1 - d
                polar_a = cmath.polar(pa)
                a.velocity = polar_a[0]
                a.angle = degrees(polar_a[1])

                pb = v2 + d
                polar_b = cmath.polar(pb)
                b.velocity = polar_b[0]
                b.angle = degrees(polar_b[1])
                
                fix_overlap(a, b)       
    for a in balls:
        a.collided = False

def fix_overlap(ball1, ball2):
     distance = calc_distance(ball1, ball2)
     while distance <= (ball1.radius + ball2.radius + 1):
        if ball1.x > ball2.x:
            ball1.x += 0.1
        else:
            ball1.x -= 0.1
        if ball1.y > ball2.y:
            ball1.y += 0.1
        else:
            ball1.y -= 0.1
        distance = ((ball1.x - ball2.x)**2 + (ball1.y - ball2.y)**2)**(0.5) 


balls = []
balls.append(Ball(250, 100))
for x in range(1,10):
    balls.append(Ball(60 + 20*x, 60 + 20*x))
    balls[x].color = random.choice(colors)
#balls.append(Ball(200, 110))
#balls.append(Ball(50, 50))
#balls[1].color = BLACK 
#balls[2].color = BLUE
stick = Stick()
puts = []

puts.append(Put(32, 36))
puts.append(Put(398, 24))
puts.append(Put(765, 36))
puts.append(Put(32, 408))
puts.append(Put(398, 420))
puts.append(Put(765, 408))

# Initialize pygame and sets screen size and caption
pygame.init()
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
pygame.display.set_caption("8 Ball Pool by Raul Vieira")

clock = pygame.time.Clock()
# Main loop
while True:
    screen.fill(GREEN)
    screen.blit(background_img, (0, 0))
    for event in pygame.event.get():
        # Closes the game if user clicked the X
        if event.type == pygame.QUIT:  
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not has_movement(balls) and event.button == LEFT_CLICK:
                stick.is_charging = True
                #balls[0].set_force_angle(4, 180)
                #balls[1].set_force_angle(4, 0)
        elif event.type == pygame.MOUSEBUTTONUP:
            if not has_movement(balls) and event.button == LEFT_CLICK:
                stick.is_charging = False
                stick.hit = True
                stick.hit_force = (stick.dist_to_ball - 180) * 0.3
            if not has_movement(balls) and event.button == RIGHT_CLICK:
                stick.dist_to_ball = 180
                
            
    #balls[0].move()
    #balls[1].move()
    #balls[2].move()
    for ball in balls:
        ball.move()
    for put in puts:
        put.draw()
        put.check_put(balls)
    check_collisions()
    stick.set_angle(balls[0])
    if not has_movement(balls):
        stick.update()
    #print(stick.angle)
    clock.tick(60)
    # Update the screen
    pygame.display.flip()