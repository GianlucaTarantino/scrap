#!/usr/bin/env python3
import os
import argparse
from scrap import cosmic, radiation

# Getting Arguments and checking if mode is valid
parser = argparse.ArgumentParser(description='Scrap (Scientific Camera for Radiations and Analysis of Particles) uses a camera to detect and analyze radiations and cosmic rays')
parser.add_argument("-m", "--mode", help="select mode between 1 (cosmic rays), 2 (detect radiation and particles)", type=int)
parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
parser.add_argument("-s", "--show", action="store_true", help="visualize graphic output")
parser.add_argument("-j", "--jpg", action="store_true", help="saves jpg of eventual cosmic ray")
parser.add_argument("-i", "--init", action="store_true", help="init the workspace")
args = parser.parse_args()
mode = args.mode

if args.init:
    try:
        os.mkdir('./data')
        os.mkdir('./data/cosmicrays')
        open('./data/cosmicrays/cosmic_rays.json', 'w').write('{"count": 0, "cosmic_rays": []}')
        open('data/particles.json', 'w').write('[]')
    except Exception as e:
        print('Unknown error while trying to create the workspace directories and files.')
        raise
    os._exit(0)

if not mode or mode < 0 or mode > 3:
    print("Invalid mode selected. Check the help page with the -h flag. Going with default mode (1)")
    mode = 1

# Cosmic Rays Detection
if mode == 1:
    print("\nStarted Cosmic Rays detection")
    cosmic(args.jpg)
elif mode == 2:
    print("\nStarted Particles and Radiations detection")
    radiation()
