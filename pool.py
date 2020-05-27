import pygame
import pygame.gfxdraw
import sys
from math import cos, sin, radians, degrees, atan2
from cmath import polar
import socket
import pickle
import constants as c
from random import randint


class Game:

    def __init__(self):
        self.balls = []
        self.balls_put_even = []
        self.balls_put_odd = []
        self.balls.append(self.Ball((600, 220)))
        for x in range(15):
            self.balls.append(self.Ball(c.BALLS_POS[x]))
            self.balls[x+1].color = c.COLORS[x]
            self.balls[x+1].number = x+1
        self.stick = self.Stick()
        self.puts = []
        self.puts.append(self.Put(32, 36))
        self.puts.append(self.Put(398, 24))
        self.puts.append(self.Put(765, 36))
        self.puts.append(self.Put(32, 408))
        self.puts.append(self.Put(398, 420))
        self.puts.append(self.Put(765, 408))
        self.turn = c.PLAYER1
        self.must_put = c.ANY
        self.first_put = False
        self.after_hit = False
        self.even_on_put = 0
        self.odd_on_put = 0

    def draw(self):
        for ball in self.balls:
            ball.move()
            ball.draw()
        for put in self.puts:
            put.draw()
            put.check_put(game)
        if not self.has_movement(self.balls):
            self.stick.draw(self.balls)

    def check_victory(self):
        is_15_ingame = False
        for ball in self.balls:
            if ball.number == 15:
                is_15_ingame = True
        if len(self.balls_put_even) == 7 and not is_15_ingame:
            if game.turn == c.PLAYER1:
                return c.PLAYER1
            else:
                return c.PLAYER2
        elif len(self.balls_put_odd) == 8:
            if game.turn == c.PLAYER1:
                return c.PLAYER1
            else:
                return c.PLAYER2
        elif (not is_15_ingame) and len(self.balls_put_even) < 7 and len(self.balls_put_odd) < 8:
            if game.turn == c.PLAYER1:
                return c.PLAYER2
            else:
                return c.PLAYER1
        return False
    
    def click_handle(self, event):
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.has_movement(self.balls) and event.button == c.LEFT_CLICK:
                self.stick.is_charging = True
                

        elif event.type == pygame.MOUSEBUTTONUP:
            if not game.has_movement(game.balls) and event.button == c.LEFT_CLICK:
                self.stick.is_charging = False
                self.stick.hit = True
                self.stick.hit_force = (game.stick.dist_to_ball - 180) * 0.25
            if not game.has_movement(game.balls) and event.button == c.RIGHT_CLICK:
                self.stick.dist_to_ball = 180

    def toggle_turn(self):
        if self.turn == c.PLAYER1:
            self.turn = c.PLAYER2
        else:
            self.turn = c.PLAYER1
        if self.must_put == c.EVEN:
            self.must_put = c.ODD
        elif self.must_put == c.ODD:
            self.must_put = c.EVEN

    def set_player_ball(self):
        if not self.first_put:
            if self.balls_put_even:
                self.must_put = c.EVEN
                self.first_put = True
                
            if self.balls_put_odd:
                self.must_put = c.ODD
                self.first_put = True

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
                    x = randint(1, 3)
                    if x==1:
                        hit_sound1.play()
                        print("Sound 1")
                    elif x==2:
                        hit_sound2.play()
                        print("Sound 2")
                    else:
                        hit_sound3.play()
                        print("Sound 3")
                    a.collided = True
                    b.collided = True

                    p1 = complex(a.x, a.y)
                    v1 = complex(a.velocity*cos(radians(a.angle)), a.velocity*sin(radians(a.angle)))
                    p2 = complex(b.x, b.y)
                    v2 = complex(b.velocity*cos(radians(b.angle)), b.velocity*sin(radians(b.angle)))
                    p12 = p1 - p2
                    d = ((v1 - v2) / p12).real * p12

                    pa = v1 - d
                    polar_a = polar(pa)
                    a.velocity = polar_a[0]
                    a.angle = degrees(polar_a[1])

                    pb = v2 + d
                    polar_b = polar(pb)
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
            self.color = c.WHITE
            self.collided = False
            self.number = number

        def set_force_angle(self, force, angle):
            self.velocity = force
            self.angle = angle

        def draw(self):
            #pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, self.color)
            pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, self.color)
            text = font.render(str(self.number), True, c.WHITE)
            xoff = 5
            yoff = 4
            if self.number < 10:
                xoff = 2
            if self.number != 0:
                screen.blit(text, (int(self.x) - xoff, int(self.y) - yoff))

        def move(self):
            self.x = self.x + self.velocity*cos(radians(self.angle))
            self.y = self.y + self.velocity*sin(radians(self.angle))
            if self.x > (c.WIDTH - c.MARGIN_RIGHT) - self.radius:
                self.x = (c.WIDTH - c.MARGIN_RIGHT) - self.radius
                self.angle = 180 - self.angle
            if self.x < self.radius + c.MARGIN_LEFT:
                self.x = self.radius + c.MARGIN_LEFT
                self.angle = 180 - self.angle
            if self.y > c.HEIGHT - c.MARGIN_BOTTOM - self.radius - c.MENU_HEIGHT:
                self.y = c.HEIGHT - c.MARGIN_BOTTOM - self.radius - c.MENU_HEIGHT
                self.angle = 360 - self.angle
            if self.y < self.radius + c.MARGIN_TOP:
                self.y = self.radius + c.MARGIN_TOP
                self.angle = 360 - self.angle

            self.velocity -= self.friction
            if self.velocity < 0:
                self.velocity = 0
        
        def draw_after_put(self, x, y):
            self.x = x
            self.y = y
            pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, self.color)
            pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, self.color)
            text = font.render(str(self.number), True, c.WHITE)
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
            self.color = c.WHITE
            self.radius = r
            
        def draw(self):
            #pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, self.color)
            #pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, self.color)
            pass
        
        def check_put(self, game):
            if not menu.is_connected:
                for ball in game.balls:
                    distance = calc_distance(ball, self)
                    if distance < self.radius:
                        if ball == game.balls[0]:
                            ball.x = -200
                            ball.y = -200
                            ball.velocity = 0
                            game.toggle_turn()
                            game.after_hit = False
                            game.even_on_put = len(game.balls_put_even)
                            game.odd_on_put = len(game.balls_put_odd)
                        else:
                            game.balls.remove(ball)
                            pocket_sound.play()
                            if ball.number % 2 == 0:
                                game.balls_put_even.append(ball)
                            else:
                                game.balls_put_odd.append(ball)
                if game.after_hit and not game.has_movement(game.balls):
                    game.after_hit = False
                    if (game.even_on_put == len(game.balls_put_even) and
                        game.odd_on_put == len(game.balls_put_odd)):
                        game.toggle_turn()
                    elif game.must_put == c.EVEN and game.odd_on_put < len(game.balls_put_odd):
                        game.toggle_turn()
                    elif game.must_put == c.ODD and game.even_on_put < len(game.balls_put_even):
                        game.toggle_turn()
                    game.even_on_put = len(game.balls_put_even)
                    game.odd_on_put = len(game.balls_put_odd)
               


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
            self.remote_hit = False

        def set_angle(self, ball_obj, pos=(-100, -100)):
            if pos[0] == -100:
                position = pygame.mouse.get_pos()
            else:
                position = pos
            
            self.x = position[0]
            self.y = position[1]
            self.angle = degrees(atan2(ball_obj.y - self.y ,  ball_obj.x - self.x))

        def draw(self, balls):
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
                if not menu.is_hosting or game.turn == c.PLAYER1:
                    balls[0].set_force_angle(self.hit_force, self.angle)
                    hit_cue_sound.play()
                    game.after_hit = True
                if menu.is_connected and game.turn == c.PLAYER2:
                    self.remote_hit = True
                
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
            self.background = c.WHITE
            self.text = text
            self.x_offset = xoff
            self.y_offset = yoff

        def draw(self, surface):
            pygame.draw.rect(surface, self.background, [self.x, self.y, self.width, self.height], 0)
            pygame.draw.rect(surface, c.BLACK, [self.x, self.y, self.width, self.height], 1)
            text = font.render(self.text, True, c.BLACK)     
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
        
        def show(self, surface, text, ): 
            tmp = font_medium.render(text, True, c.BLACK)     
            surface.blit(tmp, (self.x, self.y))


class Menu:
    
    def __init__(self):
        self.btn_host = Button(30, 450, 60, 40, "Host", 18, 15)
        self.btn_connect = Button(100, 450, 60, 40, "Connect", 10, 15)
        self.btn_host.background = c.GREEN
        self.is_hosting = False
        self.btn_connect.background = c.GREEN
        self.is_connected = False
        self.lbl_player = Label(200, 460, "")
        self.won = 0

    def draw(self, game):
        self.btn_host.draw(screen)
        self.btn_connect.draw(screen)
        winner = False
        text = ""
        if game.must_put == c.EVEN:
            ball_type = "EVEN"
        elif game.must_put == c.ODD:
            ball_type = "ODD"
        else:
            ball_type = "ANY"
        if not self.won:
            text = "Player {} Turn ({})".format(game.turn, ball_type)
            self.won = game.check_victory()
        if self.won:
            text = "Player {} won the game!".format(self.won)
        self.lbl_player.show(screen, text)

    def click_handle(self):
        if self.btn_host.click_handle():
            print("Button Host Click")
            self.is_hosting = True
            self.btn_host.background = c.RED
            host()
        if self.btn_connect.click_handle():
            print("Button Connect Click")
            self.is_connected = True
            self.btn_connect.background = c.RED
            client()

def host():
    # get the hostname
    host = socket.gethostname()
    port = PORT
    SERVER_IP = socket.gethostbyname(host)

    server_socket = socket.socket()  
    server_socket.bind((host, port))
    print("Server on IP: {} and PORT: {}".format(SERVER_IP, port))

    # configure how many client the server can listen simultaneously
    server_socket.listen(2)
    global conn
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))

def client():
    host = IP
    port = PORT
    global client_socket
    client_socket = socket.socket() 
    client_socket.connect((host, port))


background_img = pygame.image.load(r"table.png")
stick_img = pygame.image.load(r"stick.png")


f = open("ip_port_to_connect.txt", "r")
IP, PORT = f.read().splitlines()
PORT = int(PORT)
f.close()
print(IP)
print(PORT)

conn = None
client_socket = None
pygame.init()
font = pygame.font.Font('freesansbold.ttf', 10)
font_medium = pygame.font.Font('freesansbold.ttf', 16)
screen = pygame.display.set_mode((c.WIDTH, c.HEIGHT))
pygame.display.set_caption("Pool Billiards by Raul Vieira")
hit_sound1 = pygame.mixer.Sound(r"hit1.wav")
hit_sound2 = pygame.mixer.Sound(r"hit2.wav")
hit_sound3 = pygame.mixer.Sound(r"hit3.wav")
pocket_sound = pygame.mixer.Sound(r"pocket.wav")
hit_cue_sound = pygame.mixer.Sound(r"hit_cue.wav")

game = Game()
menu = Menu()


clock = pygame.time.Clock()

# Main loop
while True:
    screen.fill(c.WHITE)
    screen.blit(background_img, (0, 0))
    for event in pygame.event.get():
        if not menu.won:
            game.click_handle(event)
        if event.type == pygame.QUIT:  
            pygame.quit()
            if menu.is_hosting:
                conn.close()
            elif menu.is_connected:
                client_socket.disconnect()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            menu.click_handle()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game = Game()
        
    
    game.set_player_ball()
    
    if not menu.is_connected:
        game.check_collisions()
    game.draw_balls_put()
    if (not menu.is_connected and not menu.is_hosting) or (menu.is_hosting and game.turn == c.PLAYER1) or (menu.is_connected and game.turn == c.PLAYER2):
        game.stick.set_angle(game.balls[0])
    
    game.draw()
    menu.draw(game)
    if menu.is_connected:
        try:
            data = client_socket.recv(4096)
            if data:
                #mouse_pos = pygame.mouse.get_pos()
                balls_host, balls_host_even, balls_host_odd, mouse_pos, turn, put_type = pickle.loads(data)
                # for ball, ball_remote in zip(game.balls, balls_host):
                #     ball.x = ball_remote.x
                #     ball.y = ball_remote.y
                game.balls = balls_host.copy()
                game.balls_put_even = balls_host_even.copy()
                game.balls_put_odd = balls_host_odd.copy()
                if game.turn == c.PLAYER1:
                    game.stick.set_angle(game.balls[0], mouse_pos)
                game.turn = turn
                game.must_put = put_type

                force, angle = 0, 0
                if game.stick.remote_hit:
                    game.stick.remote_hit = False
                    force = game.stick.hit_force
                    angle = game.stick.angle
                mouse_pos = pygame.mouse.get_pos()
                data = pickle.dumps((force, angle, mouse_pos))
                client_socket.send(data)

        except Exception as e:
            print(e)
    if menu.is_hosting:
        mouse_pos = pygame.mouse.get_pos()
        data = pickle.dumps((game.balls, game.balls_put_even, game.balls_put_odd, mouse_pos, game.turn, game.must_put))
        if game.turn == c.PLAYER2:
            pass

        conn.send(data)
        try: 
            data = conn.recv(4096)
            if data:
                force, angle, mouse_pos = pickle.loads(data)
                if force:
                    game.balls[0].set_force_angle(force, angle)
                    hit_cue_sound.play()
                    game.stick.hit = False
                    game.after_hit = True
                if game.turn == c.PLAYER2:
                    game.stick.set_angle(game.balls[0], mouse_pos)
        except Exception as e:
            print(e)
    

    clock.tick(60)
    # Update the screen
    pygame.display.flip()