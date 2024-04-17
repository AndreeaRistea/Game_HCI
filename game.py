import pygame
import pickle
from os import path

from pygame import JOYBUTTONDOWN, JOYAXISMOTION, JOYHATMOTION


from button import Button
from coin import Coin
from world import World

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 900
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Game')

# define font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)
font_lvl = pygame.font.SysFont('Bauhaus 93', 40)

# define game variables
tile_size = 50
game_over = 0
main_menu = True
level = 1
max_levels = 2
score = 0
score_lvl = 0
frame_count = 0
time_expired = True

# define colours
white = (255, 255, 255)
blue = (0, 0, 255)

# load images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png')

world_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 7, 7, 0, 0, 0, 0, 7, 7, 0, 0, 0, 0, 8, 1],
    [1, 0, 0, 0, 2, 2, 0, 0, 0, 0, 2, 2, 0, 0, 0, 2, 2, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 1],
    [1, 0, 5, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 7, 0, 1],
    [1, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 1],
    [1, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 7, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 3, 0, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 6, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# function to reset level
def reset_level(level):
    global world_data
    player.reset(100, screen_height - 130)
    blob_group.empty()
    platform_group.empty()
    coin_group.empty()
    lava_group.empty()
    exit_group.empty()

    # load in level data and create world
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data, tile_size, blob_group, platform_group, lava_group, coin_group, exit_group, screen)
    # create dummy coin for showing the score
    score_coin = Coin(tile_size // 2, tile_size // 2, tile_size)
    coin_group.add(score_coin)
    return world


class Player():
    joystick = None
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20

        if game_over == 0:
            if self.joystick:
                axis_x = self.joystick.get_axis(0)
                if abs(axis_x) > 0.1:
                    dx += (5 * axis_x)
                    self.counter += 1
                    if axis_x > 0:
                        self.direction = 1
                    if axis_x < 0:
                        self.direction = -1
                else:
                    self.stop()

                for event in pygame.event.get():
                    if event.type == JOYBUTTONDOWN and self.joystick.get_button(0) \
                         and self.jumped == False and self.in_air == False:
                        self.vel_y = -15
                        self.jumped = True

                    if event.type == JOYBUTTONDOWN and self.joystick.get_button(0):
                        self.jumped = False


            else:
                if pygame.joystick.get_count() > 0:
                    self.joystick = pygame.joystick.Joystick(0)
                    self.joystick.init()

            # get keypresses
            key = pygame.key.get_pressed()
            if key[pygame.K_UP] and self.jumped == False and self.in_air == False:
                # jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_UP] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1

            # handle animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # check for collision
            self.in_air = True
            for tile in world.tile_list:
                # check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if below the ground i.e. jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # check if above the ground i.e. falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # check for collision with enemies
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                # game_over_fx.play()

            # check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                # game_over_fx.play()

            # check for collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # check for collision with platforms
            for platform in platform_group:
                # collision in the x direction
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # collision in the y direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if below platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # check if above platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    # move sideways with the platform
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            # update player coordinates
            self.rect.x += dx
            self.rect.y += dy


        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2)
            if self.rect.y > 200:
                self.rect.y -= 5

        # draw player onto screen
        screen.blit(self.image, self.rect)

        return game_over

    def stop(self):
        self.counter = 0
        self.index = 0
        if self.direction == 1:
            self.image = self.images_right[self.index]
        if self.direction == -1:
            self.image = self.images_left[self.index]

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(0, 4):
            img_right = pygame.image.load(f'img/mario_move{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


player = Player(100, screen_height - 130)

blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

player = Player(100, screen_height - 130)


# create dummy coin for showing the score
score_coin = Coin(tile_size // 2, tile_size // 2, tile_size)
coin_group.add(score_coin)

# load in level data and create world
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data, tile_size, blob_group, platform_group, lava_group, coin_group, exit_group, screen)

#  create buttons
start_button_normal = pygame.image.load("img/start_btn_normal.png")
start_button_selected = pygame.image.load("img/start_btn_selected.png")
exit_button_normal = pygame.image.load("img/exit_btn_normal.png")
exit_button_selected = pygame.image.load("img/exit_btn_selected.png")
restart_button_normal = pygame.image.load("img/restart_btn_normal.png")
restart_button_selected = pygame.image.load("img/restart_btn_selected.png")

restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_button_normal,
                        restart_button_selected, screen_width, screen_height)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_button_normal, start_button_selected,
                      screen_width, screen_height)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_button_normal, exit_button_selected,
                     screen_width, screen_height)
buttons = [start_button, exit_button]
selected_button_index = 0

run = True
game_in_progress = True

def isRight(event):
    if event.dict['value'] == (1, 0):
        return True
    return False

def isLeft(event):
    if event.dict['value'] == (-1, 0):
        return True
    return False

def restart():
    global frame_count
    restart_button.draw()
    restart_button.select()  # Selectăm butonul de restart
    frame_count = 0


pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    print(joystick.get_name())

while run:
    clock.tick(fps)

    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (100, 100))

    if main_menu:
        for event in pygame.event.get():
            if event.type == JOYAXISMOTION:
                print(event)
            if event.type == JOYHATMOTION:
                if isRight(event):
                    selected_button_index = (selected_button_index - 1) % len(buttons)

                if isLeft(event):
                    selected_button_index = (selected_button_index + 1) % len(buttons)
                print(event)
            if event.type == JOYBUTTONDOWN:
                if event.button == 0:
                    print(event)
                    if buttons[selected_button_index].draw():
                            if selected_button_index == 0:  # Dacă butonul de start este selectat
                                main_menu = False
                            elif selected_button_index == 1:  # Dacă butonul de exit este selectat
                                run = False

        # Selectează butonul corespunzător
        for i, button in enumerate(buttons):
            if i == selected_button_index:
                button.selected = True
            else:
                button.selected = False

        # Desenează butoanele
        for button in buttons:
            button.draw()

    else:
        if game_over != 1:
            frame_count += 1
        world.draw()

        if game_over == 0:
            draw_text('             Level: ' + str(level), font_lvl, white, 10, 10)
            blob_group.update()
            platform_group.update()
            # update score
            # check if a coin has been collected
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                # coin_fx.play()
            draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        # if player has died

        # if player has completed the level
        if game_over == 1:  #or frame_count // fps >= 10:
            game_in_progress = False
            # reset game and go to next level
            level += 1
            score_lvl = score
            # frame_count += 1
            if level <= max_levels:
                # reset level
                world_data = [
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 1],
                    [1, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 8, 1],
                    [1, 0, 0, 2, 0, 0, 0, 0, 0, 7, 3, 0, 0, 0, 0, 2, 2, 1],
                    [1, 0, 0, 0, 0, 7, 7, 7, 0, 2, 2, 2, 0, 5, 0, 0, 0, 1],
                    [1, 7, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 5, 0, 7, 7, 7, 0, 2, 0, 0, 0, 7, 0, 7, 0, 0, 0, 1],
                    [1, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 2, 2, 2, 0, 7, 0, 0, 0, 0, 4, 0, 0, 0, 0, 1],
                    [1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 7, 3, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 6, 6, 1, 1, 1, 1, 1, 1, 1]
                ]
                world = reset_level(level)
                game_over = 0
                score = score
                frame_count = 0
                game_in_progress = True
            elif game_over == 1:
                game_in_progress = False
                draw_text('YOU WIN!', font, blue, (screen_width // 2) - 140, screen_height // 2)
                final_score_text = 'Final Score: ' + str(score)
                text_width, text_height = font.size(final_score_text)
                text_x = (screen_width - text_width) // 2
                text_y = (screen_height + 2.5 * text_height) // 2
                draw_text(final_score_text, font, blue, text_x, text_y)

    if frame_count // fps >= 90:
        game_over = -1
        game_in_progress = False

    if game_over == -1:
        restart()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == JOYBUTTONDOWN:
            if event.button == 0:
                print(event)
                if game_over < 0:  # Verificăm dacă jocul este terminat
                    if restart_button.selected and level == 1:  # Verificăm dacă butonul de restart este selectat
                        world.draw()
                        world = reset_level(level)
                        game_over = 0
                        score = 0
                        game_in_progress = True
                    else:
                        world.draw()
                        world = reset_level(level)
                        game_over = 0
                        score = score_lvl

    if game_in_progress:
        time_remaining = max(0, 90 - (frame_count // fps))
        minutes = time_remaining // 60
        seconds = time_remaining % 60
        draw_text(f'Time: {minutes:02}:{seconds:02}', font_score, white, screen_width - 140, 10)
    pygame.display.update()

pygame.quit()
