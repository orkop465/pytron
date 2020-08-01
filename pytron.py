# -*- coding: utf-8 -*-
"""

TODO:
    Reincorcement Learning

"""
import pygame
import itertools
from numpy import *


class Game(object):

    def __init__(self, width=800, height=800, fps=30):
        pygame.init()
        pygame.display.set_caption("PyTron")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((0, 0, 0))
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.players = []
        self.living_players = []
        self.one_player = False
        self.reset = False

        self.spawn_offset = 5
        self.spawn_positions = {
            1: (int(self.width / 2), self.height - (self.spawn_offset + 5), 'U'),
            2: (int(self.width / 2), self.spawn_offset, 'D'),
            3: (self.spawn_offset + 6, int(self.height / 2), 'R'),
            4: (self.width - (self.spawn_offset + 10), int(self.height / 2), 'L')
        }

        self.colors = itertools.cycle(['green', 'blue', 'purple', 'pink', 'red', 'orange'])
        self.base_color = next(self.colors)
        self.next_color = next(self.colors)
        self.current_color = self.base_color
        self.change_every_x_seconds = 3
        self.number_of_steps = self.change_every_x_seconds * self.fps
        self.step = 1

        self.left_wall = pygame.Rect((0, 0, 5, self.height))
        self.bottom_wall = pygame.Rect((0, self.height - 5, self.width, 5))
        self.right_wall = pygame.Rect((self.width - 5, 0, 5, self.height))
        self.top_wall = pygame.Rect((0, 0, self.width, 5))

        self.map = zeros(shape=(int(self.height / 5), int(self.width / 5)))
        self.map[0] = full((1, int(self.width / 5)), -1)
        self.map[-1] = full((1, int(self.width / 5)), -1)
        self.map[:, 0] = full((1, int(self.height / 5)), -1)
        self.map[:, -1] = full((1, int(self.height / 5)), -1)
        self.clean_map = self.map.copy()

    def paint_and_check_collision(self):

        self.background.fill((0, 0, 0))

        # PLAYERS
        for player in self.living_players:
            player.rect = pygame.Rect(player.x, player.y, player.size, player.size)
            # CHECK FOR COLLISION WITH WALLS
            if self.map[int(player.y / 5), int(player.x / 5)] != 0.0:
                player.dead = True
                player.direction = ''

            player.trail.append(player.rect)
            player.map_positions.append((int(player.y / 5), int(player.x / 5)))

            if not player.dead:
                pygame.draw.rect(self.background, player.color,
                                 (player.x, player.y, player.size, player.size))  # rect: (x1, y1, width, height)

            # DRAW TRAILS
            for t in player.trail:
                pygame.draw.rect(self.background, player.color, t)

            self.map[int(player.y / 5), int(player.x / 5)] = player.player_num

        for player in self.living_players:
            if player.dead:
                self.living_players.remove(player)

        if len(self.living_players) == 1:
            self.living_players[0].points += 1
            self.reset_game()
        elif len(self.living_players) == 0:
            self.reset_game()

        # WALLS
        self.color_shifter()
        # left
        pygame.draw.rect(self.background, self.current_color, self.left_wall)
        # bottom
        pygame.draw.rect(self.background, self.current_color, self.bottom_wall)
        # right
        pygame.draw.rect(self.background, self.current_color, self.right_wall)
        # top
        pygame.draw.rect(self.background, self.current_color, self.top_wall)

        pygame.display.flip()
        self.screen.blit(self.background, (0, 0))

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

    def add_player(self, player):
        try:
            self.players.append(player)
            player.player_num = len(self.players)
            player.x, player.y, player.direction = self.spawn_positions[len(self.players)]
            self.map[int(player.y / 5), int(player.x / 5)] = player.player_num
        except IndexError:
            raise Exception("Too many players, only four are allowed")

    def reset_game(self):
        self.reset = False
        self.living_players = self.players.copy()
        i = 1
        for player in self.players:
            player.trail.clear()
            player.dead = False
            player.x, player.y, player.direction = self.spawn_positions[i]
            i += 1
        self.map = self.clean_map.copy()
        self.paint_and_check_collision()

    def run(self):
        """
        The mainloop
        """
        self.living_players = self.players.copy()
        self.paint_and_check_collision()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            keys = pygame.key.get_pressed()

            if self.one_player and not self.players[0].dead:
                if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.players[0].direction != 'R':
                    self.players[0].direction = 'L'
                elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.players[0].direction != 'L':
                    self.players[0].direction = 'R'
                elif (keys[pygame.K_UP] or keys[pygame.K_w]) and self.players[0].direction != 'D':
                    self.players[0].direction = 'U'
                elif (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.players[0].direction != 'U':
                    self.players[0].direction = 'D'

            elif not self.one_player:
                if not self.players[0].dead:
                    if keys[pygame.K_LEFT] and self.players[0].direction != 'R':
                        self.players[0].direction = 'L'
                    elif keys[pygame.K_RIGHT] and self.players[0].direction != 'L':
                        self.players[0].direction = 'R'
                    elif keys[pygame.K_UP] and self.players[0].direction != 'D':
                        self.players[0].direction = 'U'
                    elif keys[pygame.K_DOWN] and self.players[0].direction != 'U':
                        self.players[0].direction = 'D'

                if not self.players[1].dead:
                    if keys[pygame.K_a] and self.players[1].direction != 'R':
                        self.players[1].direction = 'L'
                    elif keys[pygame.K_d] and self.players[1].direction != 'L':
                        self.players[1].direction = 'R'
                    elif keys[pygame.K_w] and self.players[1].direction != 'D':
                        self.players[1].direction = 'U'
                    elif keys[pygame.K_s] and self.players[1].direction != 'U':
                        self.players[1].direction = 'D'

            for player in self.living_players:
                player.move()

            self.paint_and_check_collision()

            milliseconds = self.clock.tick(self.fps)
            self.playtime += milliseconds / 1000.0

        pygame.quit()


class Player:

    def __init__(self, game, color, vel):
        self.player_num = 0
        self.vel = vel
        self.x = 0
        self.y = 0
        self.size = 5
        self.color = color
        self.direction = ''
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.dead = False
        self.trail = []
        self.map_positions = []
        self.points = 0
        game.add_player(self)

    def move(self):
        if self.direction == 'L':
            self.x -= self.vel * 5
        elif self.direction == 'R':
            self.x += self.vel * 5
        elif self.direction == 'U':
            self.y -= self.vel * 5
        elif self.direction == 'D':
            self.y += self.vel * 5


if __name__ == '__main__':
    # call with width of window and fps
    Game = Game()
    p1 = Player(Game, (255, 0, 0), 1)
    p2 = Player(Game, (0, 255, 255), 1)
    # p3 = Player("3", Game, (255, 0, 255), 1)
    # p4 = Player("4", Game, (0, 0, 255), 5)
    Game.run()
