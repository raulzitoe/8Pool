import sys
import socket
import pickle
from math import cos, sin, radians, degrees, atan2
from random import randint
from cmath import polar
import pygame
import pygame.gfxdraw
import constants as c


class Game:
    
    # Initializes all variables for the game - some use the classes Pocket, Ball and Menu
    def __init__(self):
        self.balls = []
        self.balls_pocket_even = []
        self.balls_pocket_odd = []
        self.balls.append(Ball((600, 220)))
        for x in range(15):
            self.balls.append(Ball(c.BALLS_POS[x]))
            self.balls[x+1].color = c.COLORS[x]
            self.balls[x+1].number = x+1
        self.stick = Stick()
        self.pockets = []
        self.pockets.append(Pocket(32, 36))
        self.pockets.append(Pocket(398, 24))
        self.pockets.append(Pocket(765, 36))
        self.pockets.append(Pocket(32, 408))
        self.pockets.append(Pocket(398, 420))
        self.pockets.append(Pocket(765, 408))
        self.turn = c.PLAYER1
        self.must_pocket = c.ANY
        self.first_pocket = False
        self.after_hit = False
        self.even_on_pocket = 0
        self.odd_on_pocket = 0
        self.menu = Menu()
        self.won = False
        self.sound_effect_count = 0
        self.cue_on_pocket = False
        self.sounds_end = False

    # Draw the background, balls, pockets and stick on the screen
    def draw(self):
        for ball in self.balls:
            ball.move()
            ball.draw()
        for pocket in self.pockets:
            pocket.draw()
            self.check_pocket(pocket)
        if not self.has_movement(self.balls):
            self.stick.draw(self.balls)
        self.menu.draw(self.must_pocket, self.won)

    # Check if a ball entered the pocket and moves the ball to a different list
    # Toggles the player turn if the wrong has sunk
    def check_pocket(self, pocket):
        if not self.menu.is_connected:
            for ball in self.balls:
                distance = calc_distance(ball, pocket)
                if distance < pocket.radius:
                    if ball == self.balls[0]:
                        ball.x = -200
                        ball.y = -200
                        ball.velocity = 0
                        self.toggle_turn()
                        self.after_hit = False
                        self.even_on_pocket = len(self.balls_pocket_even)
                        self.odd_on_pocket = len(self.balls_pocket_odd)
                        self.cue_on_pocket = True
                    else:
                        self.balls.remove(ball)
                        if ball.number % 2 == 0:
                            self.balls_pocket_even.append(ball)
                        else:
                            self.balls_pocket_odd.append(ball)
            if self.after_hit and not self.has_movement(self.balls):
                self.after_hit = False
                if (self.even_on_pocket == len(self.balls_pocket_even) and
                    self.odd_on_pocket == len(self.balls_pocket_odd)):
                    self.toggle_turn()
                elif self.must_pocket == c.EVEN and self.odd_on_pocket < len(self.balls_pocket_odd):
                    self.toggle_turn()
                elif self.must_pocket == c.ODD and self.even_on_pocket < len(self.balls_pocket_even):
                    self.toggle_turn()
                self.even_on_pocket = len(self.balls_pocket_even)
                self.odd_on_pocket = len(self.balls_pocket_odd)
    
    # Check the winning conditions
    # You must pocket all 7 balls (ODD or EVEN) then ball 15
    # Ball 15 must be the last ball or you lose
    def check_victory(self):
        is_15_ingame = False
        for ball in self.balls:
            if ball.number == 15:
                is_15_ingame = True
        if len(self.balls_pocket_even) == 7 and not is_15_ingame:
            self.won = True
            if self.turn == c.PLAYER1:
                return c.PLAYER1
            else:
                return c.PLAYER2
        elif len(self.balls_pocket_odd) == 8:
            self.won = True
            if self.turn == c.PLAYER1:
                return c.PLAYER1
            else:
                return c.PLAYER2
        elif (not is_15_ingame) and len(self.balls_pocket_even) < 7 and len(self.balls_pocket_odd) < 8:
            self.won = True
            if self.turn == c.PLAYER1:
                return c.PLAYER2
            else:
                return c.PLAYER1
        return False
    
    def click_handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.menu.click_handle()
            if not self.has_movement(self.balls) and event.button == c.LEFT_CLICK:
                self.stick.is_charging = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if not self.has_movement(self.balls) and event.button == c.LEFT_CLICK:
                self.stick.is_charging = False
                self.stick.hit = True
                self.stick.hit_force = (self.stick.dist_to_ball - 180) * 0.15
            if not self.has_movement(self.balls) and event.button == c.RIGHT_CLICK:
                self.stick.dist_to_ball = 180

    def toggle_turn(self):
        if self.turn == c.PLAYER1:
            self.turn = c.PLAYER2
        else:
            self.turn = c.PLAYER1
        if self.must_pocket == c.EVEN:
            self.must_pocket = c.ODD
        elif self.must_pocket == c.ODD:
            self.must_pocket = c.EVEN

    # After the first pocket sets if the player is gonna pocket EVEN or ODD balls
    def set_player_ball(self):
        if not self.first_pocket:
            if self.balls_pocket_even:
                self.must_pocket = c.EVEN
                self.first_pocket = True
                
            if self.balls_pocket_odd:
                self.must_pocket = c.ODD
                self.first_pocket = True

    # Checks for any ball movement
    # Reposition cue ball if it is out of bounds (was sunk)
    def has_movement(self, objs):
        for obj in objs:
            if obj.velocity > 0:
                return True
        if self.balls[0].x < 0:
            self.balls[0].x = 600
            self.balls[0].y = 220
        return False

    # Checks for any collision and defines the resulting velocity and angle for both balls
    def check_collisions(self):
        for a in self.balls:
            for b in self.balls:
                if a != b and ball_collided(a, b):          
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
    
    # Define the position and draw the pocketed balls at the bottom of the screen
    def draw_balls_pocket(self):
        x, y, i, j = 420, 455, 0, 0
        for ball in self.balls_pocket_even:
            ball.draw_after_pocket(x+i, y)
            i += 30
        for ball in self.balls_pocket_odd:
            ball.draw_after_pocket(x+j, y+25)
            j += 30
    
    # Function used to generate the sound effects even when the game is over the network
    # Still needs fixes for some cases when playing connected
    def sound_effects(self):
        for a in self.balls:
            for b in self.balls:
                if a != b and ball_collided(a, b):             
                    x = randint(1, 3)
                    if x==1:
                        hit_sound1.play()
                    elif x==2:
                        hit_sound2.play()
                    else:
                        hit_sound3.play()
            ignore = True if (a.x == -200 and a.y == -200) else False           
            if a.x == (c.WIDTH - c.MARGIN_RIGHT) - a.radius:
                hit_wall_sound.play()
            if a.x == a.radius + c.MARGIN_LEFT and not ignore:
                hit_wall_sound.play()
            if a.y == c.HEIGHT - c.MARGIN_BOTTOM - a.radius - c.MENU_HEIGHT:
                hit_wall_sound.play()
            if a.y == a.radius + c.MARGIN_TOP and not ignore:
                hit_wall_sound.play()
        if self.stick.hit and self.stick.dist_to_ball < 200:
            hit_cue_sound.play()
        if len(self.balls) + self.sound_effect_count < 16:
            pocket_sound.play()
            self.sound_effect_count += 1
        if self.cue_on_pocket:
            pocket_sound.play()
            self.cue_on_pocket = False
        if self.menu.winner and not self.sounds_end:
            self.sounds_end = True
            victory_sound.play()


class Ball:

    def __init__(self, pos=(50, 50), number=0):
        self.x = pos[0]
        self.y = pos[1]
        self.friction = 0.01 #was 0.02 with 60fps
        self.velocity = 0.0
        self.angle = 0
        self.radius = 10
        self.color = c.WHITE
        self.number = number

    # Used to set the force of the cue ball when the user hits it
    def set_force_angle(self, force, angle):
        self.velocity = force
        self.angle = angle

    # Used to draw each ball
    # Antialiased circle was used, you can change both gfxdraw functions to the first commented as needed
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

    # Moves the ball depending on its velocity
    # Changes the ball angle when it hits the walls
    def move(self):
        self.x = self.x + self.velocity*cos(radians(self.angle))
        self.y = self.y + self.velocity*sin(radians(self.angle))
        ignore = True if (self.x == -200 and self.y == -200) else False
        if self.x > (c.WIDTH - c.MARGIN_RIGHT) - self.radius:
            self.x = (c.WIDTH - c.MARGIN_RIGHT) - self.radius
            self.angle = 180 - self.angle
        if self.x < self.radius + c.MARGIN_LEFT and not ignore:
            self.x = self.radius + c.MARGIN_LEFT
            self.angle = 180 - self.angle
        if self.y > c.HEIGHT - c.MARGIN_BOTTOM - self.radius - c.MENU_HEIGHT:
            self.y = c.HEIGHT - c.MARGIN_BOTTOM - self.radius - c.MENU_HEIGHT
            self.angle = 360 - self.angle
        if self.y < self.radius + c.MARGIN_TOP and not ignore:
            self.y = self.radius + c.MARGIN_TOP
            self.angle = 360 - self.angle

        self.velocity -= self.friction
        if self.velocity < 0:
            self.velocity = 0
    
    # Used to draw individual balls that are pocketed
    def draw_after_pocket(self, x, y):
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


class Pocket():

    def __init__(self, x, y, r=16):
        self.x = x
        self.y = y
        self.color = c.WHITE
        self.radius = r

    # Uncomment both lines to make the pockets visible
    # Can help you reposition or resize the pockets over a new table image
    def draw(self):
        #pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, self.color)
        #pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, self.color)
        pass
                

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

    # Sets the angle of the stick over the cue ball based on the mouse position
    def set_angle(self, ball_obj, pos=(-100, -100)):
        if pos[0] == -100:
            position = pygame.mouse.get_pos()
        else:
            position = pos
        self.x = position[0]
        self.y = position[1]
        self.angle = degrees(atan2(ball_obj.y - self.y ,  ball_obj.x - self.x))

    # Draw the stick with a distance of the cue ball according to the charging conditions
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
            if not game.menu.is_hosting or game.turn == c.PLAYER1:
                balls[0].set_force_angle(self.hit_force, self.angle)
                game.after_hit = True
            if game.menu.is_connected and game.turn == c.PLAYER2:
                self.remote_hit = True

        # Helps rotate the image with less image distortion   
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

# Moves the ball a little to compensate overlapping problems because of large simulation step
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
        
        def draw(self, surface, text): 
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
        self.winner = 0

    def draw(self, must_pocket, won):
        self.btn_host.draw(screen)
        self.btn_connect.draw(screen)
        winner = False
        text = ""
        if must_pocket == c.EVEN:
            ball_type = "EVEN"
        elif must_pocket == c.ODD:
            ball_type = "ODD"
        else:
            ball_type = "ANY"
        if not self.winner:
            text = "Player {} Turn ({})".format(game.turn, ball_type)
            self.winner = game.check_victory()
        if self.winner:
            text = "Player {} won the game!".format(self.winner)
        self.lbl_player.draw(screen, text)

    def click_handle(self):
        if self.btn_host.click_handle():
            self.is_hosting = True
            self.btn_host.background = c.RED
            host()
        if self.btn_connect.click_handle():
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



pygame.init()
background_img = pygame.image.load('assets/table.png')
stick_img = pygame.image.load('assets/stick.png')
icon_img = pygame.image.load('assets/icon.png')
pygame.display.set_icon(icon_img)
f = open("ip_port_to_connect.txt", "r")
IP, PORT = f.read().splitlines()
PORT = int(PORT)
f.close()

conn = None
client_socket = None

font = pygame.font.Font('freesansbold.ttf', 10)
font_medium = pygame.font.Font('freesansbold.ttf', 16)
screen = pygame.display.set_mode((c.WIDTH, c.HEIGHT))
pygame.display.set_caption("Pool Billiards by Raul Vieira")
hit_sound1 = pygame.mixer.Sound(r"assets/hit1.wav")
hit_sound2 = pygame.mixer.Sound(r"assets/hit2.wav")
hit_sound3 = pygame.mixer.Sound(r"assets/hit3.wav")
pocket_sound = pygame.mixer.Sound(r"assets/pocket.wav")
hit_cue_sound = pygame.mixer.Sound(r"assets/hit_cue.wav")
hit_wall_sound = pygame.mixer.Sound(r"assets/wall_hit.wav")
victory_sound = pygame.mixer.Sound(r"assets/victory.wav")

game = Game()

clock = pygame.time.Clock()

# Main loop
while True:
    screen.fill(c.WHITE)
    screen.blit(background_img, (0, 0))
    for event in pygame.event.get():
        if not game.won:
            game.click_handle(event)
        if event.type == pygame.QUIT:  
            pygame.quit()
            if game.menu.is_hosting:
                conn.close()
            elif game.menu.is_connected:
                client_socket.disconnect()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                tmp_connected = game.menu.is_connected
                tmp_hosting = game.menu.is_hosting
                game = Game()
                game.menu.is_connected = tmp_connected
                game.menu.is_hosting = tmp_hosting
                if game.menu.is_connected:
                    game.menu.btn_connect.background = c.RED
                if game.menu.is_hosting:
                    game.menu.btn_host.background = c.RED
    game.set_player_ball()
    if not game.menu.is_connected:
        game.check_collisions()
    game.draw_balls_pocket()
    if (not game.menu.is_connected and not game.menu.is_hosting) or (game.menu.is_hosting and game.turn == c.PLAYER1) or (game.menu.is_connected and game.turn == c.PLAYER2):
        game.stick.set_angle(game.balls[0])
    game.draw()
    game.sound_effects()
    
    if game.menu.is_connected:
        try:
            data = client_socket.recv(4096)
            if data:
                balls_host, balls_host_even, balls_host_odd, mouse_pos, turn, pocket_type = pickle.loads(data)
                game.balls = balls_host.copy()
                game.balls_pocket_even = balls_host_even.copy()
                game.balls_pocket_odd = balls_host_odd.copy()
                if game.turn == c.PLAYER1:
                    game.stick.set_angle(game.balls[0], mouse_pos)
                game.turn = turn
                game.must_pocket = pocket_type
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

    if game.menu.is_hosting:
        mouse_pos = pygame.mouse.get_pos()
        data = pickle.dumps((game.balls, game.balls_pocket_even, game.balls_pocket_odd, mouse_pos, game.turn, game.must_pocket))
        conn.send(data)
        try: 
            data = conn.recv(4096)
            if data:
                force, angle, mouse_pos = pickle.loads(data)
                if force:
                    game.balls[0].set_force_angle(force, angle)
                    game.stick.hit = False
                    game.after_hit = True
                if game.turn == c.PLAYER2:
                    game.stick.set_angle(game.balls[0], mouse_pos)
        except Exception as e:
            print(e)
    clock.tick(120)
    # Update the screen
    pygame.display.flip()