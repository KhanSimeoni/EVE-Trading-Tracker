import pygame

# Constants
STAR_CONVERSION_FACTOR = 1000000000000000
STAR_RADIUS = 5


class Star:
    def __init__(self, pos: tuple):
        # TODO: Star position currently does not account for differant types of axis, negative valus appear off screen
        self.pos = (pos[0] / STAR_CONVERSION_FACTOR, pos[1] / STAR_CONVERSION_FACTOR)
        self.radius = STAR_RADIUS


class StarMap:
    def __init__(self, pos: list):
        self.pos = pos

        self.stars = []
        for star_pos in pos:
            self.stars.append(Star(star_pos))

    def getStars(self):
        return self.stars
