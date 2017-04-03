#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2017-04-01
# tiles.py: Trying the pygame tiles tutorial from qq.readthedocs.io

import os
import pygame
import pygame.locals
import configparser

TILE_SIZE = 24
OFFSET = (9, 163)
COLORKEY = (0,128,128)
TILES = ".Xo"
BORDER = 2
MAPS_FOLDER = "tile_sets/maps"
AVATAR_FOLDER = "tile_sets/avatars"
LEVEL_FOLDER = "levels"
PLAYER_FOLDER = "players"
SIMILAR = {"X":"X",
           ".":".o",
           "o":"o"}

def ask_for_file(directory,extension,question):
    return_string = directory + "/{0}" + extension
    n = len(extension)
    options = [name[:-n] for name in os.listdir(directory) if (name[-n:] == extension)]
    if options == []:
        return None
    elif len(options) == 1:
        print(question+" Option {0} was automatically selected.".format(options[0]))
        return return_string.format(options[0])
    options.sort()
    while True:
        option = input(question+" ("+", ".join(options)+") ")
        if option in options:
            break
        print("Not a valid choice!")
    print("Option {0} selected.".format(option))
    return return_string.format(option)

def load_tile(x,y,filename):
    image = pygame.image.load(filename).convert()
    image.set_colorkey(COLORKEY)
    rect=(x,y,TILE_SIZE,TILE_SIZE)
    return image.subsurface(rect)

def load_tiles(xy_dir, filename):
    image = pygame.image.load(filename).convert()
    image.set_colorkey(COLORKEY)
    tile_dir = {}
    for key in xy_dir:
        x,y=xy_dir[key]
        rect = (x,y,TILE_SIZE,TILE_SIZE)
        #print(key, rect)
        tile_dir[key]=image.subsurface(rect)
    return tile_dir

def turn_vicinity(vicinity,direction):
    if direction == "w":
        return vicinity
    elif direction == "a":
        return ["".join([vicinity[i][2-j] for i in range(3)]) for j in range(3)]
    elif direction == "s":
        return ["".join([vicinity[2-j][2-i] for i in range(3)]) for j in range(3)]
    elif direction == "d":
        return ["".join([vicinity[2-i][j] for i in range(3)]) for j in range(3)]

def check_vicinity(vicinity, mask, direction):
    mask = turn_vicinity(mask, direction)
    #print(vicinity, mask)
    return all(all(mask[i][j] in vicinity[i][j]+"/" for j in range(3)) for i in range(3))

class Level():
    #def load_vicinities(self, filename):
        #parser = configparser.ConfigParser()
        #parser.read(filename)
        #self.vicinity_masks = [(sec, parser.get(sec,"mask").split("\n")) for sec in parser.sections()]
        #print(self.vicinity_masks)
        #print("Something went wrong: Vicinities were loaded manually!")

    def load_file(self, filename):
        self.map=[]
        self.key={}

        parser = configparser.ConfigParser()
        parser.read(filename)
        self.map = parser.get("level","map").split("\n")
        #print(type(self.map), self.map)
        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc
        self.width = len(self.map[0])
        self.height = len(self.map)

        self.player_pos = [int(parser.get("player",i)) for i in "xy"]

        #####
        #self.xy_dir = {char:(int(parser.get(char,"x")),int(parser.get(char,"y"))) for char in TILES}
        self.tile_file = MAPS_FOLDER+"/"+parser.get("level","tile_set")+".png"

    def get_tile_dir(self, x, y):
        if not (0<=x<self.width and 0<=y<self.height):
            char = "X"
        else:
            try:
                char = self.map[y][x]
            except IndexError:
                return {}
        try:
            return self.key[char]
        except KeyError:
            return {}

    def get_tile_type(self, x, y):
        if not (0<=x<self.width and 0<=y<self.height):
            char = "X"
        else:
            try:
                char = self.map[y][x]
            except IndexError:
                char = "X"
        return char

    def get_tile_vicinity(self,x,y):
        tile_type = self.get_tile_type(x, y)
        vicinity = ["".join([str(int(self.get_tile_type(x+i,y+j) in SIMILAR[tile_type]))
            for i in (-1,0,1)]) for j in (-1,0,1)]
        #print(self.vicinity_masks)
        for maskname,mask in self.vicinity_masks:
            for direction in "wasd":
                if check_vicinity(vicinity, mask, direction):
                    #print("\n".join(vicinity),"\n", maskname+direction)
                    return maskname+direction
                #input("Vicinities did not match:\n{0}\n{1}".format("\n".join(vicinity),"\n".join(mask)))
        print("Vicinity check failed!")
        return "4fa"

    def get_tile_name(self,x,y):
        tile_type = self.get_tile_type(x,y)
        if tile_type in "Xo.":
            return tile_type+self.get_tile_vicinity(x,y)
        elif tile_type == ".":
            return "."
        return "X4fa"

    def render(self,screen):
        vicinity_mask_parser = configparser.ConfigParser()
        vicinity_mask_parser.read("vicinity_masks.ini")
        self.vicinity_masks = [(sec, vicinity_mask_parser.get(sec,"mask").split("\n")) for sec in vicinity_mask_parser.sections()]

        tile_table_parser = configparser.ConfigParser()
        tile_table_parser.read("tile_table.ini")

        vicinity_names=tile_table_parser.sections()

        raw_wall_xy_dir = {name:[int(tile_table_parser.get(name,i)) for i in "yx"] for name in vicinity_names}
        wall_xy_dir = {("X"+name):(OFFSET[0] + (TILE_SIZE+1) * raw_wall_xy_dir[name][0], OFFSET[1] + (TILE_SIZE+1) * raw_wall_xy_dir[name][1]) for name in vicinity_names}

        raw_water_xy_dir = {name:[int(tile_table_parser.get(name,i)) for i in "yx"] for name in vicinity_names}
        for name in raw_water_xy_dir:
            raw_water_xy_dir[name][0]+=21
        water_xy_dir = {("o"+name):(OFFSET[0] + (TILE_SIZE+1) * raw_water_xy_dir[name][0], OFFSET[1] + (TILE_SIZE+1) * raw_water_xy_dir[name][1]) for name in vicinity_names}

        raw_floor_xy_dir = {name:[int(tile_table_parser.get(name,i)) for i in "yx"] for name in vicinity_names}
        for name in raw_floor_xy_dir:
            raw_floor_xy_dir[name][0]+=9
        floor_xy_dir = {("."+name):(OFFSET[0] + (TILE_SIZE+1) * raw_floor_xy_dir[name][0], OFFSET[1] + (TILE_SIZE+1) * raw_floor_xy_dir[name][1]) for name in vicinity_names}

        #xy_dir = {**wall_xy_dir, **water_xy_dir, **floor_xy_dir}
        xy_dir = {}
        xy_dir.update(wall_xy_dir)
        xy_dir.update(water_xy_dir)
        xy_dir.update(floor_xy_dir)
        #print(xy_dir)

        #print(raw_xy_dir)
        #print(xy_dir)
        tile_dir = load_tiles(xy_dir,self.tile_file)
        for y in range(-BORDER,self.height+BORDER):
            for x in range(-BORDER,self.width+BORDER):
                #print(self.get_tile(x,y))
                #if self.get_tile(x,y)["name"] == "wall":
                    #print(x,y)
                    #pygame.draw.rect(screen, (0,0,0), (TILE_SIZE*x, TILE_SIZE*y, TILE_SIZE, TILE_SIZE), 0)
                    #pygame.Rect(TILE_SIZE*x, TILE_SIZE*y, TILE_SIZE, TILE_SIZE)
                #print(x,y)
                #print(x,y,self.get_tile_vicinity(x,y))
                tile=tile_dir[self.get_tile_name(x,y)]
                screen.blit(tile,((BORDER+x)*TILE_SIZE,(BORDER+y)*TILE_SIZE))

class Player():
    def __init__(self,x,y):
        self.pos = (x,y)

    def load_file(self, filename):
        print(filename)
        parser = configparser.ConfigParser()
        parser.read(filename)
        tile_set = parser.get("tiles","tile_set")
        self.tile_file = AVATAR_FOLDER+"/" + tile_set + ".png"
        self.tile_xy = (int(parser.get("tiles","x")), int(parser.get("tiles","y")))

    def render(self,screen):
        tile = load_tile(*self.tile_xy, self.tile_file)
        x,y=self.pos
        screen.blit(tile,((BORDER+x)*TILE_SIZE,(BORDER+y)*TILE_SIZE))

def main():
    pygame.init()
    map_file = ask_for_file(LEVEL_FOLDER,".ini","Which level do you want to display?")
    map_style_file = ask_for_file(MAPS_FOLDER,".png","Which map style do you want to use?")
    player_file = ask_for_file(PLAYER_FOLDER,".ini","Which avatar do you want to use?")
    print("User input completed!\n")

    level = Level()
    level.load_file(map_file)
    level.tile_file = map_style_file

    player = Player(*level.player_pos)
    player.load_file(player_file)

    #map_number = input("Which map shall be displayed? (01, 02 or 03) ")
    #level.load_file(LEVEL_FOLDER+"/{0}.ini".format(map_number))
    #level.load_vicinities("vicinity_masks.ini")
    #style_options = [name[:-4] for name in os.listdir(LEVEL_FOLDER) if (name[-4:] == ".png")]
    #style_options_string = "("+", ".join(style_options)+")"
    #map_style = input("Which style shall be used? {0} ".format(style_options_string))
    #level.tile_file = LEVEL_FOLDER+"/{0}.png".format(map_style)
    #player = Player(*level.player_pos)
    #player.load_file(PLAYER_FOLDER+"/treecko.ini")

    #print("Pixelsize:", TILE_SIZE, TILE_SIZE)
    #print(level.width, level.height)
    screen = pygame.display.set_mode((TILE_SIZE*(2*BORDER+level.width), TILE_SIZE*(2*BORDER+level.height)))
    screen.fill((0,128,128))
    level.render(screen)
    player.render(screen)
    #screen.blit(level.tiledir["player"],(3*TILE_SIZE,3*TILE_SIZE))
    pygame.display.flip()
    while pygame.event.wait().type != pygame.locals.QUIT:
        pass
    #running = True
    #while running:
        #pass
    pygame.quit()

if __name__=="__main__":
    main()
