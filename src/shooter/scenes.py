"""場面（シーン）"""

import pygame

from .bullet import Bullet
from .enemy import Enemy
from .player import Player
from .settings import (
    BG_COLOR,
    ENEMY_SCORE,
    ENEMY_SPAWN_INTERVAL,
    SCORE_COLOR,
    SCORE_FONT_SIZE,
    SCORE_POS,
)


class Scene:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass


class PlayScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.all_sprites = pygame.sprite.Group()
        self.player = Player(self.game.screen.get_rect())
        self.all_sprites.add(self.player)
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.spawn_timer = 0
        self.score = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.shoot()

    def shoot(self):
        bullet = Bullet(self.player.rect.midtop)
        self.all_sprites.add(bullet)
        self.bullets.add(bullet)

    def spawn_enemy(self):
        enemy = Enemy(self.game.screen.get_rect())
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)

    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= ENEMY_SPAWN_INTERVAL:
            self.spawn_enemy()
            self.spawn_timer -= ENEMY_SPAWN_INTERVAL
        self.all_sprites.update(dt)
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        self.score += len(hits) * ENEMY_SCORE

    def draw(self, screen):
        screen.fill(BG_COLOR)
        self.all_sprites.draw(screen)
        score_image = self.font.render(f"SCORE: {self.score}", True, SCORE_COLOR)
        screen.blit(score_image, SCORE_POS)
