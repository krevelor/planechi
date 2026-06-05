# visualizer 1.0
# draws exclusion shadows for shapes
# by eden carrier
#
# for now, just ripping relevant code from exclusion ring
# eventually will be packagified
#


import numpy as np
import png        # pip install pypng, for some reason
import random as rand
import math

gridsize = 5
colornum = 7
iters = 500 #here for show lol
radsqrs = 65 #must be greater than root 2 or get a divide by zero

# dimensions of the grid in terms of coordinates for conversion from
# path to grid coords
xdims = (-10, 10)
ydims = (-10, 10)

inputname = "hexagrid.png"
outputname = "hexaslice.png"

#####################################3

def makerandgrid( dim, colorcount ):
    grid = np.zeros(shape=(dim,dim))
    for i in range(dim):
        for j in range(dim):
            grid[i][j] = rand.randint(1,colorcount)
    return grid

def colorid( codex, rgb ):
    for i in range(len(codex)):
        if (codex[i][0] == rgb[0] and
                codex[i][1] == rgb[1] and
                codex[i][2] == rgb[2]):
            return i
    return -1


######################################


def dist( x1, y1, x2, y2 ):
    return ((x1-x2)**2 + (y1-y2)**2)**0.5

# helper for wrapparound coordinates
# only intended for screen wrapping, doesnt work for more extreme inputs
def cowrap( x, dim ):
    if x < 0:
        x += dim
    if x >= dim:
        x -= dim
    return x

def check_pair( x1, y1, x2, y2, squarelen ):
    testdist = dist(x1,y1,x2,y2) * squarelen
    if abs(testdist - 1) > 2*squarelen:     #cull condition
        return False
    maxd = 0
    mind = 2
    for i in range(2):
        for j in range(2):
            for k in range(2):
                for l in range(2):
                    cornerdist = dist( x1+i, y1+j, x2+k, y2+l ) * squarelen
                    if cornerdist < mind:
                        mind = cornerdist
                    if cornerdist > maxd:
                        maxd = cornerdist
    if maxd > 1 and mind < 1:
        return True
    return False


def makeexclusion( dim, radsqrs ):
    #dim = 100
    grid = np.zeros(shape=(dim,dim))

    #radsqrs = 16
    squarelen = 1/radsqrs


    exclusionring = []

    #test center
    cx = dim//2
    cy = dim//2
    grid[cx][cy] = 5

    #measuring from top left so only need to go one further on upper and right sides
    for i in range( cx - radsqrs - 3, cx + radsqrs + 2 ):
        for j in range( cy - radsqrs - 3, cy + radsqrs + 2 ):
            if check_pair( cx, cy, i, j, squarelen ):
                x = cowrap( i, dim )
                y = cowrap( j, dim )
                exclusionring.append( (x,y) )
                grid[x][y] = 1
    
    # for particular application, need entries sorted by angle
    exclusionring = sortexclusion( exclusionring, (cx, cy) )

    #generecize ring to get placable filter
    for i in range(len(exclusionring)):
        x = exclusionring[i][0] - cx
        y = exclusionring[i][1] - cy
        exclusionring[i] = (x,y)
    
    return exclusionring

def makering( excfilter, offset, dim ):
    ring = []
    for i in range(len(excfilter)):
        x = cowrap( excfilter[i][0] + offset[0], dim )
        y = cowrap( excfilter[i][1] + offset[1], dim )
        ring.append( (x,y) )
    return ring



################################

def x( t ):
    return 7 * np.sin(t)

def y( t ):
    return 7 * np.cos(t)

# where you define the 1d path to use as an axis. returns x(t) and y(t)
def parameterized( tmin, tmax, step ):
    xs = []
    ys = []
    t = tmin
    while t <= tmax:
        xs.append( x(t) )
        ys.append( y(t) )
        t += step
    return xs, ys



def convert( val, factor, lowbound ):
    return math.floor( ( val - lowbound ) / factor )

def converttocoords( xs, ys, grid ):
    gx = len(grid)
    gy = len(grid[0])
    xfac = ( xdims[1] - xdims[0] ) / gx
    yfac = ( ydims[1] - ydims[0] ) / gy
    lastcoord = (-1,-1)
    coords = []
    for i in range(len(xs)):
        coord = ( convert( xs[i], xfac, xdims[0] ), convert( ys[i], yfac, ydims[0] ) )
        #print(coord)
        if lastcoord == coord:
            continue
        coords.append( coord )
        lastcoord = coord
    return coords

def makeparamed( grid ):
    (xs, ys) = parameterized( 0, 6.2, 0.1 )
    return converttocoords( xs, ys, grid )

# angle goes quad ii to i
# arcsin( delta y / dist )
# conversions are for nerds
def angle( center, val ):
    val = ( val[0] + 0.5, val[1] + 0.5 )
    center = ( center[0] + 0.5, center[1] + 0.5 )
    #print( center )
    #print( val )
    #print( ( ( val[1] - center[1] ) / dist( center[0], center[1], val[0], val[1] ) ))
    return np.arcsin( ( ( val[1] - center[1] ) / dist( center[0], center[1], val[0], val[1] ) ) )

# sorts elements of exclusion
# bucket sort into large number of bins based on angle from -pi to pi
# mapped to (0, 20pi)
# each bin will only have a couple dozen, so select sort the rest for stack simplicity
# fucking python
# pieces are passed around as ( angle, (x,y) ) pairs
def sortexclusion( exclusion, center ):
    cells = []
    for i in range(len(exclusion)):
        cells.append( ( angle( center, exclusion[i] ) + math.pi, exclusion[i] ) )

    # buckets
    buckets = np.zeros((63,0)).tolist()     # 2pi, buckets every pi/10
    for i in range(len(cells)):
        buckets[ math.floor( 10 * cells[i][0] ) ].append( cells[i] )
    # selections
    sort = []
    for b in range(len(buckets)):
        while len(buckets[b]) > 0:
            mintheta = 100
            mini = 0
            for i in range(len(buckets[b])):
                if mintheta > buckets[b][i][0]:
                    mintheta = buckets[b][i][0]
                    print(mintheta)
                    mini = i
            obj = buckets[b].pop(mini)
            #print( obj[0] )
            print()
            #sort.append( ( buckets[b].pop(i) )[1] )
            sort.append( obj[1] )
    return sort
                
#################################

# if gridsize > 0, tile inname to specified dims
# if it's zero, just load inname's dims
# assumed inname is square
def loadgrid( dim, inname ):
    global colornum, gridsize
    reader = png.Reader(filename = inname)
    w, h, pix, meta = reader.asRGB8()
    pix = list(pix)

    grid = []
    if dim > 0:
        grid = np.zeros(shape=(dim,dim))
    else:
        grid = np.zeros(shape=(w,h))
        dim = w

    # dummy entry to fix offsets
    codex = [[-1,-1,-1]]
    # fill in grid with color at [i,j] mod image dims if needed
    # construct codex for numbering as new colors encountered
    for i in range(dim):
        offset = 0
        for j in range(dim):
            #print(offset)
            r,g,b = pix[i%h][offset:offset+3]
            rgb = [r,g,b]
            #print(rgb)
            c = colorid(codex, rgb)
            if c == -1:
                c = len(codex)
                codex.append(rgb)
            grid[i][j] = c
            offset = (offset+3) % ( w * 3 )
            #offset += 3

    # adjust parameters as appropriate
    if len(codex) > colornum:
        colornum = len(codex)
    gridsize = dim
    
    return grid

def colorid( codex, rgb ):
    for i in range(len(codex)):
        if (codex[i][0] == rgb[0] and
                codex[i][1] == rgb[1] and
                codex[i][2] == rgb[2]):
            return i
    return -1


# codex to visually show number of collisions from gree (0) to red (>64%)
def badnesscodex():
    codex = []
    for i in range(64):
        codex.append( ( 4*i, 255 - 4*i, 0 ) )
    codex.append( (255,0,0) )
    return codex

#####################################################
#change codex to match order of hexagon colors when actually using
#####################################################
# png helper which specifies an eight color codex for convenience
def defaultcodex():
    codex = []
    codex.append( (255,255,255) )
    codex.append( (255,255,0) )
    codex.append( (0,255,0) )
    codex.append( (255,0,255) )
    codex.append( (0,255,255) )
    codex.append( (255,0,0) )
    codex.append( (0,0,255) )
    codex.append( (0,0,0) )
    #print(codex[1])
    return codex

# to make this more flexible, specifies a list of colors for the first
# len(codex) values. further values will be set to val % len,
# but are not really intended
# if codex is None, then will use default codex from above
def printimg( grid, filename, colorcodex ):
    if colorcodex == None:
        colorcodex = defaultcodex()
    height = len(grid)
    width = len(grid[0])
    img = []
    for y in range(height):
        row = ()
        for x in range(width):
            row = row + colorcodex[ int(grid[y][x] % len(colorcodex)) ]
        img.append(row)
    with open( filename, 'wb' ) as f:
        w = png.Writer( width, height, greyscale=False )
        w.write(f, img)

def makepathplot( path, grid, exfilter ):
    plot = []
    #print(len(path))
    #print(len(excring))
    for i in range(len(path)):
        #print()
        #print(path[i])
        plot.append([])
        excring = makering( exfilter, path[i], len(grid) )
        for j in range(len(excring)):
            #if i == 25:
            #    print(excring[j])
            plot[i].append( grid[excring[j][0]][excring[j][1]] )
    return plot

# take in already colored grid
# decide on a path through it as one axis
# for the other, uncurl exclusion ring and make it an axis
def main():
    grid = loadgrid( 0, inputname )
    #for i in range(len(grid)):
    #    for j in range(len(grid[0])):
    #        print(grid[i][j])
    path = makeparamed( grid )
    excring = makeexclusion( len(grid), radsqrs )
    #need to make img grid
    pathplot = makepathplot( path, grid, excring )
    #print()
    #for i in range(len(pathplot)):
    #    print(pathplot[i][0])
    printimg( pathplot, outputname, None )

main()
