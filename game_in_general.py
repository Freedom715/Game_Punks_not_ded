import os
import sys
import time
from random import choice

import pygame
from PIL import Image
from pygame.locals import *

FPS = 50

pygame.init()
size = WIDTH, HEIGHT = 850, 650
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

player_image_file = 'Images/Cop_'
player_shoot_file = 'Images/Cop_shoot_'


# основной персонаж


def load_image(name, colorkey=None):
    fullname = os.path.join('Images', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# player_speed\player_damage_coeff\player_damage\bullet_speed\shooting_ticks\hp\ change_player
art_parameters = {'meat': (load_image('art_meat.png', -1), (0, 0, 1, 0, 0, 1, False)),
                  'sandwich': (load_image('art_sandwich.png', -1), (0, 0, 0, 0, 0, 1, False)),
                  'breakfast': (load_image('art_breakfast.png', -1), (0, 0, 0, 0, 0, 1, False)),
                  'soup': (load_image('art_soup.png', -1), (0, 0, 0, 0, 0, 1, False)),
                  'onion': (load_image('art_onion.png', -1), (0, 0, 0, 0.7, 0, False)),
                  'screw': (load_image('art_screw.png', -1), (0, 0, 0, 0.3, -0.2, False)),
                  'amulet': (load_image('art_amulet.png', -1), (0, 0, 1, 0, 0, 0, False)),
                  'kosuha': (load_image('art_kosuha.png', -1), (-0.2, 0, 0, 0, 0, 0, True)),
                  'dead_cat': (load_image('art_dead_cat.png', -1), (0, 1.5, 1, 0, 0, 0, True)),
                  'mineral_water': (
                      load_image('art_mineral_water.png', -1), (0, 0, 0.5, 0, 0, 0, False)),
                  'good_morning': (
                      load_image('art_good_morning.png', -1), (0, 0, 0.5, 0, -0.7, 1, False)),
                  'eye': (load_image('art_eye.png', -1), (0, 2, 4, -1.5, 1.25, 0, False))}


#                 '': (load_image('')), '': (load_image(''))}
#                 '': (load_image('')), '': (load_image('')), '': (load_image('')),
#                 '': (load_image('')), '': (load_image('')), '': (load_image('')), }


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


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["УРОВНИ", "", "Выберите уровни"]

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


class Room:
    def __init__(self, filename):
        self.filename, self.exits = filename, []
        self.door_up, self.door_right, self.door_down, self.door_left = None, None, None, None
        self.load_level(self.filename + ".txt")
        self.player, self.width, self.height = None, None, None

    def get_level(self, direction):
        self.player, self.width, self.height, self.enemies = self.generate_level(
            self.load_level(self.filename + ".txt"), direction)

    def load_level(self, filename):
        filename = "Levels/" + filename
        # читаем уровень, убирая символы перевода строки
        with open(filename, 'r') as mapFile:
            for line in mapFile:
                self.exits = list(map(int, line.split()))
                break
            level_map = [line.strip() for line in mapFile]

        # и подсчитываем максимальную длину
        max_width = max(map(len, level_map))

        # дополняем каждую строку пустыми клетками ('.')
        return list(map(lambda x: x.ljust(max_width, '.'), level_map))

    def generate_level(self, level, player_direction):
        new_player, x, y = None, None, None
        enemies = []
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    Tile('empty', x, y, False, False, False)
                elif level[y][x] == '#':
                    Tile('wall', x, y, True, True, False)
                elif level[y][x] == '@':
                    if self.filename == "start":
                        new_player = Player(self, x, y, player_image_file, player_shoot_file, -1)
                    Tile('empty', x, y, False, False, False)
                elif level[y][x] == 'E':
                    enemies.append(Enemy(self, x, y, player_image_file, player_shoot_file, -1))
                    Tile('empty', x, y, False, False, False)
                if level[y][x] == 'R':
                    Tile('rock', x, y, True, True, False)
                elif level[y][x] == '0':
                    Tile('hole', x, y, True, False, True)
                elif level[y][x] == "A":
                    Tile('empty', x, y, False, False, False)
                    Artifact(x, y)
                elif level[y][x] == '^':
                    self.door_up = Tile('door_up', x, y, False, True, False)
                    if player_direction == 0 and self.filename != "start":
                        new_player = Player(self, x, y + 1, player_image_file, player_shoot_file, -1)
                elif level[y][x] == '>':
                    self.door_right = Tile('door_right', x, y, False, True, False)
                    if player_direction == 1 and self.filename != "start":
                        new_player = Player(self, x - 1, y, player_image_file, player_shoot_file, -1)
                elif level[y][x] == 'v':
                    self.door_down = Tile('door_down', x, y, False, True, False)
                    if player_direction == 2 and self.filename != "start":
                        new_player = Player(self, x, y - 1, player_image_file, player_shoot_file, -1)
                elif level[y][x] == '<':
                    self.door_left = Tile('door_left', x, y, False, True, False)
                    if player_direction == 3 and self.filename != "start":
                        new_player = Player(self, x + 1, y, player_image_file, player_shoot_file, -1)

        return new_player, x, y, enemies


class Map:
    def __init__(self, rooms_count):
        self.rooms_count = rooms_count
        self.rooms = []
        self.map = [[None] * (2 * rooms_count + 1) for _ in range(2 * rooms_count + 1)]
        self.current_x = rooms_count - 1
        self.current_y = rooms_count - 1
        self.generate_map()

    def get_coords(self, coords, direction):
        if direction == 0:
            return coords[0], coords[1] - 1
        if direction == 1:
            return coords[0] + 1, coords[1]
        if direction == 2:
            return coords[0], coords[1] + 1
        if direction == 3:
            return coords[0] - 1, coords[1]

    def generate_map(self):
        x, y = self.current_x, self.current_y
        self.map[y][x] = Room("start")
        self.rooms.append(Room("start"))
        for i in range(self.rooms_count):
            direction = choice(self.rooms[-1].exits)
            coords = self.get_coords((x, y), direction)
            while self.map[coords[0]][coords[1]] is not None or direction not in self.rooms[-1].exits:
                direction = choice(self.rooms[-1].exits)
                coords = self.get_coords((x, y), direction)
            x, y = self.get_coords((x, y), direction)

            room = Room(choice(room_types))
            while (direction + 2) % 4 not in room.exits:
                room = Room(choice(room_types))

            self.map[y][x] = room
            self.rooms.append(room)
        for elem in self.map:
            print(elem)

    def get_current_room(self):
        return self.map[self.current_y][self.current_x]

    def check_door(self):
        if self.map[self.current_y][self.current_x].door_up is not None:
            if pygame.sprite.collide_rect_ratio(0.5)(self.map[self.current_y][self.current_x].player,
                                                     self.map[self.current_y][
                                                         self.current_x].door_up):
                if self.map[self.current_y - 1][self.current_x] is not None:
                    self.current_y -= 1
                    for elem in enemy_group:
                        elem.kill()
                    return True, 2
        if self.map[self.current_y][self.current_x].door_right is not None:
            if pygame.sprite.collide_rect_ratio(0.5)(self.map[self.current_y][self.current_x].player,
                                                     self.map[self.current_y][
                                                         self.current_x].door_right):
                if self.map[self.current_y][self.current_x + 1] is not None:
                    self.current_x += 1
                    for elem in enemy_group:
                        elem.kill()
                    return True, 3
        if self.map[self.current_y][self.current_x].door_down is not None:
            if pygame.sprite.collide_rect_ratio(0.5)(self.map[self.current_y][self.current_x].player,
                                                     self.map[self.current_y][
                                                         self.current_x].door_down):
                if self.map[self.current_y + 1][self.current_x] is not None:
                    self.current_y += 1
                    for elem in enemy_group:
                        elem.kill()
                    return True, 0
        if self.map[self.current_y][self.current_x].door_left is not None:
            if pygame.sprite.collide_rect_ratio(0.5)(self.map[self.current_y][self.current_x].player,
                                                     self.map[self.current_y][
                                                         self.current_x].door_left):
                if self.map[self.current_y][self.current_x - 1] is not None:
                    self.current_x -= 1
                    for elem in enemy_group:
                        elem.kill()
                    return True, 1
        return False, 0

    def update_doors(self):
        if self.map[self.current_y][self.current_x].door_up is not None:
            if not self.map[self.current_y - 1][self.current_x]:
                self.map[self.current_y][self.current_x].door_up.image = tile_images[
                    'door_up_closed']
                self.map[self.current_y][self.current_x].door_up.block_player = True

        if self.map[self.current_y][self.current_x].door_right is not None:
            if not self.map[self.current_y][self.current_x + 1]:
                self.map[self.current_y][self.current_x].door_right.image = tile_images[
                    'door_right_closed']
                self.map[self.current_y][self.current_x].door_right.block_player = True

        if self.map[self.current_y][self.current_x].door_down is not None:
            if not self.map[self.current_y + 1][self.current_x]:
                self.map[self.current_y][self.current_x].door_down.image = tile_images[
                    'door_down_closed']
                self.map[self.current_y][self.current_x].door_down.block_player = True

        if self.map[self.current_y][self.current_x].door_left is not None:
            if not self.map[self.current_y][self.current_x - 1]:
                self.map[self.current_y][self.current_x].door_left.image = tile_images[
                    'door_left_closed']
                self.map[self.current_y][self.current_x].door_left.block_player = True


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, block_player, block_bullets, damage_player):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.block_player = block_player
        self.block_bullets = block_bullets
        self.damage_player = damage_player


class Enemy(pygame.sprite.Sprite):
    def __init__(self, room, pos_x, pos_y, image, shooting_image, direction):
        super().__init__(enemy_group, all_sprites)
        self.hp = 50
        self.room = room
        self.map = Map
        self.direction = direction
        self.x = pos_x
        self.y = pos_y
        self.count = 0
        self.images = {0: Image.open(image + "run_up.gif"),
                       1: Image.open(image + "run_right.gif"),
                       2: Image.open(image + "run_down.gif"),
                       3: Image.open(image + "run_left.gif"),
                       -1: Image.open(image + "stay.gif")}
        self.shooting_images = {0: Image.open(shooting_image + "up.gif"),
                                1: Image.open(shooting_image + "right.gif"),
                                2: Image.open(shooting_image + "down.gif"),
                                3: Image.open(shooting_image + "left.gif")}
        self.change_image(self.images, direction)
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

    def change_direction(self, direction):
        if direction != self.direction:
            self.change_image(self.images, direction)

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

    def shoot(self, direction):
        self.change_image(self.shooting_images, direction)
        if self.count % shooting_tick_delay == 0:
            if direction == 0:
                Bullet(self.rect.x + 15,
                       self.rect.y - player_size_y // 2,
                       "Images/tear_", direction, 5, player_group)
            elif direction == 1:
                Bullet(self.rect.x + player_size_x,
                       self.rect.y + 10,
                       "Images/tear_", direction, 5, player_group)
            elif direction == 2:
                Bullet(self.rect.x + 15,
                       self.rect.y + player_size_y,
                       "Images/tear_", direction, 5, player_group)
            else:
                Bullet(self.rect.x - player_size_x // 2,
                       self.rect.y + 10,
                       "Images/tear_", direction, 5, player_group)
        self.count += 1

    def check_player_coords(self):
        if player.rect.x - 10 <= self.rect.x <= player.rect.x + 10 and player.rect.y <= self.rect.y:
            self.play()
            self.shoot(0)
        elif player.rect.x - 10 <= self.rect.x <= player.rect.x + 10 and player.rect.y >= self.rect.y:
            self.play()
            self.shoot(2)
        elif player.rect.y - player_size_y <= self.rect.y <= player.rect.y + player_size_x and player.rect.x <= self.rect.x:
            self.play()
            self.shoot(3)
        elif player.rect.y - player_size_y <= self.rect.y <= player.rect.y + player_size_x and player.rect.x >= self.rect.x:
            self.play()
            self.shoot(1)
        else:
            self.play()
            self.change_image(self.images, -1)

    def check_collision(self):
        if pygame.sprite.spritecollideany(self, bullet_group, False):
            self.hp -= player.attack()
            if self.hp - player.attack() <= 0:
                self.kill()
            print('Ouch!', self.hp)
        if pygame.sprite.spritecollideany(self, player_group, False):
            print('Go away!')


class Player(pygame.sprite.Sprite):
    def __init__(self, room, pos_x, pos_y, image, shooting_image, direction,
                 parameters=None):
        super().__init__(player_group, all_sprites)
        self.room = room
        self.map = Map
        if parameters is None:
            parameters = [5, 1, 3.5, 5, 21, 3]
        self.direction = direction
        # player_speed\player_damage_coeff\player_damage\bullet_speed\shooting_ticks\hp\ change_player
        self.player_parameters = parameters
        self.images = {0: Image.open(image + "run_up.gif"),
                       1: Image.open(image + "run_right.gif"),
                       2: Image.open(image + "run_down.gif"),
                       3: Image.open(image + "run_left.gif"),
                       -1: Image.open(image + "stay.gif")}
        self.shooting_images = {0: Image.open(shooting_image + "up.gif"),
                                1: Image.open(shooting_image + "right.gif"),
                                2: Image.open(shooting_image + "down.gif"),
                                3: Image.open(shooting_image + "left.gif")}
        self.change_image(self.images, direction)
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

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
        player_speed = self.player_parameters[0]
        if direction == 0:
            collision_test_rect = pygame.Rect((self.rect.x, self.rect.y - player_speed),
                                              (player_size_x, player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem in
                     tiles_group]) == -1:
                self.rect.y -= player_speed
        if direction == 2:
            collision_test_rect = pygame.Rect((self.rect.x, self.rect.y + player_speed),
                                              (player_size_x, player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem in
                     tiles_group]) == -1:
                self.rect.y += player_speed
        if direction == 3:
            collision_test_rect = pygame.Rect((self.rect.x - player_speed, self.rect.y),
                                              (player_size_x, player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem in
                     tiles_group]) == -1:
                self.rect.x -= player_speed
        if direction == 1:
            collision_test_rect = pygame.Rect((self.rect.x + player_speed, self.rect.y),
                                              (player_size_x, player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem in
                     tiles_group]) == -1:
                self.rect.x += player_speed

    def shoot(self, direction):
        # TODO: анимация стрельбы
        self.change_image(self.shooting_images, direction)
        Bullet(self.rect.x + player_size_x // 2 - 5,
               self.rect.y + player_size_y // 2 - 5,
               "Images/bottle_", direction, player.player_parameters[3], enemy_group)

    def attack(self):
        return self.player_parameters[1] * self.player_parameters[2]


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image, direction, bullet_speed, sprites_to_damage):
        super().__init__(bullet_group, all_sprites)
        self.direction = direction
        self.bullet_speed = bullet_speed
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
        self.walls = []
        for elem in tiles_group:
            if elem.block_bullets:
                self.walls.append(elem)

    def check_collision(self):
        if pygame.sprite.spritecollideany(self, self.walls):
            self.kill()
        if pygame.sprite.spritecollideany(self, self.sprites_to_damage):
            self.kill()

    def move(self):
        self.check_collision()
        if self.direction == 0:
            self.rect.y -= self.bullet_speed
        elif self.direction == 1:
            self.rect.x += self.bullet_speed
        elif self.direction == 2:
            self.rect.y += self.bullet_speed
        elif self.direction == 3:
            self.rect.x -= self.bullet_speed

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


class Artifact(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(artifact_group)
        self.art_name = choice(list(art_parameters.keys()))
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.parameters = art_parameters[self.art_name][1]
        self.image = art_parameters[self.art_name][0]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 10, tile_height * pos_y + 10)

    def check_collision(self):
        if pygame.sprite.spritecollide(self, player_group, False):
            print(player.player_parameters)
            for i in (0, 4, 3):
                if player.player_parameters[i] + int(
                        self.parameters[i] * player.player_parameters[i]) > 1:
                    player.player_parameters[i] += int(
                        self.parameters[i] * player.player_parameters[i])
                else:
                    player.player_parameters[i] = 1
            player.player_parameters[2] += self.parameters[2] * player.player_parameters[2] * \
                                           player.player_parameters[1]
            if self.parameters[1] > player.player_parameters[1]:
                player.player_parameters[1] = self.parameters[1]
            player.player_parameters[5] += self.parameters[5]
            self.kill()
            print(player.player_parameters)
        if pygame.sprite.spritecollide(self, bullet_group, False):
            print('Ouch!')


cell_size, player_size_x, player_size_y = 50, 50, 50

all_sprites, tiles_group, artifact_group = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
player_group, bullet_group, enemy_group = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()

tile_images = {'wall': pygame.transform.scale(load_image('wall.png'), (cell_size, cell_size)),
               'empty': pygame.transform.scale(load_image('floor.png'), (cell_size, cell_size)),
               'door_up': pygame.transform.scale(load_image('door.png'), (cell_size, cell_size)),
               'door_right': pygame.transform.rotate(load_image('door.png'), 270),
               'door_down': pygame.transform.rotate(load_image('door.png'), 180),
               'door_left': pygame.transform.rotate(load_image('door.png'), 90),
               'door_up_closed': pygame.transform.scale(load_image('door_closed.png'),
                                                        (cell_size, cell_size)),
               'door_right_closed': pygame.transform.rotate(load_image('door_closed.png'), 270),
               'door_down_closed': pygame.transform.rotate(load_image('door_closed.png'), 180),
               'door_left_closed': pygame.transform.rotate(load_image('door_closed.png'), 90),
               'hole': pygame.transform.scale(load_image('hole.png'), (cell_size, cell_size)),
               'rock': pygame.transform.scale(load_image('rock.png', -1), (cell_size, cell_size))}
tile_width, tile_height = 50, 50

room_types = ["circle", "circle_in_square", "death_road", "diagonal", "lines", "mexico",
              "square_trap", "trapezoid"]

# player, level_x, level_y = generate_level(load_level('map.txt'))
game_map = Map(5)
room = game_map.get_current_room()
room.get_level(0)
player = room.player
game_map.update_doors()
time_left = 0
shooting_tick_delay = 10
counter = 0
running = True

start_screen()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            counter = 0
        if event.type == pygame.KEYUP:
            player.cur = 0
            player.change_image(player.images, player.direction)
            player.change_direction(-1)
    elem = pygame.key.get_pressed()

    if elem[pygame.K_ESCAPE] == 1:
        running = False
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
        if counter % player.player_parameters[4] == 0:
            player.shoot(0)
    elif elem[pygame.K_RIGHT]:
        player.play()
        if counter % player.player_parameters[4] == 0:
            player.shoot(1)
    elif elem[pygame.K_DOWN]:
        player.play()
        if counter % player.player_parameters[4] == 0:
            player.shoot(2)
    elif elem[pygame.K_LEFT]:
        player.play()
        if counter % player.player_parameters[4] == 0:
            player.shoot(3)

    screen.fill((0, 0, 0))
    tiles_group.draw(screen)
    enemy_group.draw(screen)
    artifact_group.draw(screen)
    bullet_group.draw(screen)
    player_group.draw(screen)

    for elem in bullet_group:
        elem.render()
        elem.move()

    for elem in artifact_group:
        elem.check_collision()

    for elem in enemy_group:
        elem.check_player_coords()
        elem.check_collision()

    door = game_map.check_door()
    if door[0]:
        all_sprites, tiles_group, artifact_group = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
        player_group, bullet_group = pygame.sprite.Group(), pygame.sprite.Group()
        room = game_map.get_current_room()
        room.get_level(door[1])
        player = room.player
        game_map.update_doors()

    for elem in bullet_group:
        elem.render()
    player.render()
    pygame.display.flip()
    clock.tick(FPS)
    counter += 1
pygame.quit()
