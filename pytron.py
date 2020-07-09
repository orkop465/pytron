# -*- coding: utf-8 -*-
"""

TODO:
    FIRST: SPLIT INTO GAME AND PLAYER CLASSES   DONE :)
    Change controls to snake-style              DONE :)
    Add dying (from walls / trail)              next
    Tron style trail

TODO late-game:
    Add sprites
    Multiple players / AI

"""
import itertools

import pygame


class Game(object):

    def __init__(self, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
           default arguments
        """
        pygame.init()
        pygame.display.set_caption("Press ESC to quit")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((0, 0, 0))  # fill background white
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.players = [Player("red", int((self.width / 2) - 25), self.height - 25, 5)]

        self.colors = itertools.cycle(['green', 'blue', 'purple', 'pink', 'red', 'orange'])
        self.base_color = next(self.colors)
        self.next_color = next(self.colors)
        self.current_color = self.base_color
        self.change_every_x_seconds = 3.
        self.number_of_steps = self.change_every_x_seconds * self.fps
        self.step = 1

    def paint(self):
        """painting on the surface"""
        # PLAYERS
        for player in self.players:
            pygame.draw.rect(self.background, (255, 0, 0),
                             (player.x, player.y, 20, 20))  # rect: (x1, y1, width, height)
        # WALLS
        self.color_shifter()
        # left
        pygame.draw.rect(self.background, self.current_color, (0, 0, 5, self.height))
        # bottom
        pygame.draw.rect(self.background, self.current_color,
                         (0, self.height - 5, self.width, 5))
        # right
        pygame.draw.rect(self.background, self.current_color,
                         (self.width - 5, 0, 5, self.height))
        # top
        pygame.draw.rect(self.background, self.current_color, (0, 0, self.width, 5))

    def color_shifter(self):
        self.step += 1
        if self.step < self.number_of_steps:
            # (y-x)/number_of_steps calculates the amount of change per step required to
            # fade one channel of the old color to the new color
            # We multiply it with the current step counter
            self.current_color = [x + (((y - x) / self.number_of_steps) * self.step) for x, y in
                                  zip(pygame.color.Color(self.base_color), pygame.color.Color(self.next_color))]
        else:
            self.step = 1
            self.base_color = self.next_color
            self.next_color = next(self.colors)

    def run(self):
        """The mainloop
        """
        self.paint()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            keys = pygame.key.get_pressed()

            # Making sure the top left position of our character is greater than our vel so we never move off the screen
            if keys[pygame.K_LEFT] and self.players[0].direction != 'R':
                self.players[0].direction = 'L'

            # Making sure the top right corner of our character is less than the screen width - its width
            if keys[pygame.K_RIGHT] and self.players[0].direction != 'L':
                self.players[0].direction = 'R'

            # Same principles apply for the y coordinate
            if keys[pygame.K_UP] and self.players[0].direction != 'D':
                self.players[0].direction = 'U'

            if keys[pygame.K_DOWN] and self.players[0].direction != 'U':
                self.players[0].direction = 'D'

            self.players[0].move()

            self.background.fill((0, 0, 0))
            self.paint()

            milliseconds = self.clock.tick(self.fps)
            self.playtime += milliseconds / 1000.0

            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))

        pygame.quit()


class Player:

    def __init__(self, color, starting_x, starting_y, vel):
        self.vel = vel
        self.x = starting_x
        self.y = starting_y
        self.color = color
        self.direction = ''

    def move(self):
        if self.direction == 'L':
            self.x -= self.vel
        elif self.direction == 'R':
            self.x += self.vel
        elif self.direction == 'U':
            self.y -= self.vel
        elif self.direction == 'D':
            self.y += self.vel


if __name__ == '__main__':
    # call with width of window and fps
    Game().run()
