# Jake Mayeux
# July 2017
# reorder.py

import re
import sys
import getopt

infile = 'gtester2.gcode'
outfile = 'out.gcode'

zhop = float(1.0) # needed to properly detect layer changes
zpos = float(0.0)
tn = -1

# used for storing GCode for each layer labeled by Tn's
data = {}

# disable the serpentining
noserp = False

# ascend or descend the order of Tn's
colorDir = True

# cli args
opts, extraparams = getopt.getopt(
   sys.argv[1:],
   'z:f:o:s',
   ['zhop', 'infile', 'outfile'])
for o, p in opts:
   if o in ['-z', '--zhop']:
      zhop = p
   elif o in ['-f', '--infile']:
      infile = p
   elif o in ['-o', '--outfile']:
      outfile = p
   elif o in ['-s', '--noserpentine']
      noserp = True


inf = open(infile, 'r')
ouf = open(outfile, 'w')
lines = inf.readlines()

# copied from mixing.py
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

# is called after each layer to sort and write GCode to the out file
def flushAndSort():
   global colorDir
   global data

   if not noserp
      colorDir = not colorDir
   # sort
   keys = sorted(data.keys())
   # reverse every other layer
   if(colorDir):
      keys = reversed(keys)

   # write
   for i in keys:
      for x in data[i]:
         ouf.write(x)

   # clear for next layer
   data = {}

for l in lines:
   # parse the GCode
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
            flushAndSort()
            zpos = getValue(l, 'Z', zpos)
            # write the line that moves it up to the next layer
            ouf.write(l)
            continue
   elif (gc[0:1] == 'T'):
      # keep track of which Tn we're on
      tn = int(gc[1:])
   
   # if we haven't established a Tn yet, dont sort just write
   if (tn == -1):
      ouf.write(l)
   else:
      # allocate 2nd array for GCode if needed
      if (not tn in data):
         data[tn] = []
         data[tn].append('T'+str(tn)+'\n')
      # store GCode in the array correlating to the current Tn
      if(gc[0:1] != 'T'):
         data[tn].append(l)

# write the last layer
flushAndSort()
