#!/usr/bin/env python3
import os
import translator
import logging
import time
import subprocess as sp
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler

unattended = True
config_file = 'translate_regions.yml'
log_file = 'translate_regions.log'
run_screen = lambda x: sp.run(f"bash sendScreenCMD.sh {x}".split(),shell=False, \
                       capture_output=True,encoding='latin-1').stdout


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)


class watchFile:
    def on_modified(event):
        logging.info('Change detected.')
        loadRegions = Thread(target=translator.main)
        loadRegions.start()

caseSensitive = False
ignoreDirectories = True
regexMatch = ["markers.yml"]
ignore_patterns = [".+bak|.+badValues"]
fileEventHandler = RegexMatchingEventHandler(regexMatch, ignore_patterns, ignoreDirectories, caseSensitive)

fileEventHandler.on_modified = watchFile.on_modified
goRecursively = False
my_observer = Observer()
my_observer.schedule(fileEventHandler, '/home/minecraft/JarlsServer/plugins/dynmap', recursive=goRecursively)

logging.info('Starting file observer')
my_observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    logging.info('Stopping file observer')
    my_observer.stop()
my_observer.join()
print('penis')
