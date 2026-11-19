"""自機"""

import pygame

from .settings import (
    PLAYER_BOTTOM_MARGIN,
    PLAYER_COLOR,
    PLAYER_HEIGHT,
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
