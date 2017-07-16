# Jake Mayeux
# July 2017
# purge-tower.py

import re
import sys
import getopt
from os import walk

absolute = -1

towerfile = 'tower.gcode'

infile = 'out.gcode'

outfile = 'out2.gcode'

towerFiles = []

towers = []

towersPath = 'PurgeTXTs'

numTowers = 0

zhop = float(1.0) # needed to properly detect layer changes

zpos = float(0.0)

tn = -1

data = {}

ltn = -1 # last Tn
maxSwaps = 0
swaps = 0

opts, extraparams = getopt.getopt(
   sys.argv[1:],
   'z:f:o:',
   ['zhop', 'infile', 'outfile'])
for o, p in opts:
   if o in ['-z', '--zhop']:
      zhop = p
   elif o in ['-f', '--infile']:
      infile = p
   elif o in ['-o', '--outfile']:
      outfile = p

inf = open(infile, 'r')
ouf = open(outfile, 'w')

lines = inf.readlines()

def getValue(line, key, default=None):
    if (key not in line) or (';' in line and line.find(key) > line.find(';')):
        return default
    sub_part = line[line.find(key) + 1:]
    m = re.search('^[0-9]+\.?[0-9]*', sub_part)
    if m is None:
        return default
    try:
        return float(m.group(0))
    except ValueError:
        return default

for (dirpath, dirnames, filenames) in walk(towersPath):
   towerFiles.extend(filenames)
   break

# find max # of times were going to change colors
for l in lines:
   ouf.write(l)
   i = l.find(' ')
   if (i == -1):
      gc = l
   else:
      gc = l[0:i]
   
   # remove comments
   if (gc.find(';') != -1):
      gc = gc[:gc.find(';')]

   if (gc == 'G1'):
      # check if Z has changed, check if it is a zhop movement
      newz = getValue(l, 'Z', -1)
      if (newz != -1 and newz - zpos < zhop - 0.01 and newz != zpos):
         if (zpos == 0):
            zpos = newz
         else:
            # new layer here
            #ouf.write('TNEW '+str(zpos)+' '+str(newz)+'\n')
            print('new layer')
            zpos = newz
            swaps = 0
            #print('reset')
   elif (gc[0:1] == 'T'):
      tn = int(gc[1:])
      if (ltn == -1):
         ltn = tn
      elif (tn != ltn):
         print('new swap', ltn, tn)
         ltn = tn
         swaps += 1
         #print('swap', swaps, l)
         if (swaps > maxSwaps):
            maxSwaps = swaps

 
for f in sorted(towerFiles):
   towers.append(open(towersPath+'/'+f, 'r').readlines())

print('maxSwaps', maxSwaps)

def drawNextTower():
   global swaps
   if (swaps > len(towers) - 1):
      print('not enough towers, skipping purge')
   else:
      for l in towers[swaps]:
         if (l.find('Z') == -1):
            ouf.write(l)
   swaps += 1


for l in lines:
   ouf.write(l)
   i = l.find(' ')
   if (i == -1):
      gc = l
   else:
      gc = l[0:i]
   
   # remove comments
   if (gc.find(';') != -1):
      gc = gc[:gc.find(';')]

   if (gc == 'G1'):
      # check if Z has changed, check if it is a zhop movement
      newz = getValue(l, 'Z', -1)
      if (newz != -1 and newz - zpos < zhop - 0.01 and newz != zpos):
         if (zpos == 0):
            zpos = newz
         else:
            # new layer here
            #ouf.write('TNEW '+str(zpos)+' '+str(newz)+'\n')
            for i in list(range(maxSwaps-swaps)):
               drawNextTower()
               #for l in towers[i]:
                  #ouf.write(';asd\n')
            zpos = newz
            swaps = 0
   elif (gc[0:1] == 'T'):
      tn = int(gc[1:])
      if (ltn == -1):
         ltn = tn
      elif (tn != ltn):
         # swap here
         ltn = tn
         drawNextTower()
         #print('swap', swaps, l)

#for l in lines:
#   break
#   i = l.find(' ')
#   if (i == -1):
#      gc = l
#   else:
#      gc = l[0:i]
#
#   if (gc.find(';') != -1):
#      gc = gc[:gc.find(';')]

   #if (gc[0:1] == 'T' and gc[1:] not in tnList):
      #tnList[gc] = False



