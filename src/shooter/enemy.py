"""敵"""

import random

import pygame

from .settings import (
    ENEMY_COLOR,
    ENEMY_HEIGHT,
    ENEMY_SPEED,
    ENEMY_WIDTH,
)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, bounds):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(ENEMY_COLOR)
        x = random.randint(0, bounds.width - ENEMY_WIDTH)
        self.rect = self.image.get_rect(left=x, bottom=bounds.top)
        self.pos = pygame.Vector2(self.rect.center)
        self.bounds = bounds

    def update(self, dt):
        self.pos.y += ENEMY_SPEED * dt
        self.rect.center = self.pos
        if self.rect.top > self.bounds.bottom:
            self.kill()
