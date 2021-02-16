# minecraft-dynmap-to-rpgregions
Convert Dynmap regions to WorldGuard/RPGRegions

Place these files in plugins/RPGRegions, update `worldName` to your world's name in translateRegions.py and finally run translateRegions.py from plugins/RPGRegions (it assumes that this is where it's running from because I'm a lazy dev). 

## Assumptions I make

- Everything found in this repo lives in plugins/RPGRegions
- You haven't renamed any of the other plugins' directories
- The regions you are converting from Dynmap -> RPGRegions are all contained within the "Counties" marker set 
- You used polygons to create your markers/regions in Dynmap
- Your minecraft server is running in a screen under the `mcs` name

## How to make this work for your server 

- make sure that you follow all the assumptions mentioned above 
- update the world name and UID in rpgregions.default
- update the `worldName` variable in translateRegions.py

Eventually I'll make this more streamlined but I put this together quickly in the past day.

## To do

- add wrapper for this whole thing to allow people to quickly update all custom values (ex world UID or name)
- - ie. rpgregions.default and translateRegions.py
- setup watchdog to watch for changes in dynmap's markers.yml and run script whenever a change occurs (unattended mode already implemented)
- probably ought to use more classes
- add logging

## Notes 

I wrote this for myself. If this breaks your server, that's on you. 
