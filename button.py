import pygame


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
        action = False

        # Verifică apăsările de taste
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN] and self.selected:
            action = True

        # Desenează butonul
        if self.selected:
            self.screen.blit(self.image_selected, self.rect)
        else:
            self.screen.blit(self.image_normal, self.rect)

        return action

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False
