import pygame
import os

'''Создание окна и ввод глобальных переменных.
    GRAVITATION - отвечает за физику прыжков
    JUMP_P - сила прыжка(коэффициент)'''
pygame.init()
WIDTH, HEIGHT = (1200, 800)
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)
SPD = 7
pygame.key.set_repeat(10, 1)
GRAVITATION = 0.5
JUMP_P = 10
clock = pygame.time.Clock()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()


def load_image(name, colorkey=None):
    """Отвечает за загрузку изображений из папки data.
        На вход получает имя файла."""
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    """Считывает структуру уровня из файла и
        возвращает в виде списка.
        На вход получает имя тестового файла."""
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


"""Загружаем два изобржения для создания анимации движения"""
player_image = load_image('Knight.png', -1)
player_image1 = load_image('Knight_L.png', -1)


class Platform(pygame.sprite.Sprite):
    """Включает в себя все платформы, с которыми главный
        герой может взаимодействовать и стоять на них.
        Конструктор класса загружает изображение и находит
        прямоугольник, в рамках которого находится обЪект."""

    def __init__(self, x_cord, y_cord):
        super().__init__(tiles_group, all_sprites)
        self.image = load_image('box.png')
        self.rect = self.image.get_rect()
        self.rect.x = x_cord
        self.rect.y = y_cord


class Player(pygame.sprite.Sprite):
    """Основной класс, отвечает за главного героя.
        Конструктор загружает изображение и получает
        прямоугольник объекта."""

    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.y_v = 0
        self.x_v = 0
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.on_earth = False
        self.jump_sound = pygame.mixer.Sound('data/sound/jump1.ogg')

    def update(self, left, right, up, plat):
        """Отвечает за движение и физику главного героя."""
        if not (left and right):
            self.x_v = 0
        if not self.on_earth:
            self.y_v += GRAVITATION

        self.on_earth = False

        self.rect.x += self.x_v
        self.collide(self.x_v, 0, plat)
        self.rect.y += self.y_v
        self.collide(0, self.y_v, plat)

    def collide(self, x_v, y_v, plat):
        """Отвечает за столкновение с платформами."""
        for pl in plat:
            if pygame.sprite.collide_rect(self, pl):
                if x_v > 0:
                    self.rect.right = pl.rect.left
                if x_v < 0:
                    self.rect.left = pl.rect.right
                if y_v > 0:
                    self.rect.bottom = pl.rect.top
                    self.on_earth = True
                    self.y_v = 0
                if y_v < 0:
                    self.rect.top = pl.rect.bottom


class Camera:
    """Определяет камеру(ракурс) наблюдения за главным героем."""

    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        """Смещение объектов относительно камеры."""
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        """Смещение камеры относительно главного героя."""
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


# Создание шлавного героя
hero = Player(1200, 4800)
# Создание объекта Камера
camera = Camera()

left = right = up = False

all_sprites.add(hero)
plat = []
"""Генерация уровня и создание группы спрайтов."""
x_cord = 0
y_cord = 0
for row in load_level('map.txt'):
    for col in row:
        if col == '#':
            wall = Platform(x_cord, y_cord)
            tiles_group.add(wall)
            plat.append(wall)
        x_cord += 50
    y_cord += 50
    x_cord = 0

tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

# Блок звука
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()
sound = pygame.mixer.Sound('data/sound/music.ogg')
sound.play(-1)
# Основной цикл программы
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                hero.image = player_image1
                hero.rect.x -= SPD
                left = True
            if key[pygame.K_RIGHT]:
                hero.image = player_image
                hero.rect.x += SPD
                right = True
            if key[pygame.K_UP]:
                hero.rect.y += -JUMP_P
                hero.jump_sound.play()
                up = True

        if event.type == pygame.KEYUP:
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                left = False
            if key[pygame.K_RIGHT]:
                right = False
            if key[pygame.K_UP]:
                up = False
    screen.fill((0, 0, 0))
    hero.update(left, right, up, plat)
    camera.update(hero)
    all_sprites.draw(screen)
    for sprite in all_sprites:
        camera.apply(sprite)
    screen.blit(screen, (0, 0))
    pygame.display.flip()
    clock.tick(60)
