#!/bin/bash

args=${@}

/usr/bin/screen -S mcs -p0 -X stuff "${args} \n"
