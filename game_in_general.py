import os
import sys
import time
from random import choice

import pygame
from PIL import Image
from pygame.locals import *


def load_image(name, colorkey=None):
    """
    Function for loading pictures from Images folders
    :param name: name of image which need to load
    :param colorkey: background color
    :return: loaded image
    """
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
    """
    Function for cutting GIF-files on frames
    :param obj: GIF-file
    :return: set of the frames
    """
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


def get_coords(coords, direction):
    """
    Function for room positioning
    :param coords: coordinates of the room with current direction
    :param direction: direction
    :return: next room coord
    """
    if direction == 0:
        return coords[0], coords[1] - 1
    if direction == 1:
        return coords[0] + 1, coords[1]
    if direction == 2:
        return coords[0], coords[1] + 1
    if direction == 3:
        return coords[0] - 1, coords[1]


class MusicAndSounds:
    def __init__(self, volume_coeff=1, music_coeff=1):
        """
        initialization of class MusicAndSounds
        :param volume_coeff: volume ratio
        :param music_coeff: music ratio
        """
        pygame.mixer.init()
        self.sound_path = 'Sounds/'
        self.music_path = 'Music/'
        self.stream = pygame.mixer.music
        self.volume_coeff = volume_coeff
        self.music_coeff = music_coeff

    def menu(self):
        """
        Start play music in menu.
        :return: None
        """
        self.stream.load(self.music_path + 'Gimn_punks_Red_plesen.mp3')
        self.stream.play()
        self.stream.set_volume(0.05 * self.music_coeff)

    def game(self, dir_name='Default_playlist'):
        """
        Start play music in game.
        :param dir_name: name of directory where is the playlist with music
        :return: None
        """
        self.stream.stop()
        game_fon = os.listdir(self.music_path + dir_name + '/')
        music_path = self.music_path + dir_name + '/'
        # game_fon = ['Changes_Roman(48)[RUS]', 'Good_night_Roman(48)[RUS]',
        #             'Gruppa_krovi_Roman(48)[RUS]', 'Star_with_name_Sun_Roman(48)[RUS]']
        self.stream.load(music_path + choice(game_fon))
        for _ in range(len(game_fon)):
            self.stream.queue(music_path + choice(game_fon))
        self.stream.play()
        self.stream.set_volume(0.05 * self.music_coeff)

    def artifact_get(self):
        """
        Function for play sound when hero pick up the artifact
        :return: None
        """
        sound = pygame.mixer.Sound(self.sound_path + 'Gulmen_Gde_zhe_etot_artefakt.wav')
        sound.play()
        sound.set_volume(0.1 * self.volume_coeff)

    def ouch(self, entity):
        """
        Function for play sound when hero/enemy get hit
        :param entity: who got hit
        :return: None
        """
        if entity == 'hero':
            sound = pygame.mixer.Sound(self.sound_path + 'Hero_ouch.wav')
            sound.set_volume(0.1 * self.volume_coeff)
        elif entity == 'enemy':
            sound = pygame.mixer.Sound(self.sound_path + 'Enemy_ouch.wav')
            sound.set_volume(0.05 * self.volume_coeff)
        sound.play()

    def shoot(self, entity):
        """
        Function for play sound when hero/enemy shoot
        :param entity: who got hit
        :return:
        """
        if entity == 'hero':
            sound = pygame.mixer.Sound(self.sound_path + 'Hero_throw.ogg')
            sound.set_volume(0.1 * self.volume_coeff)  # TODO пофиксить воспроизведение
        elif entity == 'enemy':
            sound = pygame.mixer.Sound(self.sound_path + 'Enemy_shoot.wav')
            sound.set_volume(0.01 * self.volume_coeff)
        sound.play()


class Button(pygame.sprite.Sprite):
    def __init__(self, screen, menu_button_group, x, y, image, selected_image, selected,
                 clicked_func):
        """
        initialization of class Button
        :param screen: screen where this button locate
        :param menu_button_group: group of menu buttons
        :param image: Image that displays an unselected button
        :param selected_image: Image that displays an selected button
        :param selected: Parameters shows is this button selected from the start
        :param clicked_func: what should the button do when it clicked
        """
        super().__init__(menu_button_group)
        self.menu_button_group = menu_button_group
        self.screen = screen
        self.not_selected_image = load_image(image)
        self.selected_image = load_image(selected_image)
        self.selected = selected
        if self.selected:
            self.image = self.selected_image
        else:
            self.image = self.not_selected_image

        self.clicked_func = clicked_func
        self.rect = self.image.get_rect().move(x, y)

    def check_mouse_pos(self, pos):
        """
        Function is checking a mouse position and if it collide the button rectangle image change
        :param pos: mouse position
        :return: None
        """
        if self.rect.collidepoint(pos):
            self.image = self.selected_image
        else:
            self.image = self.not_selected_image

    def check_click(self, pos):
        """
        Function is checking a mouse position and called a function if button clicked
        :param pos: mouse position
        :return: None
        """
        if self.rect.collidepoint(pos):
            if self.clicked_func:
                self.clicked_func()


class Main:
    def __init__(self):
        self.music = MusicAndSounds()
        self.size = self.WIDTH, self.HEIGHT = 850, 650
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.player_image_file = 'Images/Entities/Hero/Red_'
        self.player_shoot_file = 'Images/Entities/Hero/Red_run_'
        self.vol_set_image, self.mus_set_image = 2, 2
        self.volume_stages = ['sound_0_button.png', 'sound_1_button.png', 'sound_2_button.png',
                              'sound_3_button.png', 'sound_4_button.png']
        self.diff_stages = ['easy_diff_button.png', 'medium_diff_button.png', 'hard_diff_button.png']
        self.selected_diff_stages = ['easy_diff_selected_button.png',
                                     'medium_diff_selected_button.png',
                                     'hard_diff_selected_button.png']
        self.diff_image = 1
        self.cell_size, self.player_size_x, self.player_size_y = 50, 50, 50
        self.tile_images = {
            'wall': pygame.transform.scale(load_image('Tiles/wall.png'),
                                           (self.cell_size, self.cell_size)),
            'empty': pygame.transform.scale(load_image('Tiles/floor.png'),
                                            (self.cell_size, self.cell_size)),
            'door_up': pygame.transform.scale(load_image('Tiles/door.png'),
                                              (self.cell_size, self.cell_size)),
            'door_right': pygame.transform.rotate(load_image('Tiles/door.png'), 270),
            'door_down': pygame.transform.rotate(load_image('Tiles/door.png'), 180),
            'door_left': pygame.transform.rotate(load_image('Tiles/door.png'), 90),
            'door_up_closed': pygame.transform.scale(load_image('Tiles/door_closed.png'),
                                                     (self.cell_size, self.cell_size)),
            'door_right_closed': pygame.transform.rotate(load_image('Tiles/door_closed.png'), 270),
            'door_down_closed': pygame.transform.rotate(load_image('Tiles/door_closed.png'), 180),
            'door_left_closed': pygame.transform.rotate(load_image('Tiles/door_closed.png'), 90),
            'hole': pygame.transform.scale(load_image('Tiles/hole.png'),
                                           (self.cell_size, self.cell_size)),
            'rock': pygame.transform.scale(load_image('Tiles/rock.png', -1),
                                           (self.cell_size, self.cell_size))}
        self.tile_width, self.tile_height = 50, 50

        self.room_types = ["circle", "circle_in_square", "death_road", "diagonal", "lines", "mexico",
                           "square_trap", "trapezoid", 'loner', 'tiger', 'punks_and_rocks', 'house',
                           'rocks', 'pyramid', 'lizard', 'romb', 'boloto']
        self.running = True
        # player_hp\boss_hp\enemy_hp\enemy_shoot_speed\enemy_speed
        self.diff_parameters = [[12, 100, 25, 60, 1], [6, 200, 50, 10, 2], [6, 350, 65, 5, 4]]
        # player_speed\player_damage_coeff\player_damage\bullet_speed\shooting_ticks\hp\change_player
        self.art_parameters = {
            'meat': (load_image('Artifacts/meat.png', -1), (0, 0, 1, 0, 0, 1, False)),
            'sandwich': (
                load_image('Artifacts/sandwich.png', -1), (0, 0, 0, 0, 0, 1, False)),
            'breakfast': (
                load_image('Artifacts/breakfast.png', -1), (0, 0, 0, 0, 0, 1, False)),
            'soup': (load_image('Artifacts/soup.png', -1), (0, 0, 0, 0, 0, 1, False)),
            'onion': (load_image('Artifacts/onion.png', -1), (0, 0, 0, 0.7, 0, False)),
            'screw': (
                load_image('Artifacts/screw.png', -1), (0, 0, 0, 0.3, -0.2, False)),
            'amulet': (
                load_image('Artifacts/amulet.png', -1), (0, 0, 1, 0, 0, 0, False)),
            'dead_cat': (
                load_image('Artifacts/dead_cat.png', -1), (0, 1.5, 1, 0, 0, 0, False)),
            'mineral_water': (
                load_image('Artifacts/mineral_water.png', -1),
                (0, 0, 0.5, 0, 0, 0, False)),
            'good_morning': (
                load_image('Artifacts/good_morning.png', -1),
                (0, 0, 0.5, 0, -0.7, 1, False)),
            'eye': (
                load_image('Artifacts/eye.png', -1), (0, 2, 4, -1.5, 1.25, 0, False)),
            'prize': (load_image('Artifacts/Winner.png', -1), (0, 0, 0, 0, 0, 0, True))}

        self.counter = 0
        self.shooting_tick_delay = self.diff_parameters[self.diff_image][3]

        self.all_sprites, self.tiles_group, self.artifact_group = None, None, None
        self.player_group, self.bullet_group, self.enemy_group = None, None, None
        self.buttons_group = None
        self.game_map = None
        self.player = None
        self.room = None
        self.game_in_process = False

        self.menu()

    def load_map(self, rooms_count):
        """
        Load a game map
        :param rooms_count: How many rooms in one direction
        :return: None
        """
        self.game_map = Map(rooms_count, self)

    def load_room(self, direction):
        """
        Load the current room
        # TODO Добавь описание
        :param direction: direction of the room
        :return: None
        """
        self.all_sprites, self.tiles_group = pygame.sprite.Group(), pygame.sprite.Group()
        self.artifact_group, self.player_group = pygame.sprite.Group(), pygame.sprite.Group()
        self.bullet_group, self.enemy_group = pygame.sprite.Group(), pygame.sprite.Group()
        self.room = self.game_map.get_current_room()
        self.room.get_level(direction)
        self.player = self.room.player
        self.game_map.update_doors()

    def menu(self):
        """
        Show a menu screen and starts playing music in the menu
        :return: None
        """
        if not self.game_in_process:
            pygame.mouse.set_visible(1)
            self.music.menu()
            self.buttons_group = pygame.sprite.Group()
            fon = pygame.transform.scale(load_image('fon_menu.png'), (self.WIDTH, self.HEIGHT))
            self.screen.blit(fon, (0, 0))

            Button(self.screen, self.buttons_group, 250, 150, "Buttons/Start_button.png",
                   "Buttons/Start_selected_button.png", False,
                   self.start_game)
            Button(self.screen, self.buttons_group, 450, 375,
                   'Buttons/' + self.diff_stages[self.diff_image],
                   'Buttons/' + self.diff_stages[self.diff_image], False, None)
            Button(self.screen, self.buttons_group, 250, 250, "Buttons/Setting_button.png",
                   "Buttons/Setting_selected_button.png", False, self.settings)
            Button(self.screen, self.buttons_group, 250, 350, "Buttons/Autors_button.png",
                   "Buttons/Autors_selected_button.png", False, self.autors_show)
            Button(self.screen, self.buttons_group, 250, 450, "Buttons/Exit_button.png",
                   "Buttons/Exit_selected_button.png", False, self.terminate)
        else:
            pygame.mouse.set_visible(1)
            self.music.menu()
            self.buttons_group = pygame.sprite.Group()
            fon = pygame.transform.scale(load_image('fon_menu.png'), (self.WIDTH, self.HEIGHT))
            self.screen.blit(fon, (0, 0))

            Button(self.screen, self.buttons_group, 450, 375,
                   'Buttons/' + self.diff_stages[self.diff_image],
                   'Buttons/' + self.diff_stages[self.diff_image], False, None)
            Button(self.screen, self.buttons_group, 250, 150, "Buttons/Continue_button.png",
                   "Buttons/Continue_selected_button.png", False, self.start_game)
            Button(self.screen, self.buttons_group, 250, 250, "Buttons/Setting_button.png",
                   "Buttons/Setting_selected_button.png", False, self.settings)
            Button(self.screen, self.buttons_group, 250, 350, "Buttons/Exit_button.png",
                   "Buttons/Exit_selected_button.png", False, self.terminate)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.MOUSEMOTION:
                    for button in self.buttons_group:
                        button.check_mouse_pos(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for elem in self.buttons_group:
                        elem.check_click(event.pos)

            self.buttons_group.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

    def congratulations(self):
        pygame.mouse.set_visible(1)
        fon = pygame.transform.scale(load_image('fon_menu.png'), (self.WIDTH, self.HEIGHT))
        self.buttons_group = pygame.sprite.Group()
        self.screen.blit(fon, (0, 0))
        Button(self.screen, self.buttons_group, 250, 350, "Buttons/Start_button.png",
               "Buttons/Start_selected_button.png", False,
               self.start_game)
        Button(self.screen, self.buttons_group, 350, 175, "Artifacts/Winner.png",
               "Artifacts/Winner.png", False,
               self.start_game)
        Button(self.screen, self.buttons_group, 350, 425, "Buttons/Back_button.png",
               "Buttons/Back_selected_button.png", False, self.menu)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.MOUSEMOTION:
                    for button in self.buttons_group:
                        button.check_mouse_pos(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for elem in self.buttons_group:
                        elem.check_click(event.pos)
            self.buttons_group.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

    def settings(self):
        """
        Show a settings screen
        :return: None
        """
        fon = pygame.transform.scale(load_image('fon_menu.png'), (self.WIDTH, self.HEIGHT))
        self.buttons_group = pygame.sprite.Group()
        self.screen.blit(fon, (0, 0))
        # Volume
        Button(self.screen, self.buttons_group, 215, 150, "Buttons/vol_button.png",
               "Buttons/vol_selected_button.png", False, None)
        Button(self.screen, self.buttons_group, 325, 150, "Buttons/settings_left_button.png",
               "Buttons/settings_left_selected_button.png", False, self.change_settings_sound_low)
        Button(self.screen, self.buttons_group, 575, 150, "Buttons/settings_right_button.png",
               "Buttons/settings_right_selected_button.png", False, self.change_settings_sound_high)
        Button(self.screen, self.buttons_group, 365, 150,
               'Buttons/' + self.volume_stages[self.vol_set_image],
               'Buttons/' + self.volume_stages[self.vol_set_image], False, None)
        # Music
        Button(self.screen, self.buttons_group, 215, 250, "Buttons/mus_button.png",
               "Buttons/mus_selected_button.png", False, None)
        Button(self.screen, self.buttons_group, 325, 250, "Buttons/settings_left_button.png",
               "Buttons/settings_left_selected_button.png", False, self.change_settings_music_low)
        Button(self.screen, self.buttons_group, 575, 250, "Buttons/settings_right_button.png",
               "Buttons/settings_right_selected_button.png", False, self.change_settings_music_high)
        Button(self.screen, self.buttons_group, 365, 250,
               'Buttons/' + self.volume_stages[self.mus_set_image],
               'Buttons/' + self.volume_stages[self.mus_set_image], False, None)
        # Difficulty
        Button(self.screen, self.buttons_group, 450, 375,
               'Buttons/' + self.diff_stages[self.diff_image],
               'Buttons/' + self.selected_diff_stages[self.diff_image], False,
               self.change_settings_difficult)
        if not self.game_in_process:
            Button(self.screen, self.buttons_group, 275, 425, "Buttons/Back_button.png",
                   "Buttons/Back_selected_button.png", False, self.menu)
        else:
            Button(self.screen, self.buttons_group, 250, 450, "Buttons/Continue_button.png",
                   "Buttons/Continue_selected_button.png", False,
                   self.start_game)

        # TODO сделай так чтобы можно было вписать нужную папку или просто выбрать
        #  между двумя папками (или папками которые находятся в Sounds)

        # Прибавить\убавить звук в игре(без звука\тихо\норма\громко\бассбустед)
        # Прибавить\убавить музыку
        # Сложность (для детей\средний\для профи)
        # Плейлист (имя папки с музыкой в папке Sounds, где все файлы в формате mp3, wav или ogg)

    # TODO переформатировать эти функции
    def change_settings_sound_high(self):
        """
        Function to increase sound
        :return: None
        """
        self.vol_set_image = (self.vol_set_image + 1) % len(self.volume_stages)
        self.music.volume_coeff = 1.5 * self.vol_set_image
        self.settings()
        self.music.menu()

    def change_settings_sound_low(self):
        # поправить
        """
        Function to reduce sound
        :return: None
        """
        self.vol_set_image = self.vol_set_image - 1 if self.vol_set_image > 0 else len(
            self.volume_stages)
        self.music.volume_coeff = 1.5 * self.vol_set_image
        self.settings()
        self.music.menu()

    def change_settings_music_high(self):
        """
        Function to increase music
        :return: None
        """
        self.mus_set_image = (self.mus_set_image + 1) % len(self.volume_stages)
        self.music.music_coeff = 1.5 * self.mus_set_image
        self.settings()
        self.music.menu()

    def change_settings_music_low(self):
        # поправить
        """
        Function to reduce sound
        :return: None
        """
        self.mus_set_image = self.mus_set_image - 1 if self.vol_set_image >= 0 else len(
            self.volume_stages)
        self.music.music_coeff = 1.5 * self.mus_set_image
        self.settings()
        self.music.menu()

    def change_settings_difficult(self):
        """
        Function for changing difficulty level
        :return: None
        """
        self.diff_image = (self.diff_image + 1) % len(self.diff_stages)
        self.settings()

    def start_game(self):
        """
        This function start the game process
        :return: None
        """
        self.game_in_process = True
        pygame.mouse.set_visible(0)
        self.music.game()
        self.player_parameters = [5, 1, 3.5, 5, 21, self.diff_parameters[self.diff_image][0]]
        self.load_map(5)
        self.load_room(0)
        self.main_cycle()

    def autors_show(self):
        """
        Function to show a authors screen
        :return: None
        """
        fon = pygame.transform.scale(load_image('fon_menu.png'), (self.WIDTH, self.HEIGHT))
        text = "Урвачев Роман и Зотова Екатерина"
        self.buttons_group = pygame.sprite.Group()
        self.screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_rendered = font.render(text, 1, pygame.Color('black'))
        self.screen.blit(text_rendered, (250, 250))
        Button(self.screen, self.buttons_group, 250, 300, "Buttons/Start_button.png",
               "Buttons/Start_selected_button.png", False,
               self.start_game)
        Button(self.screen, self.buttons_group, 275, 425, "Buttons/Back_button.png",
               "Buttons/Back_selected_button.png", False, self.menu)

    def show_stats(self):
        """
        Function to show hero stats during the game
        :return: None
        """
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
        """
        Function to show the endgame screen
        :return: None
        """
        pygame.mouse.set_visible(1)
        self.buttons_group = pygame.sprite.Group()
        text = "Гамовер"
        fon = pygame.transform.scale(load_image('fon_menu.png'), (self.WIDTH, self.HEIGHT))
        self.screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 100)
        text_rendered = font.render(text, 1, pygame.Color('black'))
        self.screen.blit(text_rendered, (250, 175))

        Button(self.screen, self.buttons_group, 250, 250, "Buttons/Continue_button.png",
               "Buttons/Continue_selected_button.png", False,
               self.start_game)
        Button(self.screen, self.buttons_group, 250, 350, "Buttons/Setting_button.png",
               "Buttons/Setting_selected_button.png", False, self.settings)
        Button(self.screen, self.buttons_group, 250, 450, "Buttons/Exit_button.png",
               "Buttons/Exit_selected_button.png", False, self.terminate)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.MOUSEMOTION:
                    for button in self.buttons_group:
                        button.check_mouse_pos(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for elem in self.buttons_group:
                        elem.check_click(event.pos)
            self.buttons_group.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

    def terminate(self):
        """
        Close the game window
        :return: None
        """
        pygame.quit()
        sys.exit()

    def reset(self):
        """
        reinitialization of class Main
        :return: None
        """
        self.__init__()

    def draw_map(self, numb):
        if numb == 3:
            room_x, room_y = self.game_map.current_x, self.game_map.current_y - 1
            for y in range(numb):
                count = 0
                for x in range(-1, 2):
                    room = self.game_map.map[room_y][room_x + x]
                    if room:
                        pygame.draw.rect(self.screen, pygame.Color('black'), (
                            x * 40 + 700, y * 40 + 50,
                            40, 40), 1)
                    if room is not None and (room.enemies_init or room.artifacts_init):
                        pygame.draw.rect(self.screen, pygame.Color('black'), (
                            x * 40 + 700, y * 40 + 50,
                            40, 40), 0)
                    if room == self.game_map.map[self.game_map.current_y][self.game_map.current_x]:
                        pygame.draw.rect(self.screen, pygame.Color('red'), (
                            x * 40 + 700, y * 40 + 50,
                            40, 40), 0)
                    count += 1
                room_y += 1
        else:
            room_x, room_y = self.game_map.current_x, self.game_map.current_y - 2
            for y in range(numb):
                count = 0
                for x in range(-1, 2):
                    room = self.game_map.map[room_y][room_x + x]
                    if room:
                        pygame.draw.rect(self.screen, pygame.Color('black'), (
                            x * 40 + 650, y * 40 + 50,
                            40, 40), 1)
                    if room == self.game_map.map[self.game_map.current_y][self.game_map.current_x]:
                        pygame.draw.rect(self.screen, pygame.Color('red'), (
                            x * 40 + 650, y * 40 + 50,
                            40, 40), 0)
                    if room is not None and (room.enemies_init or room.artifacts_init):
                        pygame.draw.rect(self.screen, pygame.Color('black'), (
                            x * 40 + 650, y * 40 + 50,
                            40, 40), 0)
                    count += 1
                room_y += 1

    def main_cycle(self):
        """
        The main game cycle
        :return: None
        """
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
                self.game_in_process = True
                self.menu()
            if keys[pygame.K_LSHIFT] == 1:
                self.draw_map(5)
            else:
                self.draw_map(3)
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
        """
        initialization he class Room
        :param filename: name of the file from which the room map is loaded
        :param main: parameter for accessing the main class
        """
        self.main = main
        self.enemies_init, self.artifacts_init = True, True
        self.filename, self.exits, self.enemies, self.room_map = filename, [], 0, []
        self.artifacts, self.boss = 0, False
        self.door_up, self.door_right, self.door_down, self.door_left = None, None, None, None
        self.load_level(self.filename + ".txt")
        self.player, self.width, self.height = None, None, None

    def get_level(self, direction):
        """
        Selection of a room with the necessary direction
        :param direction: the direction needed
        :return: None
        """
        self.player, self.width, self.height = self.generate_level(
            self.load_level(self.filename + ".txt"), direction)

    def load_level(self, filename):
        """
        Reform text file in map. Map type is list of lists where all objects are just sign
        :param filename: the name of text file from what the level map load
        :return: list of lists
        """
        filename = "Levels/" + filename
        # читаем уровень, убирая символы перевода строки
        with open(filename, 'r') as mapFile:
            for line in mapFile:
                self.exits = list(map(int, line.split()))
                break
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        for elem in list(map(lambda x: x.ljust(max_width, '.'), level_map)):
            self.room_map.append(
                list(map(lambda x: 0 if x in ["#", "0", "^", "<", ">", "v", "R"] else -1, elem)))

        return list(map(lambda x: x.ljust(max_width, '.'), level_map))

    def generate_level(self, level, player_direction):
        """
        Tranform signs in level into classes
        :param level: level map
        :param player_direction: direction of player
        :return: player and his location in the rooms on the map
        """
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
                    if self.enemies_init:
                        Enemy(self, x, y, "Images/Entities/Enemies/Cop_",
                              "Images/Entities/Enemies/Cop_shoot_",
                              -1, self.main)
                        self.enemies += 1
                    Tile('empty', x, y, False, False, False, self.main)
                elif level[y][x] == 'B':
                    if self.enemies_init:
                        Boss(self, x, y, 'Images/Entities/Boss/boss_r_',
                             'Images/Entities/Boss/boss_shoot_', -1, self.main)
                        self.enemies += 1
                        self.boss = True
                    Tile('empty', x, y, False, False, False, self.main)
                if level[y][x] == 'R':
                    Tile('rock', x, y, True, True, False, self.main)
                elif level[y][x] == '0':
                    Tile('hole', x, y, True, False, True, self.main)
                elif level[y][x] == "A":
                    Tile('empty', x, y, False, False, False, self.main)
                    if self.artifacts_init:
                        self.artifacts += 1
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
        self.artifacts_init, self.enemies_init = False, False
        return new_player, x, y

    def find_way(self, coords1, coords2):
        """
        Function for enemies to find the shortest way o player
        :param coords1: coords enemy
        :param coords2: coords player
        :return:
        """
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
        """
        initialization of class Map
        :param rooms_count: room in one direction
        :param main: parameter for accessing the main class
        """
        self.rooms_count = rooms_count
        self.rooms = []
        self.map = [[None] * (2 * rooms_count + 2) for _ in range(2 * rooms_count + 2)]
        self.current_x = rooms_count
        self.current_y = rooms_count
        self.main = main
        self.generate_map()

    def generate_map(self):
        """
        Generate stage map
        :return: None
        """
        x, y = self.current_x, self.current_y
        self.map[y][x] = Room("start", self.main)
        self.rooms.append(Room("start", self.main))

        special_rooms_directions = {}

        directions = [0, 1, 2, 3]
        for elem in ['boss_room', "artifact_room", "shop"]:
            direction = choice(directions)
            special_rooms_directions[direction] = elem
            directions.remove(direction)

        directions = [0, 1, 2, 3]

        for main_direction in directions:
            x, y = self.current_x, self.current_y
            for i in range(self.rooms_count):
                if i in range(2):
                    direction = main_direction
                    x, y = get_coords((x, y), direction)
                else:
                    direction = choice(self.rooms[-1].exits)
                    coords = get_coords((x, y), direction)
                    while (self.map[coords[1]][coords[0]] is not None or
                           (direction + 2) % 4 == main_direction):
                        direction = choice(self.rooms[-1].exits)
                        coords = get_coords((x, y), direction)
                    x, y = get_coords((x, y), direction)

                if i != self.rooms_count - 1:
                    room = Room(choice(self.main.room_types), self.main)
                    while (direction + 2) % 4 not in room.exits or not self.room_check_neighbours(
                            room, x, y):
                        room = Room(choice(self.main.room_types), self.main)
                else:
                    if main_direction in special_rooms_directions:
                        room = Room(special_rooms_directions[main_direction], self.main)

                self.map[y][x] = room
                self.rooms.append(room)

        self.update_doors()
        for elem in self.map:
            for elem1 in elem:
                if elem1:
                    print(elem1.filename[0:2], end=" ")
                else:
                    print("  ", end=" ")
            print()

    def room_check_neighbours(self, room, x, y):
        """
        Checking the neighbours room location
        :param room: room for which you need to check neighbors
        :param x: ordinat of this room
        :param y: abciss of this room
        :return: have this room the right neighbor
        """
        for elem in room.exits:
            coords = get_coords((x, y), elem)
            if not self.map[coords[1]][coords[0]]:
                return True
        return False

    def get_current_room(self):
        return self.map[self.current_y][self.current_x]

    def check_door(self):
        """
        Check can there be a door in this direction
        :return: True/False and direction
        """
        current_room = self.map[self.current_y][self.current_x]
        if current_room.door_up is not None:
            if pygame.sprite.collide_rect_ratio(0.5)(current_room.player, current_room.door_up):
                if self.map[self.current_y - 1][self.current_x] is not None:
                    self.current_y -= 1
                    return True, 2
        if current_room.door_right is not None:
            if pygame.sprite.collide_rect_ratio(0.5)(current_room.player, current_room.door_right):
                if self.map[self.current_y][self.current_x + 1] is not None:
                    self.current_x += 1
                    return True, 3
        if current_room.door_down is not None:
            if pygame.sprite.collide_rect_ratio(0.5)(current_room.player, current_room.door_down):
                if self.map[self.current_y + 1][self.current_x] is not None:
                    self.current_y += 1
                    return True, 0
        if current_room.door_left is not None:
            if pygame.sprite.collide_rect_ratio(0.5)(current_room.player, current_room.door_left):
                if self.map[self.current_y][self.current_x - 1] is not None:
                    self.current_x -= 1
                    return True, 1
        return False, 0

    def update_doors(self):
        """
        Change the door images if it needs
        :return: None
        """
        current_room = self.map[self.current_y][self.current_x]
        room_up = self.map[self.current_y - 1][self.current_x]
        room_right = self.map[self.current_y][self.current_x + 1]
        room_down = self.map[self.current_y + 1][self.current_x]
        room_left = self.map[self.current_y][self.current_x - 1]

        if current_room.door_up is not None:
            if current_room.enemies != 0 or current_room.artifacts != 0:
                current_room.door_up.image = self.main.tile_images[
                    'door_up_closed']
                current_room.door_up.block_player = True
            else:
                current_room.door_up.image = self.main.tile_images[
                    'door_up']
                current_room.door_up.block_player = False

            if not room_up:
                current_room.door_up.image = self.main.tile_images[
                    'door_up_closed']
                current_room.door_up.block_player = True
            elif 2 not in room_up.exits:
                current_room.door_up.image = self.main.tile_images[
                    'door_up_closed']
                current_room.door_up.block_player = True

        if current_room.door_right is not None:
            if current_room.enemies != 0 or current_room.artifacts != 0:
                current_room.door_right.image = self.main.tile_images[
                    'door_right_closed']
                current_room.door_right.block_player = True
            else:
                current_room.door_right.image = self.main.tile_images[
                    'door_right']
                current_room.door_right.block_player = False

            if not room_right:
                current_room.door_right.image = self.main.tile_images[
                    'door_right_closed']
                current_room.door_right.block_player = True
            elif 3 not in room_right.exits:
                current_room.door_right.image = self.main.tile_images[
                    'door_right_closed']
                current_room.door_right.block_player = True

        if current_room.door_down is not None:
            if current_room.enemies != 0 or current_room.artifacts != 0:
                current_room.door_down.image = self.main.tile_images[
                    'door_down_closed']
                current_room.door_down.block_player = True
            else:
                current_room.door_down.image = self.main.tile_images[
                    'door_down']
                current_room.door_down.block_player = False

            if not room_down:
                current_room.door_down.image = self.main.tile_images[
                    'door_down_closed']
                current_room.door_down.block_player = True
            elif 0 not in room_down.exits:
                current_room.door_down.image = self.main.tile_images[
                    'door_down_closed']
                current_room.door_down.block_player = True

        if current_room.door_left is not None:
            if current_room.enemies != 0 or current_room.artifacts != 0:
                current_room.door_left.image = self.main.tile_images[
                    'door_left_closed']
                current_room.door_left.block_player = True
            else:
                current_room.door_left.image = self.main.tile_images[
                    'door_left']
                current_room.door_left.block_player = False

            if not room_left:
                current_room.door_left.image = self.main.tile_images[
                    'door_left_closed']
                current_room.door_left.block_player = True
            elif 1 not in room_left.exits:
                current_room.door_left.image = self.main.tile_images[
                    'door_left_closed']
                current_room.door_left.block_player = True
        if current_room.enemies == 0 and current_room.boss:
            Artifact(7, 5, self.main, winner=True)
            #self.main.congratulations()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, block_player, block_bullets, damage_player, main):
        """
        Initialization of class Tile
        :param tile_type: type of tile
        :param pos_x: tile position x
        :param pos_y: tile position y
        :param block_player: must this tile block player motion
        :param block_bullets: must this tile block bullet motion
        :param damage_player: must tis tile damage player
        :param main: parameter for accessing the main class
        """
        super().__init__(main.tiles_group, main.all_sprites)
        self.image = main.tile_images[tile_type]
        self.rect = self.image.get_rect().move(main.tile_width * pos_x, main.tile_height * pos_y)
        self.block_player = block_player
        self.block_bullets = block_bullets
        self.damage_player = damage_player


class Enemy(pygame.sprite.Sprite):
    def __init__(self, room, pos_x, pos_y, image, shooting_image, direction, main):
        """
                Initialization of class Enemy
                :param room: parameter for accessing the room class
                :param pos_x: Enemy position x
                :param pos_y: Enemy position y
                :param image: file which plays when entity run
                :param shooting_image: file which plays when entity shoot
                :param direction: direction where entity look after spawn
                :param main: parameter for accessing the main class
                """
        super().__init__(main.enemy_group, main.all_sprites)
        self.running, self.reversed, self.image_gif, self.frames = None, None, None, None
        self.startpoint, self.ptime, self.breakpoint, self.image = None, None, None, None
        self.image, self.main, self.room, self.map, self.x = None, main, room, Map, pos_x
        self.direction, self.y, self.count = direction, pos_y, 0
        self.hp = main.diff_parameters[main.diff_image][2]
        self.speed = main.diff_parameters[main.diff_image][4]
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
        """
        change the image in the right direction
        :param image_group:
        :param direction:
        :return: None
        """
        if self.image_gif != image_group[direction]:
            self.running, self.reversed, self.image_gif = True, False, image_group[direction]
            self.frames, self.startpoint, self.cur, = [], 0, 0
            self.ptime = time.time()
            get_frames(self)
            self.breakpoint = len(self.frames) - 1
            self.render()
            self.direction = direction

    def shoot(self, direction):
        """
        Function for the enemy to shoot
        :param direction: where enemy must shoot
        :return: None
        """
        self.main.music.shoot('enemy')
        self.change_image(self.shooting_images, direction)
        if self.count % self.main.shooting_tick_delay == 0:
            Bullet(self.rect.x + self.main.player_size_x // 2 - 5,
                   self.rect.y + self.main.player_size_y // 2 - 5,
                   "Images/Bullets/tear_", direction, 5, self.main.player_group, self.main)
        self.count += 1

    def check_player_coords(self):
        """
        Function which check the player position
        :return: can enemy shoot or not
        """
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
        """
        Check collision between enemy and other subjects
        :return: None
        """
        if pygame.sprite.spritecollideany(self, self.main.bullet_group, False):
            if pygame.sprite.spritecollideany(self, self.main.bullet_group,
                                              False).sprites_to_damage == self.main.enemy_group:
                self.hp -= self.main.player.attack()
                self.main.music.ouch('enemy')
                if self.hp - self.main.player.attack() <= 0:
                    self.kill()
                    self.room.enemies -= 1
                    if self.room.enemies == 0:
                        self.main.game_map.update_doors()

                print('Ouch!', self.hp)
        # if pygame.sprite.spritecollideany(self, self.main.player_group, False):
        #     print('Go away!')

    def move(self):
        """
        Function for move enemiies
        :return: None
        """
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
                    if collision_test_rect.collidelist(
                            [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem
                             in
                             self.main.tiles_group]) == -1:
                        if collision_test_rect.collidelist(
                                [elem.rect for elem in self.main.player_group]) == -1:
                            self.rect.y += self.speed
            elif self.rect.y > y1 * 50:
                collision_test_rect = pygame.Rect((self.rect.x, self.rect.y - self.speed),
                                                  (self.main.player_size_x, self.main.player_size_y))
                if collision_test_rect.collidelist(
                        [elem.rect if elem != self else pygame.Rect((0, 0), (0, 0)) for elem in
                         self.main.enemy_group]) == -1:
                    if collision_test_rect.collidelist(
                            [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem
                             in
                             self.main.tiles_group]) == -1:
                        if collision_test_rect.collidelist(
                                [elem.rect for elem in self.main.player_group]) == -1:
                            self.rect.y -= self.speed
            if self.rect.x < x1 * 50:
                collision_test_rect = pygame.Rect((self.rect.x + self.speed, self.rect.y),
                                                  (self.main.player_size_x, self.main.player_size_y))
                if collision_test_rect.collidelist(
                        [elem.rect if elem != self else pygame.Rect((0, 0), (0, 0)) for elem in
                         self.main.enemy_group]) == -1:
                    if collision_test_rect.collidelist(
                            [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem
                             in
                             self.main.tiles_group]) == -1:
                        if collision_test_rect.collidelist(
                                [elem.rect for elem in self.main.player_group]) == -1:
                            self.rect.x += self.speed
            elif self.rect.x > x1 * 50:
                collision_test_rect = pygame.Rect((self.rect.x - self.speed, self.rect.y),
                                                  (self.main.player_size_x, self.main.player_size_y))
                if collision_test_rect.collidelist(
                        [elem.rect if elem != self else pygame.Rect((0, 0), (0, 0)) for elem in
                         self.main.enemy_group]) == -1:
                    if collision_test_rect.collidelist(
                            [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem
                             in
                             self.main.tiles_group]) == -1:
                        if collision_test_rect.collidelist(
                                [elem.rect for elem in self.main.player_group]) == -1:
                            self.rect.x -= self.speed

    def get_pos(self, x, y):
        return x // 50, y // 50


class Boss(Enemy):
    def __init__(self, room, pos_x, pos_y, image, shooting_image, direction, main):
        """
                Initialization of class Enemy
                :param room: parameter for accessing the room class
                :param pos_x: Enemy position x
                :param pos_y: Enemy position y
                :param image: file which plays when entity run
                :param shooting_image: file which plays when entity shoot
                :param direction: direction where entity look after spawn
                :param main: parameter for accessing the main class
                """
        super().__init__(room, pos_x, pos_y, image, shooting_image, direction, main)
        self.running, self.reversed, self.image_gif, self.frames = None, None, None, None
        self.startpoint, self.ptime, self.breakpoint, self.image = None, None, None, None
        self.image, self.main, self.room, self.map, self.x = None, main, room, Map, pos_x
        self.direction, self.y, self.count = direction, pos_y, 0
        self.hp = main.diff_parameters[main.diff_image][1]
        self.speed = main.diff_parameters[main.diff_image][4]
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
        self.rect = self.image.get_rect().move(self.main.player_size_x * pos_x,
                                               self.main.player_size_y * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, room, pos_x, pos_y, image, shooting_image, direction, main,
                 parameters):
        """
        Initialization of class Player
        :param room: parameter for accessing the room class
        :param pos_x: Player position x
        :param pos_y: Player position y
        :param image: file which plays when entity run
        :param shooting_image: file which plays when entity shoot
        :param direction: direction where entity look after spawn
        :param main: parameter for accessing the main class
        """
        super().__init__(main.player_group, main.all_sprites)
        self.running, self.reversed, self.image_gif, self.frames = None, None, None, None
        self.startpoint, self.ptime, self.breakpoint, self.image = None, None, None, None
        self.cur, self.main, self.room, self.direction, \
        self.player_parameters = None, main, room, direction, parameters
        self.images = {0: Image.open(image + "run_up.gif"), 1: Image.open(image + "run_right.gif"),
                       2: Image.open(image + "run_down.gif"), 3: Image.open(image + "run_left.gif"),
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
        if self.image_gif != image_group[direction]:
            self.running, self.reversed, self.image_gif = True, False, image_group[direction]
            self.frames, self.startpoint, self.cur, = [], 0, 0
            self.ptime = time.time()
            get_frames(self)
            self.breakpoint = len(self.frames) - 1
            self.render()
            self.direction = direction

    def change_direction(self, direction):
        if direction != self.direction:
            self.change_image(self.images, direction)

    def check_collision(self):
        """
        Check collision between player and other subjects
        :return: None
        """
        if pygame.sprite.spritecollideany(self, self.main.bullet_group, False):
            if pygame.sprite.spritecollideany(self, self.main.bullet_group,
                                              False).sprites_to_damage == self.main.player_group:
                self.player_parameters[5] -= 1
                if self.player_parameters[5] <= 0:
                    self.main.game_over()
                print('Ouch!', self.player_parameters[5])
                self.main.music.ouch('hero')

    def move(self, direction):
        """
        Function for move player
        :return: None
        """
        self.change_direction(direction)
        player_speed = self.player_parameters[0]
        if direction == 0:
            collision_test_rect = pygame.Rect((self.rect.x, self.rect.y - player_speed),
                                              (self.main.player_size_x, self.main.player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem in
                     self.main.tiles_group]) == -1:
                if collision_test_rect.collidelist(
                        [elem.rect for elem in self.main.enemy_group]) == -1:
                    self.rect.y -= player_speed
        if direction == 2:
            collision_test_rect = pygame.Rect((self.rect.x, self.rect.y + player_speed),
                                              (self.main.player_size_x, self.main.player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem in
                     self.main.tiles_group]) == -1:
                if collision_test_rect.collidelist(
                        [elem.rect for elem in self.main.enemy_group]) == -1:
                    self.rect.y += player_speed
        if direction == 3:
            collision_test_rect = pygame.Rect((self.rect.x - player_speed, self.rect.y),
                                              (self.main.player_size_x, self.main.player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem in
                     self.main.tiles_group]) == -1:
                if collision_test_rect.collidelist(
                        [elem.rect for elem in self.main.enemy_group]) == -1:
                    self.rect.x -= player_speed
        if direction == 1:
            collision_test_rect = pygame.Rect((self.rect.x + player_speed, self.rect.y),
                                              (self.main.player_size_x, self.main.player_size_y))
            if collision_test_rect.collidelist(
                    [elem.rect if elem.block_player else pygame.Rect((0, 0), (0, 0)) for elem in
                     self.main.tiles_group]) == -1:
                if collision_test_rect.collidelist(
                        [elem.rect for elem in self.main.enemy_group]) == -1:
                    self.rect.x += player_speed

    def shoot(self, direction):
        """
        Function for the player to shoot
        :param direction: where player must shoot
        :return: None
        """
        self.change_image(self.shooting_images, direction)
        Bullet(self.rect.x + self.main.player_size_x // 2 - 5,
               self.rect.y + self.main.player_size_y // 2 - 5,
               "Images/Bullets/bottle_", direction, self.main.player.player_parameters[3],
               self.main.enemy_group, self.main)
        self.main.music.shoot('hero')

    def attack(self):
        return self.player_parameters[1] * self.player_parameters[2]

    def get_pos(self, x, y):
        return x // 50, y // 50


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image, direction, bullet_speed, sprites_to_damage, main):
        """
        Initializing of class Bullet
        :param x: Bullet position x
        :param y: Bullet position y
        :param image: file which plays when entity run
        :param direction: direction where entity look after spawn
        :param bullet_speed: bullet speed
        :param sprites_to_damage: which sprites need to damage
        :param main: parameter for accessing the main class
        """
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
        """
        Check collision between bullet and other subjects
        :return: None
        """
        if pygame.sprite.spritecollideany(self, self.walls):
            self.kill()
        if pygame.sprite.spritecollideany(self, self.sprites_to_damage):
            self.kill()

    def move(self):
        """
        Function for moving bullet
        :return: None
        """
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
    def __init__(self, pos_x, pos_y, main, winner=False):
        """
        initialization of class Artifact
        :param pos_x: Artifact's position x
        :param pos_y: Artifact's position y
        :param main: parameter for accessing the main class
        """
        super().__init__(main.artifact_group)
        self.main = main
        if not winner:
            self.art_name = choice(list(self.main.art_parameters.keys())[:-1])
        else:
            self.art_name = 'prize'
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.parameters = self.main.art_parameters[self.art_name][1]
        self.image = self.main.art_parameters[self.art_name][0]
        self.rect = self.image.get_rect().move(self.main.tile_width * pos_x + 10,
                                               self.main.tile_height * pos_y + 10)

    def check_collision(self):
        """
        Check collision between artifact and other subjects
        :return: None
        """
        if pygame.sprite.spritecollide(self, self.main.player_group, False):
            player_parameters = self.main.player.player_parameters
            self.main.music.artifact_get()
            for i in (0, 4, 3):
                if player_parameters[i] + int(self.parameters[i] * player_parameters[i]) > 1:
                    player_parameters[i] += int(self.parameters[i] * player_parameters[i])
                else:
                    player_parameters[i] = 1
            player_parameters[2] += (
                    self.parameters[2] * player_parameters[2] * player_parameters[1])
            if self.parameters[1] > player_parameters[1]:
                player_parameters[1] = self.parameters[1]
            player_parameters[5] += self.parameters[5]
            self.main.player_parameters = player_parameters
            self.kill()
            self.main.room.artifacts -= 1
            if self.main.room.artifacts == 0:
                self.main.game_map.update_doors()
            if self.parameters[-1] == True:
                self.main.congratulations()
        if pygame.sprite.spritecollide(self, self.main.bullet_group, False):
            print('Ouch!')


FPS = 50
pygame.init()

app = Main()

pygame.quit()
