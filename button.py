import pygame
from pygame import JOYBUTTONUP, JOYBUTTONDOWN
from pygame.joystick import Joystick


class Button:
    def __init__(self, x, y, image_normal, image_selected, screen_width, screen_height):
        self.screen_width = 900
        self.screen_height = 600
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.image_normal = image_normal
        self.image_selected = image_selected
        self.rect = self.image_normal.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.selected = False

    def draw(self):

        # Desenează butonul
        if self.selected:
            self.screen.blit(self.image_selected, self.rect)
        else:
            self.screen.blit(self.image_normal, self.rect)

        return self.selected

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False
