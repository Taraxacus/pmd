# Author: Maximilian Weinberg
# Date: 2017-04-01
# main02.py: Trying the pygame tiles tutorial from qq.readthedocs.io

import os
import configparser
import random
import easygui

import pygame

# WHAT IS:
# - a vicinity:
#    A list of three three character strings containing only the characters
#    "1", "0", "/". It is regarded as a 3x3 square of characters.
# - a vicinity code:
#    A string of three characters determining the type of vicinity of a given
#    tile. Useful for loading the right tile graphic.

FOLDERS = {"LEVELS":"levels",
           "MAPS":"tile_sets/maps",
           "AVATARS":"tile_sets/avatars",
          }
constants = configparser.ConfigParser()
constants.read("constants/constants.ini")
VICINITY_MASKS = {option:constants["masks"][option].split() for option in constants.options("masks")}
SCREEN_SIZE = tuple([constants["info"].getint("screen_size_" + i) for i in "xy"])
BORDER = tuple([constants["info"].getint("border_" + i) for i in "xy"])
del constants
DIRECTIONS = "wasd"
TILE_CODES = {"X0":("walls", "default"),
              "X1":("walls", "alternate1"),
              "X2":("walls", "alternate2"),
              ".0":("ground", "default"),
              ".1":("ground", "alternate1"),
              ".2":("ground", "alternate2"),
              ".3":("ground", "unused"),
              "o0":("water", "default")
             }
TILE_VARIATION_NUMBER = {"X":3,
                         ".":4,
                         "o":1
                        }
VARIATION_GGT = 12
SIMILAR = {"X":"X",
           ".":".o",
           "o":"o"}

def ask_for_file(directory,extension,question, name_only=False):
    """Asks user via console to choose from all files in directory 'directory'
    with extension 'extension' using the prompt 'question'."""
    # Prepar raw return string --- I should possibly do this using os.path
    if name_only:
        return_string = "{0}"
    else:
        return_string = directory + "/{0}" + extension

    # make ist of file names without extension
    n = len(extension)
    options = [name[:-n] for name in os.listdir(directory) if (name[-n:] == extension)]

    # Catch possibility of no valid options
    if options == []:
        return None
    # Catch possibility of only one valid option. This option will automatically be selected
    elif len(options) == 1:
        print(question+" Option {0} was automatically selected.".format(options[0]))
        return return_string.format(options[0])
    # Ask for option until a valid option is given
    options.sort()
    while True:
        #option = input(question+" ("+", ".join(options)+") ")
        option = easygui.choicebox(question, "User input", options)
        if option in options:
            break
        print("Not a valid choice!")

    print("Option {0} selected.".format(option))
    return return_string.format(option)

def load_tile_file(filename, position_directory, size, colorkey=None):
    """Loads tiles from 'filename' where 'position_directory' is a directory
    containing the positions of the tiles and 'size' is a tuple of the tiles'
    size. If a color 'colorkey' is given all pixels with this color will be
    loaded as transparent."""
    # Load file as PyGame image
    image = pygame.image.load(filename).convert()

    # Make certain pixels transparent
    if colorkey != None:
        image.set_colorkey(colorkey)

    # Load tiles into new dictionary
    tile_directory = {}
    size_x, size_y = size
    for key in position_directory:
        position_x,position_y = position_directory[key]
        tile_directory[key] = image.subsurface((position_x, position_y, size_x, size_y))

    return tile_directory

def load_tile_set(tile_set_name, legend):
    """Reads the INI of the tile set 'tile_set_name' to properly extract the
    tiles from the image files."""
    # Read size and colorkey
    offset_x = legend["info"].getint("offset_x")
    offset_y = legend["info"].getint("offset_y")
    size_x = legend["info"].getint("size_x")
    size_y = legend["info"].getint("size_y")
    colorkey_r = legend["info"].getint("colorkey_r")
    colorkey_g = legend["info"].getint("colorkey_g")
    colorkey_b = legend["info"].getint("colorkey_b")
    margin_x = legend["info"].getint("margin_x")
    margin_y = legend["info"].getint("margin_y")
    offset = (offset_x, offset_y)
    colorkey = (colorkey_r, colorkey_g, colorkey_b)

    # Make position directory
    position_directory = {}
    for code, tile_type in TILE_CODES.items():
        for mask in VICINITY_MASKS:
            for direction in DIRECTIONS:
                if tile_type[1] in legend[tile_type[0]]:
                    # offset, size, margin, column and line
                    dx_type = legend[tile_type[0]].getint(tile_type[1])
                    dx_vicinity = legend["tile_table"].getint(mask + direction + "x")
                    dy_vicinity = legend["tile_table"].getint(mask + direction + "y")
                    x = offset_x + (size_x + margin_x) * (3 * dx_type + dx_vicinity)
                    y = offset_y + (size_y + margin_y) * dy_vicinity
                    position_directory[code+mask+direction] = (x, y)
    filename = FOLDERS["MAPS"] + "/{0}.png".format(tile_set_name)
    tile_directory = load_tile_file(filename, position_directory, (size_x, size_y), colorkey)
    for code, tile_type in TILE_CODES.items():
        for mask in VICINITY_MASKS:
            for direction in DIRECTIONS:
                if code[1] != "0":
                    test = tile_directory[code[0]+"0"+mask+direction].copy()
                    if tile_type[1] in legend[tile_type[0]]:
                        test.blit(tile_directory[code+mask+direction], (0,0))
                    tile_directory[code+mask+direction] = test
    return tile_directory

def turn_vicinity(vicinity,direction):
    """Takes a vicinity 'vicinity' and turns it according to 'direction': "w" is no turn,
    "a" is turning left, "s" is turning upside down, "d" is turning right."""
    if direction == "w":
        return vicinity
    elif direction == "a":
        return ["".join([vicinity[i][2-j] for i in range(3)]) for j in range(3)]
    elif direction == "s":
        return ["".join([vicinity[2-j][2-i] for i in range(3)]) for j in range(3)]
    elif direction == "d":
        return ["".join([vicinity[2-i][j] for i in range(3)]) for j in range(3)]

def check_vicinity(vicinity, mask, direction):
    """Checks if the vicinity 'vicinity' matches the mask vicinity 'mask'
    turned by direction 'direction'. A character matches if it equals the
    corresponding mask character or equals "/". The vicinity matches if all
    the characters match."""
    mask = turn_vicinity(mask, direction)
    return all(all(mask[i][j] in vicinity[i][j]+"/" for j in range(3)) for i in range(3))

class Level():
    """This is the raw class for a single map the player can navigate through."""
    def load_file(self, filename):
        """Loads configuration from 'filename'."""
        # Initialize configuration parser
        parser = configparser.ConfigParser()
        parser.read(filename)

        # Load map
        self.map = parser.get("level", "map").split("\n")
        self.width = len(self.map[0])
        self.height = len(self.map)
        self.default_tile = parser.get("level","default_tile")

        self.player_position = [int(parser.get("player",i)) for i in "xy"]
        self.tile_set = parser.get("level", "tile_set")
        if self.tile_set == "ask":
            question = "Which tile set would you like to use?" 
            self.tile_set = ask_for_file(FOLDERS["MAPS"], ".png", question, True)
        self.variation = [[random.randint(0,VARIATION_GGT-1)
            for j in range(self.height + 2 * BORDER[1])] for i in range(self.width + 2 * BORDER[1])]
        # Loads tile set from file
        self.legend = configparser.ConfigParser()
        self.legend.read([FOLDERS["MAPS"] + "/{0}.leg".format(name) for name in ["default", self.tile_set]])
        tile_size_x = self.legend["info"].getint("size_x")
        tile_size_y = self.legend["info"].getint("size_y")
        self.tile_size = (tile_size_x, tile_size_y)
        self.dimensions = (self.width * tile_size_x,  self.height * tile_size_y)

    def get_tile_type(self, x, y):
        """ Gets type of the tile at ('x', 'y')."""
        if not ((0 <= x < self.width) and (0 <= y < self.height)):
            char = self.default_tile
        else:
            try:
                char = self.map[y][x]
            except IndexError:
                char = self.default_tile
        return char

    def get_tile_variation(self, x, y):
        """ Gets type of the tile at ('x', 'y')."""
        #if not (0<=x<self.width  + 2 * BORDER[1] and 0<=y<self.height + 2 * BORDER[1]):
        if not ((-BORDER[0] <= x <= self.width + BORDER[0])
                and (-BORDER[1] <= y <= self.height + BORDER[1])):
            var = 0
        else:
            try:
                var = self.variation[x - BORDER[0]][y - BORDER[1]]
            except IndexError:
                var = 0
        return var

    def get_tile_type_variant(self, x, y):
        tile_type = self.get_tile_type(x, y)
        variation = self.get_tile_variation(x, y)  % TILE_VARIATION_NUMBER[tile_type]
        return tile_type + str(variation)

    def get_tile_vicinity(self, x, y):
        """ Returns the vicinity type of the tile at ('x', 'y') as vicinity
        code."""
        # Determine vicinity of tile at position (x, y)
        tile_type = self.get_tile_type(x, y)
        vicinity = ["".join([str(int(self.get_tile_type(x+i,y+j) in SIMILAR[tile_type]))
            for i in (-1,0,1)]) for j in (-1,0,1)]
        # Check it against the vicinity masks
        for maskname,mask in VICINITY_MASKS.items():
            for direction in DIRECTIONS:
                #print(vicinity, mask, direction)
                if check_vicinity(vicinity, mask, direction):
                    return maskname+direction
        print("Vicinity check failed!")
        return "4fa"

    def get_tile_code(self, x, y):
        return self.get_tile_type_variant(x, y) + self.get_tile_vicinity(x, y)

    def render(self):
        """Renders the level map onto a PyGame surface and returns it."""
        # Load tile set
        self.tile_directory = load_tile_set(self.tile_set, self.legend)

        # Create PyGame surface and blit tiles on it
        #print(self.width * tile_size[0], self.height * tile_size[1])
        size_x = (self.width + 2 * BORDER[0]) * self.tile_size[0]
        size_y = (self.height + 2 * BORDER[1]) * self.tile_size[1]
        image = pygame.Surface((size_x, size_y))
        for y in range(-BORDER[1], self.height + BORDER[1]):
            for x in range(-BORDER[0], self.width + BORDER[0]):
                tile = self.tile_directory[self.get_tile_code(x, y)]
                image.blit(tile, ((x + BORDER[0]) * self.tile_size[0],
                    (y + BORDER[1]) * self.tile_size[1])) #, tile_size, tile_size))
        return image

def run():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                key = event.key
                if event.key == pygame.K_q:
                    running = False

def main():
    # Initialize PyGame
    pygame.init()

    # Get user input
    level_file = ask_for_file(FOLDERS["LEVELS"],".ini","Which level do you want to display?")
    print("User input complete!")

    # Initialize level
    level = Level()
    level.load_file(level_file)

    # Initialize screen
    #screen = pygame.display.set_mode(SCREEN_SIZE)
    screen = pygame.display.set_mode((1000,700))
    #screen = pygame.display.set_mode(level.dimensions)
    screen.fill((128,128,128))

    # Draw on screen
    background = level.render()
    screen.blit(background, (0, 0))
    pygame.display.flip()

    run()

    print("Quitting...")
    pygame.quit()

if __name__=="__main__":
    main()
