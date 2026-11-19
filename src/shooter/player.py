"""自機"""

import pygame

from .settings import (
    PLAYER_BOTTOM_MARGIN,
    PLAYER_COLOR,
    PLAYER_HEIGHT,
    PLAYER_SPEED,
    PLAYER_WIDTH,
)


class Player(pygame.sprite.Sprite):
    def __init__(self, bounds):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(
            midbottom=(bounds.centerx, bounds.bottom - PLAYER_BOTTOM_MARGIN)
        )
        self.bounds = bounds

    def update(self, dt):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1
        self.rect.x += dx * PLAYER_SPEED * dt
        self.rect.y += dy * PLAYER_SPEED * dt
        self.rect.clamp_ip(self.bounds)
