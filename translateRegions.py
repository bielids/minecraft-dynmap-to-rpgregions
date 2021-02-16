#!/usr/bin/env python3
import os
import yaml
import re
import json
import subprocess as sp
import argparse

run_screen = lambda x: sp.run(f"bash sendScreenCMD.sh {x}".split(),shell=False, capture_output=True,encoding='latin-1').stdout

class colour:
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
    description="Alerts if configured hugepages do not match available hugepages")
parser.add_argument("-u", "--unattended", nargs='?', const=True, default=False, help="Will run unattended, use default options everywhere")
args = parser.parse_args()


def title_except(s, exceptions):
    word_list = re.split(' ', s)       # re.split behaves as expected
    final = [word_list[0].capitalize()]
    for word in word_list[1:]:
        final.append(word if word in exceptions else word.capitalize())
    return " ".join(final)


def load_files():
    try:
        with open(r'/home/minecraft/JarlsServer/plugins/dynmap/markers.yml', 'r') as file:
            dynmap_conf = yaml.load(file, Loader=yaml.Loader)
        with open(r'/home/minecraft/JarlsServer/plugins/WorldGuard/worlds/JarlsWorld/regions.yml', 'r') as file:
            worldguard_conf = yaml.load(file, Loader=yaml.Loader)
    except:
        print("welp, that didn't work")

    return (dynmap_conf, worldguard_conf)


def load_defaults():
    try:
        with open(r'worldguard.default', 'r') as file:
            wg_def = yaml.load(file, Loader=yaml.Loader)
        with open(r'rpgregions.default', 'r') as file:
            rpg_def = json.load(file)
    except:
        print("welp, that didn't work")

    return (wg_def, rpg_def)


def write_worldguard(wg_conf, dm_conf, wg_def):
    new_regions_wg = []
    wg_changes = False
    for key in dm_conf['sets']['Counties']['areas'].keys():
        region_name = dm_conf['sets']['Counties']['areas'][key]['label'].lower().replace(' ', '_').strip('')
        region_name = re.sub('[!@#$()]', '', region_name)
        if region_name not in wg_conf['regions'].keys():
            new_regions_wg.append(key)
            wg_changes = True
            print(f"Going to create new region called '{region_name}'.")
        else:
            print(f"'{region_name}' already exists in WorldGuard. Skipping...")
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
        print('Writing changes to WorldGuard')
        try:
            with open(r'/home/minecraft/JarlsServer/plugins/WorldGuard/worlds/JarlsWorld/regions.yml', 'w') as write_out:
                out = yaml.dump(wg_conf, write_out)
                print(f"{colour.GREEN}Wrote all regions to plugins/WorldGuard/worlds/JarlsWorld/regions.yml{colour.END}")
                run_screen("rg reload")
        except:
            print('fuck')
    else:
        print(f'{colour.YELLOW}No changes being made to WorldGuard{colour.END}')

    return wg_conf


def write_rpgregions(wg_conf, rpg_def, unattended):
    json_out = []
    new_regions_rpg = []
    rpg_changes = False
    articles = ['a', 'an', 'of', 'the', 'is']
    run_screen("rpgregions save")
    for key in wg_conf['regions'].keys():
        if os.path.exists(f'regions/{key}.json'):
            overwrite_region = False
            if unattended:
                overwrite_region = False
            else:
                overwrite_region = {"y":True,"n":False}[input(f'{key} already exists. Do you wish to overwrite the RPGRegions file? (y/N)').lower().strip() or 'n']
            if overwrite_region:
                new_regions_rpg.append(key)
        else:
            new_regions_rpg.append(key)
    for region in new_regions_rpg:
        nr = rpg_def
        nr['id'] = region
        nr['customName'] =  title_except(re.sub('_', ' ', region), articles)
        nr['subtitle'] = \
        [
            title_except(re.sub('_', ' ', region), articles)
        ]
        try:
            with open(f'regions/{region}.json', 'w') as file:
                print(f'Writing new region to plugins/RPGRegions/regions/{region}.json')
                json.dump(nr, file, indent=2, sort_keys=False)
                rpg_changes = True
        except:
            print(f'Unable to write {region} to regions folder')
    if rpg_changes:
        run_screen("rpgregions reload")
        run_screen("rpgregions")
        print(f'{colour.GREEN}Wrote changes to RPGRegions{colour.END}')


def main():
    dm_conf, wg_conf = load_files()
    wg_def, rpg_def = load_defaults()
    wg_conf = write_worldguard(wg_conf, dm_conf, wg_def)
    write_rpgregions(wg_conf, rpg_def, args.unattended)


if __name__ == "__main__":
    main()
