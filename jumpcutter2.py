#!/usr/bin/env python3 

# Jumpcutter2

# Imports
from scipy.io import wavfile
import numpy as np
import sys

import subprocess
import os
import time
import shutil
import random

#
# Voice detection
#

# Preper
ifile = sys.argv[1]
ofile = sys.argv[2]
os.mkdir('./TEMP')

# Extract audio
cmd = 'ffmpeg -loglevel panic -i ' + ifile + ' ./TEMP/temp.wav'
subprocess.call(cmd, shell = True)

# Get data
wav = wavfile.read('./TEMP/temp.wav')
data = wav[1]

# Sensetive
mask = (data[:,0] > 3000) | (data[:,0] < -3000)

# Dum filtering
for i in range(14):
    mask = np.logical_or(mask, np.roll(mask, 2 ** i))
mask = np.logical_or(mask, np.roll(mask, -2 ** i))

# Output list
sam = []
flat = np.diff(np.r_[0,np.flatnonzero(np.diff(mask))+1,mask.size])
for i in range(flat.size):
    s = flat[:i].sum()
    sam.append([s, int(mask[s])])

# Replace sample to time and play rate
for i in range(len(sam)):
    if(sam[i][1]):
        s = 1.5
    else:
        s = 0
    sam[i] = [sam[i][0] / 44100, s]

#
# Render video
#

# Split video by list(add filter)
fstr = ''
cp = []
for i in range(len(sam) - 1):
    if not sam[i][1]:
        continue
    cmd = 'ffmpeg -loglevel panic -ss ' + str(sam[i][0])+ ' -to ' + str(sam[i + 1][0])+ ' -i ' + ifile + ' -filter_complex "setpts=' + str(1 / sam[i][1]) + '*PTS;atempo=' + str(1 * sam[i][1]) + '" ./TEMP/clip' + str(i) + '.mp4'

    fstr += "file './clip" + str(i) + ".mp4'\n"
    cp.append(subprocess.Popen(cmd, shell = True))
    print('\r{0:.0%}'.format(i / len(sam)), end="")
    while len(cp) > 8:
        for p in cp:
            if p.poll() is not None:
                cp.remove(p)
        time.sleep(0.01)
for p in cp:
    p.wait()

# Output merge list
f = open('./TEMP/concat.txt', 'w')
f.write(fstr)
f.close()

# Merge video
cmd = 'ffmpeg -loglevel panic -f concat -safe 0 -i ./TEMP/concat.txt -codec copy ' + ofile
subprocess.call(cmd, shell = True)

# Delete temp file
shutil.rmtree('./TEMP')