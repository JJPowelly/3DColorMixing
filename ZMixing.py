
import re
import sys
import getopt
from os import walk

absolute = -1

infile = 'ZMixingIn.gcode'

outfile = 'ZMixingOut.gcode'

colorfile = 'color-codes.txt'

maxZ = float(-1.0)

zhop = float(1.0) # needed to properly detect layer changes

zpos = float(0.0)

#lastz = float(-1.0)

numColors = -1 # -1 to use all colors from the color code file

numExtruders = 16 # number of virtual extruders our printer can handle

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
cof = open(colorfile, 'r')
ouf = open(outfile, 'w')

lines = inf.readlines()
colors = cof.readlines()

# change the mixing ratios of the virtual extruders to colors defined in the color-codes file
def setColors(start, length):
    s = 0
    i = 0
    for l in colors[start:start+length]:
        for c in l:
            if c != '\n':
                ouf.write('M163 S'+str(s)+' P'+c+'\n')
                #print('M163 S'+str(s)+' P'+c)
                s += 1
        s = 0
        ouf.write('M164 S'+str(i)+'\n\n')
        #print('M164 S'+str(i)+'\n')
        i += 1


#setColors(32,16)
#sys.exit()

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

# iterate through lines from last to firstG92
for x in reversed(range(len(lines))):
   l = lines[x]
   i = l.find(' ')
   if (i == -1):
      gc = l
   else:
      gc = l[0:i]
   
   # remove comments
   if (gc.find(';') != -1):
      gc = gc[:gc.find(';')]

   if (gc == 'G1'):
      # if we got a Z, its the last z, so its the max
      maxZ = getValue(l, 'Z', -1)
      if (maxZ != -1):
         break

if numColors == -1:
    numSwaps = len(colors)
else:
    numColors = numExtruders

swapHeight = maxZ / numSwaps
nextSwap = swapHeight
print(maxZ)
print(swapHeight)
print(numSwaps)

numResets = 0
ct = 0 # current T
firstG92 = True
firstG28 = True
#ouf.write('T'+str(ct)+'\n')
for l in lines:
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
      #print(newz)
      if (newz != -1 and newz - zpos < zhop - 0.01 and newz != zpos):
         if (zpos == 0):
            zpos = newz
         elif (zpos > 0):
            zpos = newz
            # new layer here
            if (zpos >= nextSwap):
               nextSwap += swapHeight
               #print(nextSwap)
               if ct == -1:
                  numResets += 1
                  setColors(numExtruders*numResets, numExtruders)        
               ct += 1
               ouf.write('T'+str(ct)+'\n')
               if ct >= numExtruders-1:
                  ct = -1

   # print firstG92 Tn after first G92
   ouf.write(l)
   if (gc == 'G92' and firstG92):
      firstG92 = False
      ouf.write('T0\n')
   if (gc == 'G28' and firstG28):
      firstG28 = False
      setColors(numExtruders*numResets, numExtruders)        
