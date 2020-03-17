#!/usr/bin/env python3
# Inspire by carykh
# Rewrite By Snowsore

# jc2mp4

# Imports
from scipy.io import wavfile
import numpy as np
import sys

import subprocess
import os
import time
import shutil
import random

import timeit

#
# Voice detection
#

# Preper
start = timeit.default_timer()
ifile = sys.argv[1]
ofile = sys.argv[2]
os.mkdir('./TEMP')

# Extract audio
cmd = 'ffmpeg -loglevel panic -i {} ./TEMP/temp.wav'.format(ifile)
subprocess.call(cmd, shell = True)

# Get data
wav = wavfile.read('./TEMP/temp.wav')
sampleRate = wav[0]
data = wav[1]

# Sensetive
mask = (data[:,0] > 800) | (data[:,0] < -800)

# Dum filtering
dynamic = 0
release = 0
for i in range(100):
    dynamic += 2 ** i;
    if dynamic > 0.06 * sampleRate:
        for l in range(i):
            mask = np.logical_or(mask, np.roll(mask, -2 ** l))
        break
for i in range(100):
    release += 2 ** i;
    if release > 0.06 * sampleRate:
        for l in range(i):
            mask = np.logical_or(mask, np.roll(mask, 2 ** l))
        break

# Output list
mask = np.insert(mask, 0, 0)
mask = np.append(mask, 0)
flat = np.flatnonzero(np.diff(mask))
flat = flat / sampleRate
print("{} div {}".format(len(flat) / 2, ifile))

#
# Render video
#

# Split video by list(add filter)
fstr = ''
cp = []
for i in range(len(flat) - 1):
    if i % 2:
        continue
    if flat[i + 1] - flat[i] < 0.1:
        continue

    cmd = 'ffmpeg -loglevel panic -ss {} -i {} -t {} ./TEMP/clip{}.mp4'.format(flat[i], ifile, flat[i + 1] - flat[i], i)
    fstr += "file './clip" + str(i) + ".mp4'\n"
    
    cp.append(subprocess.Popen(cmd, shell = True))
    print('\r{0:.0%}'.format(i / len(flat)), end="")
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
# cmd = 'ffmpeg -loglevel panic -f concat -safe 0 -i ./TEMP/concat.txt -c:v h264_nvenc -filter_complex "setpts=PTS/{};atempo={}" -async 1 {}'.format(1.5, 1.5, ofile)
cmd = 'ffmpeg -loglevel panic -f concat -safe 0 -i ./TEMP/concat.txt -c:v h264_nvenc -filter_complex "setpts=PTS/{};loudnorm,atempo={}" -async 1 -b:v 400k -c:a aac -b:a 160k -ar 44100 {}'.format(1.5, 1.5, ofile)
subprocess.call(cmd, shell = True)

# Delete temp file
shutil.rmtree('./TEMP')

# Show time spend
stop = timeit.default_timer()
print('Time: ', stop - start)  