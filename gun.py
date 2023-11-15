import math
from random import choice
from random import randint
from random import random

import pygame


FPS = 30

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

WIDTH = 800
HEIGHT = 600

# ускорение свободного падения 1000 pix/sec
ACC = 30 / FPS

# коэффициент восстановления
REC = 0.6

#коэффициент трения
K = 0.2

# отступы стен от краев

DY = 50
DX = 20

SCORE = 0

#описательная часть кода

def draw_heart(screen, x, y, s, color = RED):
    pygame.draw.polygon(
    screen, 
    color, 
    [[x, y], [x + s, y - s], [x + 2*s, y], [x, y + 2*s], [x - 2*s, y], [x - s, y - s]])

def sign(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    return -1

def speed_loss(vn, vt):
    """
    Функция выдает новые значения скоростей после неупругого удара.
    Порядок: нормальная, тангенсальная
    """
    if vt == 0:
        if abs(vn) < 5:
            return(0, 0)
        vn_new = -vn * REC
        return(vn_new, 0)
    new_vn = -REC * vn
    delta_vt = K*(1 + REC)*abs(vn)
    if delta_vt > abs(vt):
        return(new_vn, 0)
    return(new_vn, sign(vt)*(abs(vt) - delta_vt))

def decision(probability):
    return random() < probability

def draw_score():
    global SCORE
    """
    отрисовка счета
    """
    myfont = pygame.font.Font(None, 32)
    points = myfont.render(f'Score: {str(SCORE)}', 1, BLACK)
    screen.blit(points, (30, 30))


class Ball:
    def __init__(self, screen: pygame.Surface, x=40, y=450):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 8
        self.vx = 0
        self.vy = 0
        self.color = choice(GAME_COLORS)
        self.live = FPS

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        self.x += self.vx
        self.y += self.vy

        # мяч не должен пробивать стены

        if self.y + self.r > HEIGHT - DY:
            self.y = HEIGHT - DY - self.r

        if self.x + self.r > WIDTH - DX:
            self.x = WIDTH - DX - self.r

        if self.x - self.r < DX:
            self.x = DX + self.r
        
        # ускорение

        self.vy += ACC

        # отражение от правой стенки
        if self.r + self.x >= WIDTH - DX:
            self.vx, self.vy = speed_loss(self.vx, self.vy)

        #отражение от нижней стенки
        
        if self.r + self.y >= HEIGHT - DY:
            self.vy, self.vx = speed_loss(self.vy, self.vx) 

        #отражение от левой стенки
        if self.x - self.r <= DX:
            self.vx, self.vy = speed_loss(self.vx, self.vy)

    def draw(self):
        """
        метод рисует шарик
        """
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )
        # edge
        pygame.draw.circle(
            self.screen,
            BLACK,
            (self.x, self.y),
            self.r,
            2
        )

    def do_live(self):
        """
        метод проверяет, нужно ли продолжать отрисовывать шарик. 
        если он лежит на земле без движения больше секунды, то отрисовывать его больше не надо
        """
        if self.y == HEIGHT - 50 - self.r and self.vx == 0 and self.vy == 0:
            if self.live == 0:
                return False
            else:
                self.live -= 1
                return True
        else:
            return True

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        dist = ((self.x - obj.x)**2 + (self.y - obj.y)**2)**0.5 
        if dist <= self.r + obj.r:
            return True
        return False


class Gun:
    def __init__(self, screen, x = 40, y = HEIGHT - 50, width = 7):
        self.screen = screen
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = GREY
        self.x = x
        self.y = y
        self.width = width
        self.r = 20

        self.tank_w = 30
        self.tank_h = 15
        self.speed = 10

        self.y -= self.tank_h / 2

        self.live = 10

    def fire2_start(self, event):
        """
        метод делает пушку активной
        """
        self.f2_on = 1

    def fire2_end(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen, x = self.x, y = self.y)
        new_ball.r += 5
        self.an = math.atan2((event.pos[1]-new_ball.y), (event.pos[0]-new_ball.x))
        new_ball.vx =  self.f2_power / 2 * math.cos(self.an)
        new_ball.vy =  self.f2_power / 2 * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event):
        """
        Прицеливание. Зависит от положения мыши.
        """

        if event:
            if event.pos[0] == self.x:
                self.an = - sign (event.pos[1]-self.y) *math.pi / 2
            elif event.pos[0] < self.x:
                self.an = math.pi + math.atan(-(event.pos[1]-self.y) / (event.pos[0]-self.x))
            else:
                self.an = math.atan(-(event.pos[1]-self.y) / (event.pos[0]-self.x))
        if self.f2_on:
            self.color = RED
        else:
            self.color = GREY

    def draw(self):

        """
        Рисует пушку, направленную к курсору
        """
    
        # координаты углов

        x = self.x
        y = self.y
        w = self.width
        h = self.f2_power + 10
        angle_rad = self.an 

        top_left_x = x - w / 2 * math.sin(angle_rad)
        top_left_y = y - w / 2 * math.cos(angle_rad)

        top_right_x = x - w / 2 * math.sin(angle_rad) + h * math.cos(angle_rad)
        top_right_y = y - w / 2 * math.cos(angle_rad) - h * math.sin(angle_rad)

        bottom_left_x = x + w / 2 * math.sin(angle_rad)
        bottom_left_y = y + w / 2 * math.cos(angle_rad)

        bottom_right_x = x + w / 2 * math.sin(angle_rad) + h * math.cos(angle_rad)
        bottom_right_y = y + w / 2 * math.cos(angle_rad) - h * math.sin(angle_rad)

        pygame.draw.polygon(self.screen, self.color, [
            (top_left_x, top_left_y),
            (top_right_x, top_right_y),
            (bottom_right_x, bottom_right_y),
            (bottom_left_x, bottom_left_y)
        ])


        rect = pygame.Rect(self.x - self.tank_w / 2, self.y - self.tank_h / 2, self.tank_w, self.tank_h)
        pygame.draw.rect(self.screen, self.color, rect, width=0, border_radius=3)
     
    def draw_lifes(self):
        """
        отрисовывает количество жизней пушки
        """
        size = 5
        x = 40
        y = 65
        for i in range(self.live):
            draw_heart(self.screen, x + i * size * 5, y, size)

    def hit(self):
        self.live -= 1

    def power_up(self):
        """
        Метод усиливает пушку
        """
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            self.color = RED
        else:
            self.color = GREY

    def move(self, direction):
        """
        Движение пушки
        -1 - влево, 1 - вправо, 0 - никуда
        """
        self.x += direction*self.speed

        if self.x <=  DX + self.tank_w / 2:
            self.x = DX + self.tank_w / 2
        if self.x >=  WIDTH - (DX + self.tank_w / 2):
            self.x = WIDTH - (DX + self.tank_w / 2)

class Shot(Ball):
    def __init__(self, screen: pygame.Surface, x=40, y=450):
        super().__init__(screen, x, y)
        self.r = 7
        self.color = BLACK
    def move(self):
        self.x += self.vx
        self.y += self.vy

        # вражеская пуля пропадает после удара о землю

        if self.y + self.r >= HEIGHT - DY:
            self.live = 0

        if self.x + self.r >= WIDTH - DX:
            self.live = 0
        
        if self.x - self.r <= DX:
            self.live = 0
        
        # ускорение

        self.vy += ACC

        
class Target:
    """
    мишень, двигающаяся по горизонтали
    """
    def __init__(self, screen):
        self.screen = screen
        self.color = GREY
        self.points = 0
        self.live = 1
        

        max_r = 20
        min_r = 10
        self.r = randint(min_r, max_r)
        self.x = randint(self.r + DX, WIDTH - self.r - DX)
        self.y = randint(self.r + DY + 100, self.r + DY + 400)

        self.v = 10

    def new_target(self):
        """ Инициализация новой цели. """
        max_r = 20
        min_r = 10
        self.r = randint(min_r, max_r)
        self.x = randint(self.r + DX, WIDTH - self.r - DX)
        self.y = randint(self.r + DY + 100, self.r + DY + 400)

        self.live = 1

    def hit(self):
        """Попадание шарика в цель."""
        global SCORE
        SCORE += 1


    def draw(self):
        """
        отрисовка мишени
        """
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )
        # edge
        pygame.draw.circle(
            self.screen,
            BLACK,
            (self.x, self.y),
            self.r,
            2
        )

    def move(self):
        self.x += self.v

        if self.x > WIDTH - DX - self.r:
            self.v = -self.v
            #self.x = self.x - (WIDTH - DX - self.r)
        if self.x < DX + self.r:
            self.v = -self.v

class NonHorTarget(Target):
    """
        мишень движется во всем пространстве экрана, отражаясь от стенок
    """
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        v_max = 10
        self.vx = randint(-v_max, v_max)
        self.vy = randint(-v_max, v_max)

    def new_target(self):
        """ Инициализация новой цели. """
        max_r = 20
        min_r = 10
        self.r = randint(min_r, max_r)
        self.x = randint(self.r + DX, WIDTH - self.r - DX)
        self.y = randint(self.r + DY + 100, self.r + DY + 400)

        v_max = 10
        self.vx = randint(-v_max, v_max)
        self.vy = randint(-v_max, v_max)

        self.live = 1

    def move(self):
        self.x += self.vx
        self.y += self.vy

        ceil = 50
        # мишень не должна пробивать стены

        if self.y + self.r > HEIGHT - DY - ceil:
            self.y = HEIGHT - DY - self.r - ceil

        if self.x + self.r > WIDTH - DX:
            self.x = WIDTH - DX - self.r

        if self.x - self.r < DX:
            self.x = DX + self.r
        
        if self.y - self.r < DY + ceil:
            self.y = DY + self.r + ceil
        

        # отражение от правой и левой стенок
        if self.r + self.x >= WIDTH - DX or self.x - self.r <= DX:
            self.vx = -self.vx

        #отражение от нижней и верхней стенок
        
        if self.r + self.y >= HEIGHT - DY - ceil or self.y - self.r <= DY + ceil:
            self.vy = -self.vy


class KillTarget():

    """
    мишень гоняется за танком и в рандомные моменты времени выстреливает по ходу своего движения
    """

    def __init__(self, screen):
        self.screen = screen
        self.color = BLACK
        self.live = 5
        self.r = 10
        self.vx = 0

        self.hitted = 0
        self.ball_hit = 0
        

        self.length = 40
        self.width = 10
        self.x = randint(self.length / 2 + DX, WIDTH - self.length / 2 - DX)
        self.y = randint(self.width / 2 + DY + 50, self.width / 2 + DY + 200)

        self.v = 3

    def new_target(self):
        """ Инициализация новой цели. """

        self.x = randint(self.length / 2 + DX, WIDTH - self.length / 2 - DX)
        self.y = randint(self.width / 2 + DY + 50, self.width / 2 + DY + 200)

        self.live = 5

    def not_hit(self, ball_id):
        if self.ball_hit == ball_id:
            self.hitted = 0
            self.color = BLACK

    def hit(self, ball_id):
        """Попадание шарика в цель."""
        global SCORE
        if self.hitted:
            return False
        else:
            self.hitted = 1
            self.ball_hit = ball_id
            self.color = RED
            if self.live > 1:
                self.live -= 1
                return False
            else:
                SCORE += 5
                return True


    def draw(self):
        """
        отрисовка мишени
        """
        pygame.draw.line(
            self.screen,
            self.color,
            [self.x - self.length / 2, self.y],
            [self.x + self.length / 2, self.y],
            width = self.width
        )

        pygame.draw.line(
            self.screen,
            self.color,
            [self.x, self.y],
            [self.x, self.y + self.length / 2],
            width = self.width
        )

        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

        myfont = pygame.font.Font(None, 32)
        lifes = myfont.render(str(self.live), 1, BLACK)
        screen.blit(lifes, lifes.get_rect(center = (self.x, self.y - 20)))

    def move(self, obj):
        self.vx = (obj.x - self.x) * self.v / 100
        self.x += self.vx

    def shoot(self):
        if self.vx < 3:
            prob = 1/2/FPS
        else:
            prob = 2/FPS
        if decision(1/FPS):
            global shots
            if abs(self.vx) > 3:
                new_shot = Shot(self.screen, x = self.x + sign(self.vx) * self.length / 2, y = self.y)
            else:
                new_shot = Shot(self.screen, x = self.x, y = self.y + self.length / 2)
            new_shot.vx =  self.vx *2
            new_shot.vy =  0
            shots.append(new_shot)
        


#исполнительная часть кода

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    bullet = 0
    balls = []
    shots = []

    clock = pygame.time.Clock()
    gun = Gun(screen)
    target1 = Target(screen)
    target2 = NonHorTarget(screen)
    killtarget = KillTarget(screen)
    finished = False

    while not finished:

        #отрисовка кадра

        screen.fill(WHITE)
        gun.draw()
        gun.draw_lifes()

        target1.draw()
        target2.draw()
        killtarget.draw()

        draw_score()
        for b in balls:
            if b.do_live():
                b.draw()
        for s in shots:
            if s.live:
                s.draw()

        target1.move()
        target2.move()
        killtarget.move(gun)
        pygame.display.update()

        clock.tick(FPS)

        #проверка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                gun.fire2_start(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                gun.fire2_end(event)
                gun.targetting(event)
            elif event.type == pygame.MOUSEMOTION:
                gun.targetting(event)

        # проверка клавиш

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            gun.move(1)
        elif keys[pygame.K_a]:
            gun.move(-1)
        else:
            gun.move(0)
    

        #движение шаров и проверка попадания в цель 
        for b in balls:
            b.move()

            if b.hittest(target1) and target1.live:
                target1.live = 0
                target1.hit()
                target1.new_target()
            if b.hittest(target2) and target2.live:
                target2.live = 0
                target2.hit()
                target2.new_target()
            
            if b.hittest(killtarget):
                if killtarget.hit(id(b)):
                    killtarget.new_target()
            else:
                killtarget.not_hit(id(b))
            """
                #отрисовка экрана победы n секунд
                n = 3
                for i in range(n*FPS):
                    screen.fill(WHITE)
                    gun.draw()
                    target1.draw_score()
                    myfont = pygame.font.Font(None, 32)
                    if len(balls) == 1:
                        points = myfont.render(f'You hit the target in 1 shot', 1, BLACK)
                    else:
                        points = myfont.render(f'You hit the target in {len(balls)} shots', 1, BLACK)
                    screen.blit(points, (WIDTH / 2 - points.get_width() / 2, HEIGHT / 2 - points.get_height() / 2))
                    for b in balls:
                        if b.do_live():
                            b.draw()
                    pygame.display.update()

                    clock.tick(FPS)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            finished = True
                        elif event.type == pygame.MOUSEMOTION:
                            gun.targetting(event)

                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_d]:
                        gun.move(1)
                    elif keys[pygame.K_a]:
                        gun.move(-1)
                    else:
                        gun.move(0)
                    for b in balls:
                        b.move()
                    if finished:
                        break
                balls = []
            """
        for s in shots:
            s.move()
            if s.hittest(gun):
                gun.hit()
                print(gun.live)
        gun.power_up()
        killtarget.shoot()


    pygame.quit()
