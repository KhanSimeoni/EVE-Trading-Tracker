# A GUI tool for tracking and calculating good EVE Online shipment routes
# Written in pygame, and for use with pypy3

import string
import sys
import pygame
from pygame.locals import *
from operator import sub, add

# Initialize pygame; REQUIRED BEFORE ANY PYGAME CODE
pygame.init()

# Constants
WINDOW_SIZE = (800, 600)
FPS = 60

# Basic functions such as updating rendering
class BasicFunctions:
    def __init__(self):
        pass

    def updateObjects(self, window, objects: list, colors: list):

        # Draw every object in the objcts list
        for object in objects:
            object_id = objects.index(object)
            pygame.draw.rect(window, colors[object_id], object)

    def posMath(operation: int, pos1: tuple, pos2: tuple):
        """
        Does math to coordinates in tuple form, operator defined with an int
        1: add
        2: subtract
        """

        # Addition math
        if operation == 1:
            return tuple(map(add, pos1, pos2))

        # Subtraction math
        elif operation == 2:
            return tuple(map(sub, pos1, pos2))

    def flattenList(list):
        return [item for sublist in list for item in sublist]


# Colors
class Colors:
    def __init__(self):
        self.dark_background = pygame.Color(17, 7, 41)
        self.light_background = pygame.Color(17, 0, 89)
        self.dark_menu = pygame.Color(17, 0, 73)
        self.light_menu = pygame.Color(17, 0, 95)


# Menus
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


def run():

    # Get basic program functions
    functions = BasicFunctions()

    # Get colors
    colors = Colors()

    # Createa blank display (like a canvas)
    display = pygame.display.set_mode(WINDOW_SIZE)

    # Create a game clock
    clock = pygame.time.Clock()

    # test menu
    test_menu = Menu(display, colors, (0, 0), (200, 450), "Test Window")
    test_menu2 = Menu(display, colors, (300, 0), (200, 450), "Test Window 2")

    # Variables for looping
    moving_menu_pos = None
    moving_menu = None
    moving_menu_init = None
    moving_menu_mouse_init = None
    collided = False

    # Start the main event loop
    running = True
    while running:

        # Clear the screen at the start of the frame
        display.fill(colors.dark_background)

        # Math for moving the active menu
        if moving_menu_pos != None:
            moving_menu_pos = moving_menu.getPos()
            moving_menu.move(
                BasicFunctions.posMath(
                    2,
                    BasicFunctions.posMath(
                        2,
                        pygame.mouse.get_pos(),
                        moving_menu_mouse_init,
                    ),
                    BasicFunctions.posMath(
                        2,
                        moving_menu_pos,
                        moving_menu_init,
                    ),
                )
            )

        # Update things in the frame
        functions.updateObjects(
            display,
            BasicFunctions.flattenList(
                [test_menu.getObjects(), test_menu2.getObjects()],
            ),
            BasicFunctions.flattenList(
                [test_menu.getColors(), test_menu2.getColors()],
            ),
        )

        # Update the screen and the objects on the screen
        pygame.display.update()

        # If the game is quite, exit pygame
        for event in pygame.event.get():

            # If the mouse button is pressed
            if event.type == pygame.MOUSEBUTTONDOWN:

                # If clicking on a menu get menu information for later use
                if test_menu.header.collidepoint(pygame.mouse.get_pos()):
                    moving_menu_mouse_init = pygame.mouse.get_pos()
                    moving_menu = test_menu
                    collided = True

                elif test_menu2.header.collidepoint(pygame.mouse.get_pos()):
                    moving_menu_mouse_init = pygame.mouse.get_pos()
                    moving_menu = test_menu2
                    collided = True

                # If collision detected with menu (above statement) get the menu position for later use
                if collided:
                    moving_menu_init = moving_menu.getPos()
                    moving_menu_pos = moving_menu.getPos()

            # If no longer holding a menu, forget information about the menu
            if event.type == pygame.MOUSEBUTTONUP:
                moving_menu_pos = None
                moving_menu = None
                moving_menu_init = None
                collided = False

            # If the gam is quit, quit the game :)
            if event.type == QUIT:
                pygame.quit()

                # Return of 0 means program exited correctly
                return 0

        # Run the game (and the clock) at the desired FPS
        clock.tick(FPS)


# Run the main event loop function
if __name__ == "__main__":
    sys.exit(run())
