import string
import pygame


# Menu objects
class Menu:
    def __init__(self, window, colors, pos: tuple, size: tuple, title: string):

        # Colors for the manu objects
        self.headerColor = colors.light_menu
        self.bodyColor = colors.dark_menu

        # Create a rectangle for the body
        self.body = pygame.rect.Rect(
            pos[0],
            pos[1] + (size[1] / 11),
            size[0],
            size[1] - (size[1] / 11),
        )

        # Create a rectangle for the header
        self.header = pygame.rect.Rect(
            pos[0],
            pos[1],
            size[0],
            size[1] / 11,
        )

    # Move the menu (moves by delta, not to position)
    def move(self, pos: tuple):
        pygame.Rect.move_ip(self.header, pos)
        pygame.Rect.move_ip(self.body, pos)

    def getPos(self, body: bool = False):
        """
        Returns the position of the menu
        If body is true, returns the position of the body instead
        """

        # Return the top left pos of the header
        if not body:
            return self.header.topleft

        # Return the top left pos of the body
        elif body:
            return self.body.topleft

    # Return the objects making up the menu
    def getObjects(self):
        return [self.body, self.header]

    # Return the colors used in the menu
    def getColors(self):
        return [self.bodyColor, self.headerColor]
