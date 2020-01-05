import os
import time
from pygame.locals import *
from PIL import Image
import pygame
import sys

FPS = 50

pygame.init()
size = WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()
# основной персонаж
player = None


def get_frames(obj):
    image = obj.image_gif
    pal = image.getpalette()
    base_palette = []
    for i in range(0, len(pal), 3):
        rgb = pal[i:i + 3]
        base_palette.append(rgb)

    all_tiles = []
    try:
        while 1:
            if not image.tile:
                image.seek(0)
            if image.tile:
                all_tiles.append(image.tile[0][3][0])
            image.seek(image.tell() + 1)
    except EOFError:
        image.seek(0)

    all_tiles = tuple(set(all_tiles))

    try:
        while 1:
            try:
                duration = image.info["duration"]
            except:
                duration = 100

            duration *= .001  # convert to milliseconds!
            cons = False

            x0, y0, x1, y1 = (0, 0) + image.size
            if image.tile:
                tile = image.tile
            else:
                image.seek(0)
                tile = image.tile
            if len(tile) > 0:
                x0, y0, x1, y1 = tile[0][1]

            if all_tiles:
                if all_tiles in ((6,), (7,)):
                    cons = True
                    pal = image.getpalette()
                    palette = []
                    for i in range(0, len(pal), 3):
                        rgb = pal[i:i + 3]
                        palette.append(rgb)
                elif all_tiles in ((7, 8), (8, 7)):
                    pal = image.getpalette()
                    palette = []
                    for i in range(0, len(pal), 3):
                        rgb = pal[i:i + 3]
                        palette.append(rgb)
                else:
                    palette = base_palette
            else:
                palette = base_palette

            pi = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
            pi.set_palette(palette)
            if "transparency" in image.info:
                pi.set_colorkey(image.info["transparency"])
            pi2 = pygame.Surface(image.size, SRCALPHA)
            if cons:
                for i in obj.frames:
                    pi2.blit(i[0], (0, 0))
            pi2.blit(pi, (x0, y0), (x0, y0, x1 - x0, y1 - y0))

            obj.frames.append([pi2, duration])
            image.seek(image.tell() + 1)
    except EOFError:
        pass


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y, False)
            elif level[y][x] == '#':
                Tile('wall', x, y, True)
            elif level[y][x] == '@':
                Tile('empty', x, y, False)
                new_player = Player(x, y, player_image_file, player_shoot_file, 1, 5, 10)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, block):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.block = block


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image, shooting_image, direction, speed, shooting_ticks):
        super().__init__(player_group, all_sprites)
        self.direction = direction
        self.shooting_ticks = shooting_ticks
        self.images = {0: Image.open(image + "up.gif"),
                       1: Image.open(image + "right.gif"),
                       2: Image.open(image + "down.gif"),
                       3: Image.open(image + "left.gif")}
        self.shooting_images = {0: Image.open(shooting_image + "up.gif"),
                                1: Image.open(shooting_image + "right.gif"),
                                2: Image.open(shooting_image + "up.gif"),
                                3: Image.open(shooting_image + "left.gif")}
        self.change_image(self.images, direction)
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.speed = speed

    def render(self):
        if self.running:
            if time.time() - self.ptime > self.frames[self.cur][1]:
                if self.reversed:
                    self.cur -= 1
                    if self.cur < self.startpoint:
                        self.cur = self.breakpoint
                else:
                    self.cur += 1
                    if self.cur > self.breakpoint:
                        self.cur = self.startpoint

                self.ptime = time.time()
        self.image = self.frames[self.cur][0]

    def pause(self):
        self.running = False

    def play(self):
        self.running = True

    def change_image(self, image_group, direction):
        self.running = True
        self.reversed = False
        self.image_gif = image_group[direction]
        self.frames = []
        self.startpoint = 0
        self.ptime = time.time()
        self.cur = 0
        get_frames(self)
        self.breakpoint = len(self.frames) - 1
        self.render()
        self.direction = direction

    def change_direction(self, direction):
        if direction != self.direction:
            self.change_image(self.images, direction)

    def move(self, direction):
        self.change_direction(direction)
        self.play()
        if direction == 0:
            collision_test_rect = pygame.Rect((self.rect.x, self.rect.y - self.speed),
                                              (player_size_x, player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block else pygame.Rect((0, 0), (0, 0)) for elem in
                     tiles_group]) == -1:
                self.rect.y -= self.speed
        if direction == 2:
            collision_test_rect = pygame.Rect((self.rect.x, self.rect.y + self.speed),
                                              (player_size_x, player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block else pygame.Rect((0, 0), (0, 0)) for elem in
                     tiles_group]) == -1:
                self.rect.y += self.speed
        if direction == 3:
            collision_test_rect = pygame.Rect((self.rect.x - self.speed, self.rect.y),
                                              (player_size_x, player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block else pygame.Rect((0, 0), (0, 0)) for elem in
                     tiles_group]) == -1:
                self.rect.x -= self.speed
        if direction == 1:
            collision_test_rect = pygame.Rect((self.rect.x + self.speed, self.rect.y),
                                              (player_size_x, player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block else pygame.Rect((0, 0), (0, 0)) for elem in
                     tiles_group]) == -1:
                self.rect.x += self.speed

    def shoot(self, direction):
        # TODO: анимация стрельбы
        self.change_image(self.shooting_images, direction)
        Bullet(self.rect.x + player_size_x // 2 - 5,
               self.rect.y + player_size_y // 2 - 5,
               "data/bottle_", direction, 5, player_group)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image, direction, speed, sprites_to_damage):
        super().__init__(bullet_group, all_sprites)
        self.direction = direction
        self.images = {0: Image.open(image + "up.gif"),
                       1: Image.open(image + "right.gif"),
                       2: Image.open(image + "down.gif"),
                       3: Image.open(image + "left.gif")}
        self.running = True
        self.reversed = False
        self.image_gif = self.images[direction]
        self.frames = []
        self.startpoint = 0
        self.ptime = time.time()
        self.cur = 0
        get_frames(self)
        self.breakpoint = len(self.frames) - 1
        self.render()
        self.rect = self.image.get_rect().move(x, y)
        self.sprites_to_damage = sprites_to_damage
        self.speed = speed

    def check_collision(self):
        if pygame.sprite.spritecollideany(self, walls):
            self.kill()
        # if pygame.sprite.spritecollideany(self, self.sprites_to_damage):
        #     self.kill()

    def move(self):
        self.check_collision()
        if self.direction == 0:
            self.rect.y -= self.speed
        elif self.direction == 1:
            self.rect.x += self.speed
        elif self.direction == 2:
            self.rect.y += self.speed
        elif self.direction == 3:
            self.rect.x -= self.speed

    def render(self):
        if self.running:
            if time.time() - self.ptime > self.frames[self.cur][1]:
                if self.reversed:
                    self.cur -= 1
                    if self.cur < self.startpoint:
                        self.cur = self.breakpoint
                else:
                    self.cur += 1
                    if self.cur > self.breakpoint:
                        self.cur = self.startpoint

                self.ptime = time.time()
        self.image = self.frames[self.cur][0]

    def pause(self):
        self.running = False

    def play(self):
        self.running = True

    def change_direction(self, direction):
        if direction != self.direction:
            self.image_gif = self.images[direction]
            self.frames = []
            self.startpoint = 0
            self.ptime = time.time()
            self.cur = 0
            get_frames(self)
            self.breakpoint = len(self.frames) - 1
            self.render()
            self.direction = direction


cell_size, player_size_x, player_size_y = 50, 50, 50
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
tile_images = {'wall': pygame.transform.scale(load_image('rock.png'), (cell_size, cell_size)),
               'empty': pygame.transform.scale(load_image('floor.png'), (cell_size, cell_size))}
player_image_file = "data/Cop_run_"
player_shoot_file = "data/Cop_shoot_"
tile_width = tile_height = 50
start_screen()
running = True
player, level_x, level_y = generate_level(load_level('map.txt'))
time_left = 0
shooting_tick_delay = 10
counter = 0
walls = []
for elem in tiles_group:
    if elem.block:
        walls.append(elem)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            counter = 0
        if event.type == pygame.KEYUP:
            player.cur = 0
            player.change_image(player.images, player.direction)
    elem = pygame.key.get_pressed()

    if elem[pygame.K_w] == 1:
        player.move(0)
    if elem[pygame.K_s] == 1:
        player.move(2)
    if elem[pygame.K_a] == 1:
        player.move(3)
    if elem[pygame.K_d] == 1:
        player.move(1)
    if elem[pygame.K_UP]:
        player.play()
        if counter % player.shooting_ticks == 0:
            player.shoot(0)
    elif elem[pygame.K_RIGHT]:
        player.play()
        if counter % player.shooting_ticks == 0:
            player.shoot(1)
    elif elem[pygame.K_DOWN]:
        player.play()
        if counter % player.shooting_ticks == 0:
            player.shoot(2)
    elif elem[pygame.K_LEFT]:
        player.play()
        if counter % player.shooting_ticks == 0:
            player.shoot(3)

    for elem in bullet_group:
        elem.render()
        elem.move()

    screen.fill((0, 0, 0))
    tiles_group.draw(screen)
    player_group.draw(screen)
    bullet_group.draw(screen)
    for elem in bullet_group:
        elem.render()
    player.render()
    player.pause()
    pygame.display.flip()
    clock.tick(FPS)
    counter = (counter + 1) % FPS
pygame.quit()
