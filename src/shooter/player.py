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
        self.pos = pygame.Vector2(self.rect.center)
        self.bounds = bounds

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_RIGHT]:
            direction.x += 1
        if keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_DOWN]:
            direction.y += 1
        if direction.length() > 0:
            direction = direction.normalize()
        self.pos += direction * PLAYER_SPEED * dt
        self.rect.center = self.pos
        before = self.rect.center
        self.rect.clamp_ip(self.bounds)
        if self.rect.center != before:
            self.pos = pygame.Vector2(self.rect.center)
