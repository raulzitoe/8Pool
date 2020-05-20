import pygame
import pygame.gfxdraw
import sys
from math import *
import cmath
import random
from network import Network
import socket
import pickle

# Colors used
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (127, 127, 127)

COLOR_1 = (228, 165, 28)
COLOR_2 = (3, 99, 177)
COLOR_3 = (206, 34, 21)
COLOR_4 = (139, 3, 122)
COLOR_5 = (208, 123, 2)
COLOR_6 = (4, 117, 34)
COLOR_7 = (124, 60, 7)
COLOR_8 = (0, 0, 0)
COLOR_9 = (238, 191, 100)
COLOR_10 = (3, 99, 177)
COLOR_11 = (161, 18, 2)
COLOR_12 = (127, 1, 63)
COLOR_13 = (165, 96, 3)
COLOR_14 = (4, 112, 30)
COLOR_15 = (125, 61, 7)
colors = (COLOR_1, COLOR_2, COLOR_3,
            COLOR_4, COLOR_5, COLOR_6, COLOR_7, 
            COLOR_8, COLOR_9, COLOR_10, COLOR_11, 
            COLOR_12, COLOR_13, COLOR_14, COLOR_15)
BX = 100
BY = 180

balls_pos = ((BX, BY), (BX, BY+22), (BX, BY+44), (BX, BY+66), (BX, BY+88),
              (BX+19, BY+11), (BX+19, BY+33), (BX+19, BY+55), (BX+19, BY + 77),
               (BX+38, BY+22), (BX+38, BY+44), (BX+38, BY+66),
               (BX+57, BY+33), (BX+57, BY+55),
               (BX+76, BY+44))

MARGIN_TOP = 26
MARGIN_BOTTOM = 27
MARGIN_LEFT = 26
MARGIN_RIGHT = 27
WIDTH = 800
MENU_HEIGHT = 50
HEIGHT = 448 + MENU_HEIGHT
LEFT_CLICK = 1
RIGHT_CLICK = 3
PLAYER1 = 1
PLAYER2 = 2
EVEN = 1
ODD = 2

background_img = pygame.image.load(r"C:\Users\raul-\Documents\Python projects\8Pool\table.png")
stick_img = pygame.image.load(r"C:\Users\raul-\Documents\Python projects\8Pool\stick.png")


class Game:

    def __init__(self):
        self.balls = []
        self.balls_put_even = []
        self.balls_put_odd = []
        self.balls.append(self.Ball((600, 220)))
        for x in range(15):
            self.balls.append(self.Ball(balls_pos[x]))
            self.balls[x+1].color = colors[x]
            self.balls[x+1].number = x+1
        self.stick = self.Stick()
        self.puts = []
        self.puts.append(self.Put(32, 36))
        self.puts.append(self.Put(398, 24))
        self.puts.append(self.Put(765, 36))
        self.puts.append(self.Put(32, 408))
        self.puts.append(self.Put(398, 420))
        self.puts.append(self.Put(765, 408))
        self.turn = PLAYER1
        self.p1 = 0
        self.first_put = False

    def toggle_turn(self):
        if self.turn == PLAYER1:
            self.turn = PLAYER2
        else:
            self.turn = PLAYER1

    def set_player_ball(self):
        if not self.first_put:
            if self.balls_put_even:
                self.first_put = True
                if self.turn == PLAYER1:
                    self.p1 = EVEN
                else:
                    self.p1 = ODD
            if self.balls_put_odd:
                self.first_put = True
                if self.turn == PLAYER1:
                    self.p1 = ODD
                else:
                    self.p1 = EVEN

    def has_movement(self, objs):
        for obj in objs:
            if obj.velocity > 0:
                return True
        if self.balls[0].x < 0:
            self.balls[0].x = 600
            self.balls[0].y = 220
        return False

    

    def check_collisions(self):
        for a in self.balls:
            for b in self.balls:
                if a is not b and ball_collided(a, b) and not a.collided and not b.collided:             
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
        for a in self.balls:
            a.collided = False
    
    def draw_balls_put(self):
        x, y, i, j = 420, 455, 0, 0
        for ball in self.balls_put_even:
            ball.draw_after_put(x+i, y)
            i += 30
        for ball in self.balls_put_odd:
            ball.draw_after_put(x+j, y+25)
            j += 30

    class Ball:

        def __init__(self, pos=(50, 50), number=0):
            self.x = pos[0]
            self.y = pos[1]
            self.friction = 0.02
            self.velocity = 0.0
            self.angle = 0
            self.radius = 10
            self.color = WHITE
            self.collided = False
            self.number = number

        def set_force_angle(self, force, angle):
            self.velocity = force
            self.angle = angle

        def move(self):
            self.x = self.x + self.velocity*cos(radians(self.angle))
            self.y = self.y + self.velocity*sin(radians(self.angle))
            #pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, self.color)
            pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, self.color)
            
            text = font.render(str(self.number), True, WHITE)
            xoff = 5
            yoff = 4
            if self.number < 10:
                xoff = 2
            if self.number != 0:
                screen.blit(text, (int(self.x) - xoff, int(self.y) - yoff))

            if self.x > (WIDTH - MARGIN_RIGHT) - self.radius:
                self.x = (WIDTH - MARGIN_RIGHT) - self.radius
                self.angle = 180 - self.angle
            if self.x < self.radius + MARGIN_LEFT:
                self.x = self.radius + MARGIN_LEFT
                self.angle = 180 - self.angle
            if self.y > HEIGHT - MARGIN_BOTTOM - self.radius - MENU_HEIGHT:
                self.y = HEIGHT - MARGIN_BOTTOM - self.radius - MENU_HEIGHT
                self.angle = 360 - self.angle
            if self.y < self.radius + MARGIN_TOP:
                self.y = self.radius + MARGIN_TOP
                self.angle = 360 - self.angle

            self.velocity -= self.friction
            if self.velocity < 0:
                self.velocity = 0
        
        def draw_after_put(self, x, y):
            self.x = x
            self.y = y
            pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, self.color)
            pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, self.color)
            text = font.render(str(self.number), True, WHITE)
            xoff = 5
            yoff = 4
            if self.number < 10:
                xoff = 2
            if self.number != 0:
                screen.blit(text, (int(self.x) - xoff, int(self.y) - yoff))


    class Put():

        def __init__(self, x, y, r=16):
            self.x = x
            self.y = y
            self.color = WHITE
            self.radius = r
        
        def draw(self):
            #pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, self.color)
            #pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, self.color)
            pass
        
        def check_put(self, balls, balls_put_even, balls_put_odd):
            for ball in balls:
                distance = calc_distance(ball, self)
                if distance < self.radius:
                    if ball == balls[0]:
                        #ball.x = 600
                        #ball.y = 220
                        ball.x = -200
                        ball.y = -200
                        ball.velocity = 0
                    else:
                        balls.remove(ball)
                        if ball.number % 2 == 0:
                            balls_put_even.append(ball)
                        else:
                            balls_put_odd.append(ball)


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

        def update(self, balls):
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
            x, y = self.rect.center
            self.rect = self.image.get_rect()
            angle = self.angle
            self.x = balls[0].x - self.dist_to_ball * cos(radians(angle))
            self.y = balls[0].y - self.dist_to_ball * sin(radians(angle))
            self.rect.center = (int(self.x), int(self.y))
            screen.blit(self.image, self.rect)

def calc_distance(a, b):
        return ((a.x - b.x)**2 + (a.y - b.y)**2)**(0.5)

def ball_collided(ball1, ball2):
        distance = calc_distance(ball1, ball2)
        if distance <= (ball1.radius + ball2.radius):
            return True
        else:
            return False

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
            distance = calc_distance(ball1, ball2)

class Button:

        def __init__(self, x, y, width, height, text, xoff=0, yoff=0):
            self.x = x
            self.y = y
            self.height = height
            self.width = width
            self.background = WHITE
            self.text = text
            self.x_offset = xoff
            self.y_offset = yoff

        def draw(self, surface):
            pygame.draw.ellipse(surface, self.background, [self.x, self.y, self.width, self.height], 0)
            text = font.render(self.text, True, BLACK)     
            surface.blit(text, (self.x + self.x_offset, self.y + self.y_offset))
        
        def click_handle(self):
            pos = pygame.mouse.get_pos()
            if pos[0] > self.x and pos[1] > self.y and pos[0] < (self.x + self.width) and pos[1] < (self.y + self.height):
                return True
            else:
                return False

class Label:
    
        def __init__(self, x, y, text=""):
            self.x = x
            self.y = y
            self.text = text
        
        def show(self, surface, text): 
            tmp = font.render(text, True, BLACK)     
            surface.blit(tmp, (self.x, self.y))

conn = None
client_socket = None


def host():
    # get the hostname
    host = socket.gethostname()
    port = 5000  # initiate port no above 1024

    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(2)
    global conn
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address))

def client():
    host = socket.gethostname()  # as both code is running on same pc
    port = 5000  # socket server port number
    global client_socket
    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server


# Initialize pygame and sets screen size and caption
pygame.init()
# Font to use in the entire game
font = pygame.font.Font('freesansbold.ttf', 10)
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
pygame.display.set_caption("8 Ball Pool by Raul Vieira")

game = Game()
btn_host = Button(30, 450, 60, 50, "Host", 10, 20)
btn_connect = Button(100, 450, 60, 50, "Connect", 10, 20)
btn_host.background = GREEN
btn_connect.background = GREEN
server = Network()
lbl_player = Label(200, 470, "")

clock = pygame.time.Clock()
connected = False
hosting = False

# Main loop
while True:
    screen.fill(WHITE)
    screen.blit(background_img, (0, 0))
    for event in pygame.event.get():
        # Closes the game if user clicked the X
        if event.type == pygame.QUIT:  
            pygame.quit()
            if hosting:
                conn.close()
            else:
                client_socket.disconnect()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not game.has_movement(game.balls) and event.button == LEFT_CLICK:
                game.stick.is_charging = True
            if btn_host.click_handle():
                print("Button Host Click")
                host()
                hosting = True
            if btn_connect.click_handle():
                print("Button Connect Click")
                client()
                connected = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if not game.has_movement(game.balls) and event.button == LEFT_CLICK:
                game.stick.is_charging = False
                game.stick.hit = True
                game.stick.hit_force = (game.stick.dist_to_ball - 180) * 0.25
            if not game.has_movement(game.balls) and event.button == RIGHT_CLICK:
                game.stick.dist_to_ball = 180
    for ball in game.balls:
        ball.move()
    for put in game.puts:
        put.draw()
        put.check_put(game.balls, game.balls_put_even, game.balls_put_odd)
    if not connected:
        game.check_collisions()
    game.draw_balls_put()
    game.stick.set_angle(game.balls[0])
    if not game.has_movement(game.balls):
        game.stick.update(game.balls)
        game.set_player_ball()
    btn_host.draw(screen)
    btn_connect.draw(screen)
    if game.p1 == EVEN:
        ball_type = "EVEN"
    elif game.p1 == ODD:
        ball_type = "ODD"
    else:
        ball_type = "ANY"
    text = "Player {} Turn ({})".format(game.turn, ball_type)
    lbl_player.show(screen, text)
    if connected:
        try:
            data = client_socket.recv(4096)
            if data:
                balls_host, balls_host_even, balls_host_odd = pickle.loads(data)
                # for ball, ball_remote in zip(game.balls, balls_host):
                #     ball.x = ball_remote.x
                #     ball.y = ball_remote.y
                game.balls = balls_host.copy()
                game.balls_put_even = balls_host_even.copy()
                game.balls_put_odd = balls_host_odd.copy()
        except Exception as e:
            print(e)
    if hosting:
        data = pickle.dumps((game.balls, game.balls_put_even, game.balls_put_odd))
        conn.send(data)  # send data to the client
    

    clock.tick(60)
    # Update the screen
    pygame.display.flip()