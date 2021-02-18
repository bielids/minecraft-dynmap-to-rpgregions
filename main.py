#!/usr/bin/env python3
import os
import yaml
import re
import json
import subprocess as sp
import argparse
import logging
import uuid
import readline

config_file = 'translate_regions.yml'
log_file = 'translate_regions.log'
run_screen = lambda x: sp.run(f"bash sendScreenCMD.sh {x}".split(),shell=False, capture_output=True,encoding='latin-1').stdout

class clr:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

parser = argparse.ArgumentParser(
    description="Covert dynmap regions to WorldGuard and RPGRegions")
parser.add_argument("-u", "--unattended", nargs='?', const=True, default=False, help="Will run unattended, use default options everywhere")
parser.add_argument("--wg-only", nargs='?', const=True, default=False, help="Will convert to WorldGuard only")
parser.add_argument("--rpg-only", nargs='?', const=True, default=False, help="Will convert to RPGRegions only (dangerous)")
args = parser.parse_args()


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)


def rlinput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)  # or raw_input in Python 2
   finally:
      readline.set_startup_hook()


def title_except(s, exceptions):
    word_list = re.split(' ', s)       # re.split behaves as expected
    final = [word_list[0].capitalize()]
    for word in word_list[1:]:
        final.append(word if word in exceptions else word.capitalize())
    return " ".join(final)


def load_config():
    global config
    logging.debug('Loading config file...')
    if not os.path.exists(config_file):
        initialise_config()
    else:
        try:
            with open(config_file, 'rb') as file:
                config = yaml.load(file, Loader=yaml.Loader)
                logging.info('Successfully loaded config')
        except Exception as err:
            logging.error(f'Unable to load config: {err}')
            exit(2)

def get_world_name():
    logging.debug('Getting world name from server.properties...')
    try:
        with open('../server.properties', 'r') as file:
            lvlre = re.compile('^level-name=')
            for line in file.readlines():
                if re.match(lvlre, line):
                    world_name = line.strip().split('=')[1]
            logging.debug('Read world name from server.properties')
    except Exception as err:
        logging.error(f"Couldn't find server.properties where I expected it... {err}")
        exit(2)
    return world_name


def get_world_uuid(world_name):
    logging.debug(f"Getting world UUID from ../{world_name}/uid.dat")
    try:
        with open(f"../{world_name}/uid.dat", 'rb') as file:
            world_uuid = uuid.UUID(bytes=file.read(16))
            logging.debug(f"Read UUID from ../{world_name}/uid.dat")
    except Exception as err:
        logging.error('Unable to get world UUID. Cannot continue.')

    return str(world_uuid)


def initialise_config():
    global config
    config = {}
    logging.debug('Starting user-interactive config initialisation')
    print(f"{clr.GREEN}Please initialise your config before starting!\n{clr.END}")
    config['world_name'] = rlinput("What world do you want to export the regions to? ", get_world_name())
    logging.debug(f"{config['world_name']} selected.")
    config['world_uuid'] = get_world_uuid(config['world_name'])
    try:
        with open(config_file, 'w') as file:
            yaml.dump(config, file)
            logging.info('Successfully saved config')
    except Exception as err:
        logging.error('Unable to save config')

def load_files():
    try:
        logging.debug('Loading Dynmap markers file...')
        with open(r'../plugins/dynmap/markers.yml', 'r') as file:
            dynmap_conf = yaml.load(file, Loader=yaml.Loader)
            logging.info('Loaded Dynmap markers file')
        logging.debug('Loading WorldGuard regions config file')
    except Exception as err:
        logging.error(f"Unable to load Dynmap file: {err}")
        exit(2)
    try:
        with open(f"../plugins/WorldGuard/worlds/{config['world_name']}/regions.yml", 'r') as file:
            worldguard_conf = yaml.load(file, Loader=yaml.Loader)
            logging.info('Loaded WorldGuard regions file')
    except Exception as err:
        logging.error(f"Unable to load WorldGuard file: {err}")
        exit(2)

    return (dynmap_conf, worldguard_conf)


def load_defaults():
    logging.info('Loading defaults files...')
    try:
        with open(r'worldguard.default', 'r') as file:
            wg_def = yaml.load(file, Loader=yaml.Loader)
        with open(r'rpgregions.default', 'r') as file:
            rpg_def = json.load(file)
    except:
        print("welp, that didn't work")

    return (wg_def, rpg_def)


def write_worldguard(wg_conf, dm_conf, wg_def):
    logging.debug(f"{'=' * 8}Starting WorldGuard region loading... {'=' * 8}")
    new_regions_wg = []
    wg_changes = False
    for key in dm_conf['sets']['Counties']['areas'].keys():
        region_name = dm_conf['sets']['Counties']['areas'][key]['label'].lower().replace(' ', '_').strip('')
        region_name = re.sub('[!@#$()]', '', region_name)
        if region_name not in wg_conf['regions'].keys():
            new_regions_wg.append(key)
            wg_changes = True
            logging.debug(f"Going to create new region called '{region_name}'.")
        else:
            logging.debug(f"'{region_name}' already exists in WorldGuard. Skipping...")
    logging.debug('Regions acquired, starting point translation')
    for region in new_regions_wg:
        region_name = dm_conf['sets']['Counties']['areas'][region]['label'].lower().replace(' ', '_').strip('') # got lazy, should be removed
        region_name = re.sub('[!@#$()]', '', region_name) # same here :(
        x = dm_conf['sets']['Counties']['areas'][region]['x']
        z = dm_conf['sets']['Counties']['areas'][region]['z']
        points = []
        for index, x_pos in enumerate(x):
            points.append({'x': x_pos, 'z': z[index]})
        r = wg_def['default']
        r['points'] = points
        wg_conf['regions'][region_name] = {}
        wg_conf['regions'][region_name].update(r)

    if wg_changes:
        logging.info('Writing changes to WorldGuard')
        try:
            with open(f"../plugins/WorldGuard/worlds/{config['world_name']}/regions.yml", 'w') as write_out:
                out = yaml.dump(wg_conf, write_out)
                logging.info(f"Wrote all regions to plugins/WorldGuard/worlds/{config['world_name']}/regions.yml")
                run_screen("rg reload")
        except:
            logging.error(f"Unable to write regions to plugins/WorldGuard/worlds/{config['world_name']}/regions.yml")
    else:
        logging.debug('No changes being made to WorldGuard')

    return wg_conf


def write_rpgregions(wg_conf, rpg_def, unattended):
    logging.debug(f"{'=' * 8} Starting RPGRegions region loading... {'=' * 8}")
    json_out = []
    new_regions_rpg = []
    rpg_changes = False
    articles = ['a', 'an', 'of', 'the', 'is']
    run_screen("rpgregions save")
    for key in wg_conf['regions'].keys():
        if os.path.exists(f'../plugins/RPGRegions/regions/{key}.json'):
            overwrite_region = False
            if unattended:
                logging.debug(f"'{key}' already exists in RPGRegions. Skipping...")
                overwrite_region = False
            else:
                overwrite_region = {"y":True,"n":False}[input(f'{key} already exists. Do you wish to overwrite the RPGRegions file? (y/N)').lower().strip() or 'n']
            if overwrite_region:
                new_regions_rpg.append(key)
        else:
            new_regions_rpg.append(key)
    logging.debug('Starting RPGRegions region generation...')
    for region in new_regions_rpg:
        nr = rpg_def
        nr['id'] = region
        nr['customName'] =  title_except(re.sub('_', ' ', region), articles)
        nr['subtitle'] = \
        [
            title_except(re.sub('_', ' ', region), articles)
        ]
        try:
            with open(f'../plugins/RPGRegions/regions/{region}.json', 'w') as file:
                logging.info(f'Writing new region to ../plugins/RPGRegions/regions/{region}.json')
                json.dump(nr, file, indent=2, sort_keys=False)
                rpg_changes = True
        except:
            print(f'Unable to write {region} to regions folder')
    if rpg_changes:
        run_screen("rpgregions reload")
        run_screen("rpgregions")
        logging.info('Wrote changes to RPGRegions')
    else:
        logging.debug('No changes made to RPGRegions.')


def main():
    if not re.search('.*scripts$', os.path.dirname(os.path.abspath(__file__))):
        logging.error('Please run script for correct folder. See README.md for info')
        exit(1)
    else:
        logging.debug('Script in correct directory, continuing...')
    load_config()
    dm_conf, wg_conf = load_files()
    wg_def, rpg_def = load_defaults()
    wg_conf = write_worldguard(wg_conf, dm_conf, wg_def)
    write_rpgregions(wg_conf, rpg_def, args.unattended)
    logging.info(f"{'=' * 8} Region conversion complete. {'=' * 8}")

if __name__ == "__main__":
    main()
