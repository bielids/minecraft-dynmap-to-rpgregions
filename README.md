# minecraft-dynmap-to-rpgregions
Convert Dynmap regions to WorldGuard/RPGRegions

Place these files in `your_minecraft_server_folder/scripts`, and run main.py. 

## Assumptions I make

- Everything found in this repo lives in `your_minecraft_server_folder/scripts`
- You haven't renamed any of the other plugins' directories
- The regions you are converting from Dynmap -> RPGRegions are all contained within the "Counties" marker set 
- You used polygons to create your markers/regions in Dynmap
- Your minecraft server is running in a screen under the `mcs` name
- 
## To do

- setup watchdog to watch for changes in dynmap's markers.yml and run script whenever a change occurs (unattended mode already implemented)
- probably ought to use more classes
- allow modification of RPGRegion region attributes before creating json file (ex. change reward or title/subtitle)

## Notes 

I wrote this for myself. If this breaks your server, that's on you. 
