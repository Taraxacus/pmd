#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2017-04-03
# iniremaker.py: Reformat inifiles

import configparser
import os

INIFILE="tile_table.ini"

def main():
    inifile = INIFILE
    parser = configparser.ConfigParser()
    parser2 = configparser.ConfigParser()
    parser.read(inifile)
    parser2["tile_table"] = {}
    for section in parser.sections():
        parser2["tile_table"][section + "x"] = str(int(parser[section]["y"]) - 3)
        parser2["tile_table"][section + "y"] = parser[section]["x"]
    newfile_name = inifile[:-4]+"-re"+inifile[-4:]
    if os.path.isfile(newfile_name):
        print("Error: File {0} already exists.".format(newfile_name))
    else:
        newfile = open(newfile_name,"w")
        parser2.write(newfile)
        newfile.close()

if __name__=="__main__":
    main()
