"""弾"""

import pygame

from .settings import BULLET_COLOR, BULLET_HEIGHT, BULLET_SPEED, BULLET_WIDTH


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(BULLET_COLOR)
        self.rect = self.image.get_rect(midbottom=pos)
        self.pos = pygame.Vector2(self.rect.center)

    def update(self, dt):
        self.pos.y -= BULLET_SPEED * dt
        self.rect.center = self.pos
        if self.rect.bottom < 0:
            self.kill()
