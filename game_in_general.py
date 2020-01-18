import os
import sys
import time
from random import choice

import pygame
from PIL import Image
from pygame.locals import *

FPS = 50

pygame.init()


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


class Button(pygame.sprite.Sprite):
    def __init__(self, screen, menu_button_group, x, y, image, selected_image, selected,
                 clicked_func):
        super().__init__(menu_button_group)
        self.not_selected_image = load_image(image)
        self.selected_image = load_image(selected_image)
        self.selected = selected
        if self.selected:
            self.image = self.selected_image
        else:
            self.image = self.not_selected_image

        self.clicked_func = clicked_func
        self.rect = self.image.get_rect().move(x, y)

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            if self.clicked_func:
                self.clicked_func()


class Main:
    def __init__(self):
        self.size = self.WIDTH, self.HEIGHT = 850, 650
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.player_image_file = 'Images/Red_'
        self.player_shoot_file = 'Images/Red_run_'
        self.cell_size, self.player_size_x, self.player_size_y = 50, 50, 50

        self.tile_images = {
            'wall': pygame.transform.scale(load_image('wall.png'), (self.cell_size, self.cell_size)),
            'empty': pygame.transform.scale(load_image('floor.png'),
                                            (self.cell_size, self.cell_size)),
            'door_up': pygame.transform.scale(load_image('door.png'),
                                              (self.cell_size, self.cell_size)),
            'door_right': pygame.transform.rotate(load_image('door.png'), 270),
            'door_down': pygame.transform.rotate(load_image('door.png'), 180),
            'door_left': pygame.transform.rotate(load_image('door.png'), 90),
            'door_up_closed': pygame.transform.scale(load_image('door_closed.png'),
                                                     (self.cell_size, self.cell_size)),
            'door_right_closed': pygame.transform.rotate(load_image('door_closed.png'), 270),
            'door_down_closed': pygame.transform.rotate(load_image('door_closed.png'), 180),
            'door_left_closed': pygame.transform.rotate(load_image('door_closed.png'), 90),
            'hole': pygame.transform.scale(load_image('hole.png'), (self.cell_size, self.cell_size)),
            'rock': pygame.transform.scale(load_image('rock.png', -1),
                                           (self.cell_size, self.cell_size))}
        self.tile_width, self.tile_height = 50, 50

        self.room_types = ["circle", "circle_in_square", "death_road", "diagonal", "lines", "mexico",
                           "square_trap", "trapezoid"]
        self.running = True

        # player_speed\player_damage_coeff\player_damage\bullet_speed\shooting_ticks\hp\ change_player
        self.art_parameters = {'meat': (load_image('art_meat.png', -1), (0, 0, 1, 0, 0, 1, False)),
                               'sandwich': (
                                   load_image('art_sandwich.png', -1), (0, 0, 0, 0, 0, 1, False)),
                               'breakfast': (
                                   load_image('art_breakfast.png', -1), (0, 0, 0, 0, 0, 1, False)),
                               'soup': (load_image('art_soup.png', -1), (0, 0, 0, 0, 0, 1, False)),
                               'onion': (load_image('art_onion.png', -1), (0, 0, 0, 0.7, 0, False)),
                               'screw': (
                                   load_image('art_screw.png', -1), (0, 0, 0, 0.3, -0.2, False)),
                               'amulet': (
                                   load_image('art_amulet.png', -1), (0, 0, 1, 0, 0, 0, False)),
                               'dead_cat': (
                                   load_image('art_dead_cat.png', -1), (0, 1.5, 1, 0, 0, 0, True)),
                               'mineral_water': (
                                   load_image('art_mineral_water.png', -1),
                                   (0, 0, 0.5, 0, 0, 0, False)),
                               'good_morning': (
                                   load_image('art_good_morning.png', -1),
                                   (0, 0, 0.5, 0, -0.7, 1, False)),
                               'eye': (
                                   load_image('art_eye.png', -1), (0, 2, 4, -1.5, 1.25, 0, False))}

        self.player_parameters = [5, 1, 3.5, 5, 21, 6]

        self.counter = 0
        self.shooting_tick_delay = 10

        self.all_sprites, self.tiles_group, self.artifact_group = None, None, None
        self.player_group, self.bullet_group, self.enemy_group = None, None, None
        self.buttons_group = None
        self.game_map = None
        self.player = None
        self.room = None

        self.menu()

    def load_map(self, rooms_count):
        self.game_map = Map(rooms_count, self)

    def load_room(self, direction):
        print(self.player_parameters)
        self.all_sprites, self.tiles_group = pygame.sprite.Group(), pygame.sprite.Group()
        self.artifact_group, self.player_group = pygame.sprite.Group(), pygame.sprite.Group()
        self.bullet_group, self.enemy_group = pygame.sprite.Group(), pygame.sprite.Group()
        self.room = self.game_map.get_current_room()
        self.room.get_level(direction)
        self.player = self.room.player
        self.game_map.update_doors()

    def menu(self):
        self.buttons_group = pygame.sprite.Group()
        fon = pygame.transform.scale(load_image('fon_menu.png'), (self.WIDTH, self.HEIGHT))
        self.screen.blit(fon, (0, 0))

        Button(self.screen, self.buttons_group, 250, 100, "Start_button.png",
               "Start_button.png", False,
               self.start_game)
        Button(self.screen, self.buttons_group, 250, 200, "Setting_button.png",
               "Setting_button.png", False, None)
        Button(self.screen, self.buttons_group, 250, 300, "Autors_button.png",
               "Autors_button.png", False, self.autors_show)

        # for line in intro_text:
        #    string_rendered = font.render(line, 1, pygame.Color('black'))
        #    intro_rect = string_rendered.get_rect()
        #    text_coord += 10
        #    intro_rect.top = text_coord
        #    intro_rect.x = 10
        #    text_coord += intro_rect.height
        #    self.screen.blit(string_rendered, intro_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for elem in self.buttons_group:
                        elem.check_click(event.pos)

            self.buttons_group.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

    def start_game(self):
        self.player_parameters = [5, 1, 3.5, 5, 21, 6]
        self.load_map(5)
        self.load_room(0)
        self.main_cycle()

    def autors_show(self):
        fon = pygame.transform.scale(load_image('fon_menu.png'), (self.WIDTH, self.HEIGHT))
        text = "Урвачев Роман и Зотова Екатерина"
        self.buttons_group = pygame.sprite.Group()
        self.screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_rendered = font.render(text, 1, pygame.Color('black'))
        self.screen.blit(text_rendered, (250, 100))
        button_start = Button(self.screen, self.buttons_group, 250, 200, "Start_button.png",
                              "Start_button.png", False,
                              self.start_game)

    def show_stats(self):
        stats = ["Статистика персонажа", "Скорость", "Множитель урона", "Урон",
                 "Скорость пули", "Время перезарядки", "ХП"]
        intro_text = []
        text_coord = 50
        font = pygame.font.Font(None, 36)
        for i in range(len(stats)):
            if i >= 1:
                intro_text.append(stats[i] + ": " + str(self.player_parameters[i - 1]))
            else:
                intro_text.append(stats[i])
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 50
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)

    def game_over(self):
        self.buttons_group = pygame.sprite.Group()
        text = "Гамовер"
        fon = pygame.transform.scale(load_image('fon_menu.png'), (self.WIDTH, self.HEIGHT))
        self.screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 100)
        text_rendered = font.render(text, 1, pygame.Color('black'))
        self.screen.blit(text_rendered, (250, 100))

        button_start = Button(self.screen, self.buttons_group, 250, 200, "Continue_button.png",
                              "Continue_button.png", False,
                              self.start_game)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for elem in self.buttons_group:
                        elem.check_click(event.pos)

            self.buttons_group.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

    def terminate(self):
        pygame.quit()
        sys.exit()

    def reset(self):
        self.__init__()

    def main_cycle(self):
        while self.running:
            self.screen.fill((0, 0, 0))
            self.tiles_group.draw(self.screen)
            self.enemy_group.draw(self.screen)
            self.artifact_group.draw(self.screen)
            self.bullet_group.draw(self.screen)
            self.player_group.draw(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.KEYDOWN:
                    self.counter = 0
                if event.type == pygame.KEYUP:
                    if (event.key == pygame.K_w or event.key == pygame.K_s or
                            event.key == pygame.K_a or event.key == pygame.K_d or
                            event.key == pygame.K_UP or event.key == pygame.K_RIGHT or
                            event.key == pygame.K_DOWN or event.key == pygame.K_LEFT):
                        self.player.cur = 0
                        self.player.change_image(self.player.images, self.player.direction)
                        self.player.change_direction(-1)
            keys = pygame.key.get_pressed()

            if keys[pygame.K_ESCAPE] == 1:
                return
            if keys[pygame.K_r] == 1:
                self.start_game()
            if keys[pygame.K_w] == 1:
                self.player.move(0)
            if keys[pygame.K_s] == 1:
                self.player.move(2)
            if keys[pygame.K_a] == 1:
                self.player.move(3)
            if keys[pygame.K_d] == 1:
                self.player.move(1)
            if keys[pygame.K_UP]:
                if self.counter % self.player.player_parameters[4] == 0:
                    self.player.shoot(0)
            elif keys[pygame.K_RIGHT]:
                if self.counter % self.player.player_parameters[4] == 0:
                    self.player.shoot(1)
            elif keys[pygame.K_DOWN]:
                if self.counter % self.player.player_parameters[4] == 0:
                    self.player.shoot(2)
            elif keys[pygame.K_LEFT]:
                if self.counter % self.player.player_parameters[4] == 0:
                    self.player.shoot(3)
            elif keys[pygame.K_TAB] == 1:
                self.show_stats()

            for elem in self.bullet_group:
                elem.render()
                elem.move()

            for elem in self.player_group:
                elem.render()
                elem.check_collision()

            for elem in self.artifact_group:
                elem.check_collision()

            for elem in self.enemy_group:
                elem.move()
                elem.render()
                elem.check_player_coords()
                elem.check_collision()

            door = self.game_map.check_door()
            if door[0]:
                self.load_room(door[1])

            for elem in self.bullet_group:
                elem.render()

            self.player.render()
            pygame.display.flip()
            self.clock.tick(FPS)
            self.counter += 1


class Room:
    def __init__(self, filename, main):
        self.main = main
        self.filename, self.exits, self.enemies, self.room_map = filename, [], [], []
        self.door_up, self.door_right, self.door_down, self.door_left = None, None, None, None
        self.load_level(self.filename + ".txt")
        self.player, self.width, self.height = None, None, None

    def get_level(self, direction):
        self.player, self.width, self.height = self.generate_level(
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
        for elem in list(map(lambda x: x.ljust(max_width, '.'), level_map)):
            self.room_map.append(
                list(map(lambda x: 0 if x in ["#", "0", "^", "<", ">", "v", "R"] else -1, elem)))

        return list(map(lambda x: x.ljust(max_width, '.'), level_map))

    def generate_level(self, level, player_direction):
        new_player, x, y = None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    Tile('empty', x, y, False, False, False, self.main)
                elif level[y][x] == '#':
                    Tile('wall', x, y, True, True, False, self.main)
                elif level[y][x] == '@':
                    if self.filename == "start":
                        new_player = Player(self, x, y, self.main.player_image_file,
                                            self.main.player_shoot_file, -1,
                                            self.main, self.main.player_parameters)
                    Tile('empty', x, y, False, False, False, self.main)
                elif level[y][x] == 'E':
                    self.enemies.append(
                        Enemy(self, x, y, "Images\Cop_", "Images\Cop_shoot_",
                              -1, self.main))
                    Tile('empty', x, y, False, False, False, self.main)
                if level[y][x] == 'R':
                    Tile('rock', x, y, True, True, False, self.main)
                elif level[y][x] == '0':
                    Tile('hole', x, y, True, False, True, self.main)
                elif level[y][x] == "A":
                    Tile('empty', x, y, False, False, False, self.main)
                    Artifact(x, y, self.main)
                elif level[y][x] == '^':
                    self.door_up = Tile('door_up', x, y, False, True, False, self.main)
                    if player_direction == 0 and self.filename != "start":
                        new_player = Player(self, x, y + 1, self.main.player_image_file,
                                            self.main.player_shoot_file,
                                            -1, self.main, self.main.player_parameters)
                elif level[y][x] == '>':
                    self.door_right = Tile('door_right', x, y, False, True, False, self.main)
                    if player_direction == 1 and self.filename != "start":
                        new_player = Player(self, x - 1, y, self.main.player_image_file,
                                            self.main.player_shoot_file,
                                            -1, self.main, self.main.player_parameters)
                elif level[y][x] == 'v':
                    self.door_down = Tile('door_down', x, y, False, True, False, self.main)
                    if player_direction == 2 and self.filename != "start":
                        new_player = Player(self, x, y - 1, self.main.player_image_file,
                                            self.main.player_shoot_file,
                                            -1, self.main, self.main.player_parameters)
                elif level[y][x] == '<':
                    self.door_left = Tile('door_left', x, y, False, True, False, self.main)
                    if player_direction == 3 and self.filename != "start":
                        new_player = Player(self, x + 1, y, self.main.player_image_file,
                                            self.main.player_shoot_file,
                                            -1, self.main, self.main.player_parameters)

        return new_player, x, y

    def find_way(self, coords1, coords2):
        x1, y1 = coords1
        x2, y2 = coords2
        delta_x = [1, 0, -1, 0]
        delta_y = [0, 1, 0, -1]

        test_board = []
        height = len(self.room_map)
        width = len(self.room_map[0])
        for y in range(height):
            test_board.append([])
            for x in range(width):
                if self.room_map[y][x] == 0:
                    test_board[y].append(-1)
                else:
                    test_board[y].append(-2)

        counter = 0
        test_board[y1][x1] = 0
        while True:
            stop = True
            for y in range(height):
                for x in range(width):
                    if test_board[y][x] == counter:
                        for i in range(4):
                            x3, y3 = x + delta_x[i], y + delta_y[i]
                            if 0 <= x3 < width and 0 <= y3 < height:
                                if test_board[y3][x3] == -2:
                                    stop = False
                                    test_board[y3][x3] = counter + 1
            counter += 1
            if stop or test_board[y2][x2] != -2:
                break
        path = []
        if test_board[y2][x2] == -2:
            return []

        x = x2
        y = y2
        counter = test_board[y2][x2]
        while counter > 0:
            path.append((x, y))
            counter -= 1
            for i in range(4):
                x3, y3 = x + delta_x[i], y + delta_y[i]
                if 0 <= x3 < width and 0 <= y3 < height:
                    if test_board[y3][x3] == counter:
                        x = x + delta_x[i]
                        y = y + delta_y[i]
                        break
        return path

    def __repr__(self):
        return 'Room(' + self.filename + ')'


class Map:
    def __init__(self, rooms_count, main):
        self.rooms_count = rooms_count
        self.rooms = []
        self.map = [[None] * (2 * rooms_count + 2) for _ in range(2 * rooms_count + 2)]
        self.current_x = rooms_count
        self.current_y = rooms_count
        self.main = main
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
        self.map[y][x] = Room("start", self.main)
        self.rooms.append(Room("start", self.main))

        special_rooms_directions = {}

        directions = [0, 1, 2, 3]
        for elem in ["boss_room", "artifact_room", "shop"]:
            direction = choice(directions)
            special_rooms_directions[direction] = elem
            directions.remove(direction)

        directions = [0, 1, 2, 3]

        for main_direction in directions:
            x, y = self.current_x, self.current_y
            for i in range(self.rooms_count):
                if i in range(1):
                    direction = main_direction
                    x, y = self.get_coords((x, y), direction)
                else:
                    direction = choice(self.rooms[-1].exits)
                    coords = self.get_coords((x, y), direction)
                    while (self.map[coords[1]][coords[0]] is not None or
                           (direction + 2) % 4 == main_direction):
                        direction = choice(self.rooms[-1].exits)
                        coords = self.get_coords((x, y), direction)
                    x, y = self.get_coords((x, y), direction)

                if i != self.rooms_count - 1:
                    room = Room(choice(self.main.room_types), self.main)
                    while (direction + 2) % 4 not in room.exits or not self.room_check_neighbours(
                            room, x, y):
                        room = Room(choice(self.main.room_types), self.main)

                    self.map[y][x] = room
                    self.rooms.append(room)
                else:
                    if direction in special_rooms_directions:
                        self.map[y][x] = Room(special_rooms_directions[direction], self.main)

            for elem in self.map:
                for elem1 in elem:
                    if elem1:
                        print(elem1.filename[0:2], end=" ")
                    else:
                        print("  ", end=" ")
                print()
            print()

    def room_check_neighbours(self, room, x, y):
        for elem in room.exits:
            coords = self.get_coords((x, y), elem)
            if not self.map[coords[1]][coords[0]]:
                return True
        return False

    def get_current_room(self):
        return self.map[self.current_y][self.current_x]

    def check_door(self):
        if self.map[self.current_y][self.current_x].door_up is not None:
            if pygame.sprite.collide_rect_ratio(0.5)(self.map[self.current_y][self.current_x].player,
                                                     self.map[self.current_y][
                                                         self.current_x].door_up):
                if self.map[self.current_y - 1][self.current_x] is not None:
                    self.current_y -= 1
                    return True, 2
        if self.map[self.current_y][self.current_x].door_right is not None:
            if pygame.sprite.collide_rect_ratio(0.5)(self.map[self.current_y][self.current_x].player,
                                                     self.map[self.current_y][
                                                         self.current_x].door_right):
                if self.map[self.current_y][self.current_x + 1] is not None:
                    self.current_x += 1
                    return True, 3
        if self.map[self.current_y][self.current_x].door_down is not None:
            if pygame.sprite.collide_rect_ratio(0.5)(self.map[self.current_y][self.current_x].player,
                                                     self.map[self.current_y][
                                                         self.current_x].door_down):
                if self.map[self.current_y + 1][self.current_x] is not None:
                    self.current_y += 1
                    return True, 0
        if self.map[self.current_y][self.current_x].door_left is not None:
            if pygame.sprite.collide_rect_ratio(0.5)(self.map[self.current_y][self.current_x].player,
                                                     self.map[self.current_y][
                                                         self.current_x].door_left):
                if self.map[self.current_y][self.current_x - 1] is not None:
                    self.current_x -= 1
                    return True, 1
        return False, 0

    def update_doors(self):
        if self.map[self.current_y][self.current_x].door_up is not None:
            if not self.map[self.current_y - 1][self.current_x]:
                self.map[self.current_y][self.current_x].door_up.image = self.main.tile_images[
                    'door_up_closed']
                self.map[self.current_y][self.current_x].door_up.block_player = True
            elif 2 not in self.map[self.current_y - 1][self.current_x].exits:
                self.map[self.current_y][self.current_x].door_up.image = self.main.tile_images[
                    'door_up_closed']
                self.map[self.current_y][self.current_x].door_up.block_player = True

        if self.map[self.current_y][self.current_x].door_right is not None:
            if not self.map[self.current_y][self.current_x + 1]:
                self.map[self.current_y][self.current_x].door_right.image = self.main.tile_images[
                    'door_right_closed']
                self.map[self.current_y][self.current_x].door_right.block_player = True
            elif 3 not in self.map[self.current_y][self.current_x + 1].exits:
                self.map[self.current_y][self.current_x].door_right.image = self.main.tile_images[
                    'door_up_closed']
                self.map[self.current_y][self.current_x].door_right.block_player = True

        if self.map[self.current_y][self.current_x].door_down is not None:
            if not self.map[self.current_y + 1][self.current_x]:
                self.map[self.current_y][self.current_x].door_down.image = self.main.tile_images[
                    'door_down_closed']
                self.map[self.current_y][self.current_x].door_down.block_player = True
            elif 0 not in self.map[self.current_y + 1][self.current_x].exits:
                self.map[self.current_y][self.current_x].door_down.image = self.main.tile_images[
                    'door_up_closed']
                self.map[self.current_y][self.current_x].door_down.block_player = True

        if self.map[self.current_y][self.current_x].door_left is not None:
            if not self.map[self.current_y][self.current_x - 1]:
                self.map[self.current_y][self.current_x].door_left.image = self.main.tile_images[
                    'door_left_closed']
                self.map[self.current_y][self.current_x].door_left.block_player = True
            elif 1 not in self.map[self.current_y][self.current_x - 1].exits:
                self.map[self.current_y][self.current_x].door_left.image = self.main.tile_images[
                    'door_up_closed']
                self.map[self.current_y][self.current_x].door_left.block_player = True


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, block_player, block_bullets, damage_player, main):
        super().__init__(main.tiles_group, main.all_sprites)
        self.image = main.tile_images[tile_type]
        self.rect = self.image.get_rect().move(main.tile_width * pos_x, main.tile_height * pos_y)
        self.block_player = block_player
        self.block_bullets = block_bullets
        self.damage_player = damage_player


class Enemy(pygame.sprite.Sprite):
    def __init__(self, room, pos_x, pos_y, image, shooting_image, direction, main):
        super().__init__(main.enemy_group, main.all_sprites)
        self.running = None
        self.reversed = None
        self.image_gif = None
        self.frames = None
        self.startpoint = None
        self.ptime = None
        self.cur = None
        self.breakpoint = None
        self.image = None
        self.main = main
        self.hp = 50
        self.room = room
        self.map = Map
        self.direction = direction
        self.x = pos_x
        self.y = pos_y
        self.count = 0
        self.speed = 2
        self.image_gif = None
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
        self.rect = self.image.get_rect().move(self.main.tile_width * pos_x,
                                               self.main.tile_height * pos_y)

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
        if self.image_gif != image_group[direction]:
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
        if self.count % self.main.shooting_tick_delay == 0:
            Bullet(self.rect.x + self.main.player_size_x // 2 - 5,
                   self.rect.y + self.main.player_size_y // 2 - 5,
                   "Images/tear_", direction, 5, self.main.player_group, self.main)
        self.count += 1

    def check_player_coords(self):
        if (self.main.player.rect.x - 10 <= self.rect.x <= self.main.player.rect.x + 10 and
                self.main.player.rect.y <= self.rect.y):
            self.shoot(0)
            return True
        elif (self.main.player.rect.x - 10 <= self.rect.x <= self.main.player.rect.x + 10 and
              self.main.player.rect.y >= self.rect.y):
            self.shoot(2)
            return True
        elif (self.main.player.rect.y - self.main.player_size_y
              <= self.rect.y <= self.main.player.rect.y + self.main.player_size_x and
              self.main.player.rect.x <= self.rect.x):
            self.shoot(3)
            return True
        elif (self.main.player.rect.y - self.main.player_size_y
              <= self.rect.y <= self.main.player.rect.y + self.main.player_size_x and
              self.main.player.rect.x >= self.rect.x):
            self.shoot(1)
            return True
        else:
            self.change_image(self.images, -1)

    def check_collision(self):
        if pygame.sprite.spritecollideany(self, self.main.bullet_group, False):
            if pygame.sprite.spritecollideany(self, self.main.bullet_group,
                                              False).sprites_to_damage == self.main.enemy_group:
                self.hp -= self.main.player.attack()
                if self.hp - self.main.player.attack() <= 0:
                    self.kill()
                print('Ouch!', self.hp)
        if pygame.sprite.spritecollideany(self, self.main.player_group, False):
            print('Go away!')

    def move(self):
        if self.room.find_way(self.get_pos(self.rect.x, self.rect.y),
                              self.get_pos(self.room.player.rect.x, self.room.player.rect.y)):
            x1, y1 = self.room.find_way(self.get_pos(self.rect.x, self.rect.y),
                                        self.get_pos(self.room.player.rect.x,
                                                     self.room.player.rect.y))[-1]
            if self.rect.y < y1 * 50:
                collision_test_rect = pygame.Rect((self.rect.x, self.rect.y + self.speed),
                                                  (self.main.player_size_x, self.main.player_size_y))
                if collision_test_rect.collidelist(
                        [elem.rect if elem != self else pygame.Rect((0, 0), (0, 0)) for elem in
                         self.main.enemy_group]) == -1:
                    self.rect.y += self.speed
            elif self.rect.y > y1 * 50:
                collision_test_rect = pygame.Rect((self.rect.x, self.rect.y - self.speed),
                                                  (self.main.player_size_x, self.main.player_size_y))
                if collision_test_rect.collidelist(
                        [elem.rect if elem != self else pygame.Rect((0, 0), (0, 0)) for elem in
                         self.main.enemy_group]) == -1:
                    self.rect.y -= self.speed
            if self.rect.x < x1 * 50:
                collision_test_rect = pygame.Rect((self.rect.x + self.speed, self.rect.y),
                                                  (self.main.player_size_x, self.main.player_size_y))
                if collision_test_rect.collidelist(
                        [elem.rect if elem != self else pygame.Rect((0, 0), (0, 0)) for elem in
                         self.main.enemy_group]) == -1:
                    self.rect.x += self.speed
            elif self.rect.x > x1 * 50:
                collision_test_rect = pygame.Rect((self.rect.x - self.speed, self.rect.y),
                                                  (self.main.player_size_x, self.main.player_size_y))
                if collision_test_rect.collidelist(
                        [elem.rect if elem != self else pygame.Rect((0, 0), (0, 0)) for elem in
                         self.main.enemy_group]) == -1:
                    self.rect.x -= self.speed

    def get_pos(self, x, y):
        return x // 50, y // 50


class Player(pygame.sprite.Sprite):
    def __init__(self, room, pos_x, pos_y, image, shooting_image, direction, main,
                 parameters):
        super().__init__(main.player_group, main.all_sprites)
        self.running = None
        self.running = None
        self.reversed = None
        self.image_gif = None
        self.frames = None
        self.startpoint = None
        self.ptime = None
        self.cur = None
        self.breakpoint = None
        self.image = None
        self.main = main
        self.room = room
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
        self.rect = self.image.get_rect().move(self.main.tile_width * pos_x,
                                               self.main.tile_height * pos_y)

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

    def check_collision(self):
        if pygame.sprite.spritecollideany(self, self.main.bullet_group, False):
            if pygame.sprite.spritecollideany(self, self.main.bullet_group,
                                              False).sprites_to_damage == self.main.player_group:
                self.player_parameters[5] -= 1
                if self.player_parameters[5] <= 0:
                    self.main.game_over()
                print('Ouch!', self.player_parameters[5])

    def move(self, direction):
        self.change_direction(direction)
        player_speed = self.player_parameters[0]
        if direction == 0:
            collision_test_rect = pygame.Rect((self.rect.x, self.rect.y - player_speed),
                                              (self.main.player_size_x, self.main.player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem in
                     self.main.tiles_group]) == -1:
                self.rect.y -= player_speed
        if direction == 2:
            collision_test_rect = pygame.Rect((self.rect.x, self.rect.y + player_speed),
                                              (self.main.player_size_x, self.main.player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem in
                     self.main.tiles_group]) == -1:
                self.rect.y += player_speed
        if direction == 3:
            collision_test_rect = pygame.Rect((self.rect.x - player_speed, self.rect.y),
                                              (self.main.player_size_x, self.main.player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem in
                     self.main.tiles_group]) == -1:
                self.rect.x -= player_speed
        if direction == 1:
            collision_test_rect = pygame.Rect((self.rect.x + player_speed, self.rect.y),
                                              (self.main.player_size_x, self.main.player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem in
                     self.main.tiles_group]) == -1:
                self.rect.x += player_speed

    def shoot(self, direction):
        # TODO: анимация стрельбы
        self.change_image(self.shooting_images, direction)
        Bullet(self.rect.x + self.main.player_size_x // 2 - 5,
               self.rect.y + self.main.player_size_y // 2 - 5,
               "Images/bottle_", direction, self.main.player.player_parameters[3],
               self.main.enemy_group, self.main)

    def attack(self):
        return self.player_parameters[1] * self.player_parameters[2]

    def show_stats(self):
        pass

    def get_pos(self, x, y):
        return x // 50, y // 50


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image, direction, bullet_speed, sprites_to_damage, main):
        super().__init__(main.bullet_group, main.all_sprites)
        self.image = None
        self.main = main
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
        for elem in self.main.tiles_group:
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
    def __init__(self, pos_x, pos_y, main):
        super().__init__(main.artifact_group)
        self.main = main
        self.art_name = choice(list(self.main.art_parameters.keys()))
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.parameters = self.main.art_parameters[self.art_name][1]
        self.image = self.main.art_parameters[self.art_name][0]
        self.rect = self.image.get_rect().move(self.main.tile_width * pos_x + 10,
                                               self.main.tile_height * pos_y + 10)

    def check_collision(self):
        if pygame.sprite.spritecollide(self, self.main.player_group, False):
            print(self.main.player.player_parameters)
            for i in (0, 4, 3):
                if self.main.player.player_parameters[i] + int(
                        self.parameters[i] * self.main.player.player_parameters[i]) > 1:
                    self.main.player.player_parameters[i] += int(
                        self.parameters[i] * self.main.player.player_parameters[i])
                else:
                    self.main.player.player_parameters[i] = 1
            self.main.player.player_parameters[2] += (
                    self.parameters[2] * self.main.player.player_parameters[2] *
                    self.main.player.player_parameters[1])
            if self.parameters[1] > self.main.player.player_parameters[1]:
                self.main.player.player_parameters[1] = self.parameters[1]
            self.main.player.player_parameters[5] += self.parameters[5]
            self.main.player_parameters = self.main.player.player_parameters
            self.kill()
            print(self.main.player.player_parameters)
        if pygame.sprite.spritecollide(self, self.main.bullet_group, False):
            print('Ouch!')


app = Main()

pygame.quit()
