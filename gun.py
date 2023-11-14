import math
from random import choice
from random import randint

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

#описательная часть кода

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
        self.r = 10
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

        if self.y + self.r > HEIGHT - 50:
            self.y = HEIGHT - 50 - self.r

        if self.x + self.r > WIDTH - 20:
            self.x = WIDTH - 20 - self.r
        
        # ускорение

        self.vy += ACC

        # отражение от правой стенки
        if self.r + self.x >= WIDTH - 20:
            self.vx, self.vy = speed_loss(self.vx, self.vy)

        #отражение от нижней стенки
        
        if self.r + self.y >= HEIGHT - 50:
            self.vy, self.vx = speed_loss(self.vy, self.vx)

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
    def __init__(self, screen, x = 40, y = 450, width = 7):
        self.screen = screen
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = GREY
        self.x = x
        self.y = y
        self.width = width

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
        new_ball = Ball(self.screen)
        new_ball.r += 5
        self.an = math.atan2((event.pos[1]-new_ball.y), (event.pos[0]-new_ball.x))
        new_ball.vx = self.f2_power / 2 * math.cos(self.an)
        new_ball.vy = self.f2_power / 2 * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            if event.pos[0] <= 20:
                self.an = - sign (event.pos[1]-450) *math.pi / 2
            else:
                self.an = math.atan(-(event.pos[1]-450) / (event.pos[0]-20))
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


class Target:
    
    def __init__(self, screen):
        self.screen = screen
        self.color = RED
        self.points = 0
        self.live = 1
        
        self.x = randint(600, 780)
        self.y = randint(300, 550)
        self.r = randint(2, 50)

    def new_target(self):
        """ Инициализация новой цели. """
        self.x = randint(600, 780)
        self.y = randint(300, 550)
        self.r = randint(2, 50)
        
        x = self.x
        y = self.y
        r = self.r
        color = self.color
        self.live = 1

    def hit(self, points=1, ):
        """Попадание шарика в цель."""
        self.points += points


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
    def draw_score(self):
        """
        отрисовка счета
        """
        myfont = pygame.font.Font(None, 32)
        points = myfont.render(str(self.points), 1, BLACK)
        screen.blit(points, (30, 30))

#исполнительная часть кода

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    bullet = 0
    balls = []

    clock = pygame.time.Clock()
    gun = Gun(screen)
    target = Target(screen)
    finished = False

    while not finished:

        #отрисовка кадра
        screen.fill(WHITE)
        gun.draw()
        target.draw()
        target.draw_score()
        for b in balls:
            if b.do_live():
                b.draw()
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

        #движение шаров и проверка попадания в цель 
        for b in balls:
            b.move()
            if b.hittest(target) and target.live:
                target.live = 0
                target.hit()
                target.new_target()

                #отрисовка экрана победы n секунд
                n = 3
                for i in range(n*FPS):
                    screen.fill(WHITE)
                    gun.draw()
                    target.draw_score()
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
                    for b in balls:
                        b.move()
                    if finished:
                        break
                balls = []
        gun.power_up()

    pygame.quit()
