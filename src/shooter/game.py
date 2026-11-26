"""ゲームループと全体の管理（監督）"""

import pygame

from .scenes import PlayScene
from .settings import (
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
        self.scene = PlayScene(self)

    def change_scene(self, scene):
        self.scene = scene

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                self.running = False
            else:
                self.scene.handle_event(event)
