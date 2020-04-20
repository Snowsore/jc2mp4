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

import timeit

#
# Voice detection
#

# Preper
start = timeit.default_timer()
ifile = sys.argv[1]
ofile = sys.argv[2]
sensitivity = sys.argv[3]
os.mkdir('./TEMP')

# Extract audio
cmd = 'ffmpeg -loglevel panic -i "{}" ./TEMP/temp.wav'.format(ifile)
subprocess.call(cmd, shell = True)

# Get data
wav = wavfile.read('./TEMP/temp.wav')
sample_rate = wav[0]
data = wav[1]

# Sensetive
mask = (data[:,0] > sensitivity) | (data[:,0] < -sensitivity)

# Dum filtering
dynamic = 0
release = 0
for i in range(100):
    if dynamic > sample_rate / 60:
        for l in range(i):
            mask = np.logical_or(mask, np.roll(mask, -2 ** l))
        break
    dynamic += 2 ** i;

for i in range(100):
    if release > sample_rate / 60:
        for l in range(i):
            mask = np.logical_or(mask, np.roll(mask, 2 ** l))
        break
    release += 2 ** i;

# Output audio
wavfile.write('./TEMP/audio.wav', sample_rate, data[~np.array(mask)])

# Output list
mask = np.insert(mask, 0, 0)
mask = np.append(mask, 0)
flat = np.flatnonzero(np.diff(mask)) / sample_rate

audio_start = flat[0::2]
audio_stop = flat[1::2]
duration_mask = (audio_stop - audio_start) > 0.2

audio_start = audio_start[duration_mask]
audio_stop = audio_stop[duration_mask]
audio_duration = audio_stop - audio_start

print("{} div {}".format(len(audio_start), ifile))

#
# Render video
#

# Split video by list(add filter)
fstr = ''
cp = []
for i in range(len(audio_start)):
    cmd = 'ffmpeg -loglevel panic -ss {} -i "{}" -t {} ./TEMP/clip{}.mov'.format(audio_start[i], ifile, audio_duration[i], i)
    fstr += "file './clip" + str(i) + ".mov'\n"

    while len(cp) > 7:
        for p in cp:
            if p.poll() is not None:
                cp.remove(p)
        time.sleep(0.01)
        
    cp.append(subprocess.Popen(cmd, shell = True))
    print('\r{0:.0%}'.format(i / len(audio_start)), end="")
for p in cp:
    p.wait()

# Output merge list
f = open('./TEMP/concat.txt', 'w')
f.write(fstr)
f.close()

# Merge video
cmd = 'ffmpeg -loglevel panic -f concat -safe 0 -i ./TEMP/concat.txt "{}"'.format(ofile)
subprocess.call(cmd, shell = True)  

# Delete temp file
shutil.rmtree('./TEMP')

# Show time spend
stop = timeit.default_timer()
print('Time: ', stop - start)  
