"""ゲームループと全体の管理（監督）"""

import pygame

from .bullet import Bullet
from .enemy import Enemy
from .player import Player
from .settings import (
    BG_COLOR,
    ENEMY_SPAWN_INTERVAL,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TITLE,
)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.all_sprites = pygame.sprite.Group()
        self.player = Player(self.screen.get_rect())
        self.all_sprites.add(self.player)
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.spawn_timer = 0

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.shoot()

    def shoot(self):
        bullet = Bullet(self.player.rect.midtop)
        self.all_sprites.add(bullet)
        self.bullets.add(bullet)

    def spawn_enemy(self):
        enemy = Enemy(self.screen.get_rect())
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)

    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= ENEMY_SPAWN_INTERVAL:
            self.spawn_enemy()
            self.spawn_timer -= ENEMY_SPAWN_INTERVAL
        self.all_sprites.update(dt)

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.all_sprites.draw(self.screen)
        pygame.display.flip()
