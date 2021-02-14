#!/usr/bin/python
"""
Github repo can be found here:
https://github.com/sparshg/pycollab
"""
from os import environ
import math

# Hide pygame Hello prompt
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
from pygame.math import Vector2

# Declare some constants and variables
WIDTH, HEIGHT = (600, 400)
FPS = 60
WHITE = "#F1F1F1"
BLACK = "#101010"
ORANGE = "#FF6600"
RED = "#FF1F00"


class Frame:
    def __init__(self, gap=110):
        self.length = 3 * gap
        self.gap = gap
        self.moves = []
        self.turn = 1
        # fmt: off
        self.points = self.cartesian([
            [self.gap/2, self.length/2], [self.gap/2, -self.length/2],
            [-self.gap/2, -self.length/2], [-self.gap/2, self.length/2],
            [-self.length/2, self.gap/2], [self.length/2, self.gap/2],
            [self.length/2, -self.gap/2], [-self.length/2, -self.gap/2],
        ])
        # fmt: on
        self.rects = []
        for i in range(3):
            for j in range(3):
                self.rects.append(
                    pygame.Rect((-1.5 + 1 * j) * gap, (1.5 - 1 * i) * gap, gap, gap)
                )
        self.rects = self.cartesian(self.rects)

        self.animations = [
            Animate(700 + i * 100).line(self.points[i], self.points[i + 1])
            for i in range(0, len(self.points), 2)
        ]

    # Convert given list cartesian coordinates to pygame coordinates
    @staticmethod
    def cartesian(coords, new_origin=(WIDTH / 2, HEIGHT / 2)):
        for coord in coords:
            coord[0] = coord[0] + new_origin[0]
            coord[1] = -coord[1] + new_origin[1]
        return coords

    def detect_click(self, pos):
        for rect in self.rects:
            if rect.collidepoint(pos):
                self.moves.append(OX(self.turn, rect.center))
                self.turn = 1 - self.turn
                self.rects.remove(rect)
                break

    def draw(self):
        for animation in self.animations:
            animation.play()
        for move in self.moves:
            move.draw()


class OX:
    def __init__(self, _type, center):
        self.type = _type
        self.center = center
        if _type == 1:
            self.animation = Animate(color=ORANGE).cross(center)
        elif _type == 0:
            self.animation = Animate(color=RED).circle(center)

    def draw(self):
        self.animation.play()


class Animate:

    LINEAR = lambda x: x
    EASE_OUT_SINE = lambda x: math.sin(math.pi / 2 * x)
    EASE_IO_SINE = lambda x: 0.5 - math.cos(math.pi * x) / 2
    EASE_OUT_QUART = lambda x: 1 - pow(1 - x, 4)

    def EASE_IO_QUART(x):
        return 8 * pow(x, 4) if x < 0.5 else 1 - pow(-2 * x + 2, 4) / 2

    def __init__(self, dur=500, color=WHITE, fn=EASE_OUT_QUART):
        self.color = color
        self.function = fn
        self.dur = dur
        self.start_time = pygame.time.get_ticks()
        self.final_time = self.start_time + dur
        self.type = None

    def line(self, p1, p2, width=8):
        self.type = "line"
        self.finished = False
        self.width = width
        self.p1 = Vector2(p1)
        self.p2 = Vector2(p2)
        self.p = self.p2 - self.p1
        self.length = self.p.magnitude()
        return self

    def circle(self, center=[WIDTH / 2, HEIGHT / 2], radius=38, width=8):
        self.type = "circle"
        self.finished = False
        self.width = width
        self.radius = radius
        self.center = Vector2(center)
        self.rect = pygame.Rect(
            (center - Vector2(radius, radius)), (2 * radius, 2 * radius)
        )
        return self

    def cross(self, center=[WIDTH / 2, HEIGHT / 2], length=40, width=10):
        self.type = "cross"
        # fmt: off
        points = [
            Vector2(-length, 0), Vector2(length, 0),
            Vector2(0, length), Vector2(0, -length)
        ]
        # fmt: on
        for point in points:
            point.update(point.rotate(45) + Vector2(center))

        self.sub_animations = [
            Animate(self.dur + i * 100, self.color, self.function).line(
                points[i], points[i + 1], width
            )
            for i in range(0, len(points), 2)
        ]
        return self

    def play(self, skip=False):

        if self.type == "cross":
            for animation in self.sub_animations:
                animation.play()
            return

        if not self.finished:
            if pygame.time.get_ticks() < self.final_time and not skip:
                fraction = (
                    pygame.time.get_ticks() - self.start_time
                ) / self.dur + 0.001
                if self.type == "line":
                    self.p.scale_to_length(self.length * self.function(fraction))
                elif self.type == "circle":
                    self.r = self.radius - self.width * self.function(fraction)
            else:
                if self.type == "line":
                    self.p = self.p2 - self.p1
                if self.type == "circle":
                    self.r = self.radius - self.width
                self.finished = True
        if self.type == "line":
            pygame.draw.line(
                Main.win, self.color, self.p1, self.p + self.p1, self.width
            )
        elif self.type == "circle":
            pygame.draw.circle(Main.win, self.color, self.center, self.radius)
            pygame.draw.circle(Main.win, BLACK, self.center, self.r)


# The main controller
class Main:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tic-Tac-Toe")

        Main.win = pygame.display.set_mode((WIDTH, HEIGHT))
        Main.running = True

        self.frame = Frame()
        Main.clock = pygame.time.Clock()
        # dt is the time since last frame, which is ideally 1/FPS
        Main.dt = Main.clock.tick(FPS)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Main.running = False
            if event.type == pygame.MOUSEBUTTONUP:
                self.frame.detect_click(pygame.mouse.get_pos())

    def draw(self):
        Main.win.fill(BLACK)
        self.frame.draw()
        pygame.display.update()

    # The main loop
    def loop(self):
        while self.running:
            self.check_events()
            self.draw()
            # Calculate dt for next frame
            Main.dt = Main.clock.tick(FPS)
        pygame.quit()


# Test if the script is directly ran
if __name__ == "__main__":
    Main().loop()
