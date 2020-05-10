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

WIDTH = 400
HEIGHT = 300

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

        if self.x > WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.angle = 180 - self.angle
        if self.x < self.radius:
            self.x = self.radius
            self.angle = 180 - self.angle
        if self.y > HEIGHT - self.radius:
            self.y = HEIGHT - self.radius
            self.angle = 360 - self.angle
        if self.y < self.radius:
            self.y = self.radius
            self.angle = 360 - self.angle

        self.velocity -= self.friction
        if self.velocity < 0:
           self.velocity = 0

class Stick:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.angle = 0

    def set_angle(self, ball_obj):
        position = pygame.mouse.get_pos()
        self.x = position[0]
        self.y = position[1]
        self.angle = degrees(atan2(self.y - ball_obj.y, self.x - ball_obj.x))

def ball_collided(ball1, ball2):
    distance = ((ball1.x - ball2.x)**2 + (ball1.y - ball2.y)**2)**(0.5)
    #print("Distance: " + str(distance))
    #print(ball1.x, ball1.y, ball2.x, ball2.y)
    if distance <= (ball1.radius + ball2.radius + 1):
        return True
    else:
        return False

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
                #if a.angle > 180:
                #        a.angle -= 360
                #elif a.angle < -180:
                #    a.angle += 360
                #print("A velocity and angle: " + str(a.velocity) + " || "+ str(a.angle))
                pb = v2 + d
                polar_b = cmath.polar(pb)
                b.velocity = polar_b[0]
                b.angle = degrees(polar_b[1])
                #if b.angle > 180:
                #    b.angle -= 360
                #elif b.angle < -180:
                #        b.angle += 360
                #print("B velocity and angle: " + str(b.velocity) + " || "+ str(b.angle))
                
                fix_overlap(a, b)
                
    for a in balls:
        a.collided = False

def fix_overlap(ball1, ball2):
     distance = ((ball1.x - ball2.x)**2 + (ball1.y - ball2.y)**2)**(0.5) 
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
    balls.append(Ball(10 + 20*x, 10 + 20*x))
    balls[x].color = random.choice(colors)
#balls.append(Ball(200, 110))
#balls.append(Ball(50, 50))
#balls[1].color = BLACK 
#balls[2].color = BLUE
stick = Stick()

# Initialize pygame and sets screen size and caption
pygame.init()
size = (400, 300)
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
pygame.display.set_caption("8 Ball Pool by Raul Vieira")

clock = pygame.time.Clock()
# Main loop
while True:
    screen.fill(GREEN)
    for event in pygame.event.get():
        # Closes the game if user clicked the X
        if event.type == pygame.QUIT:  
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            balls[0].set_force_angle(8, stick.angle)
            #balls[0].set_force_angle(4, 180)
            #balls[1].set_force_angle(4, 0)
            print(balls[0].angle)

            
    #balls[0].move()
    #balls[1].move()
    #balls[2].move()
    for ball in balls:
        ball.move()
    check_collisions()
    stick.set_angle(balls[0])
    #print(stick.angle)
    clock.tick(60)
    # Update the screen
    pygame.display.flip()