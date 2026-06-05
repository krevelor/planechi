

import numpy as np
import png        # pip install pypng, for some reason
import random as rand



# sim params
gridsize = 200
colornum = 13
iters = 5
radsqrs = 80


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


# function to check if two pixels overlap
# checks all sixteen pairs of corners
# if there exists a pair whose distance is >= 1 and
# one whose distance is <=1, then the two collide
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

# function to construct a list of offsets constituting the
# "exculsion ring" for the given parameters
# this list of offsets can then be used with any particular
# pixel to find all pixels it collides with
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

    #generecize ring to get placable filter
    for i in range(len(exclusionring)):
        x = exclusionring[i][0] - cx
        y = exclusionring[i][1] - cy
        exclusionring[i] = (x,y)

    return exclusionring

# takes a list of offsets and applies them to a specific pixel
def makering( excfilter, offset, dim ):
    ring = []
    for i in range(len(excfilter)):
        x = cowrap( excfilter[i][0] + offset[0], dim )
        y = cowrap( excfilter[i][1] + offset[1], dim )
        ring.append( (x,y) )
    return ring

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
            row = row + colorcodex[ int(grid[y,x] % len(colorcodex)) ]
        img.append(row)
    with open( filename, 'wb' ) as f:
        w = png.Writer( width, height, greyscale=False )
        w.write(f, img)

def main(dim):
    grid = np.zeros((dim,dim))
    grid[dim//2][dim//2] = 1
    adjs = []
    adjs.append( (dim//2,dim//2 - 1) )
    adjs.append( (dim//2,dim//2 + 1) )
    adjs.append( (dim//2 - 1,dim//2) )
    adjs.append( (dim//2 + 1,dim//2) )
    excfilter = makeexclusion( dim, radsqrs )
    while len(adjs) > 0:
        i = rand.randint(0,len(adjs)-1)
        coords = adjs.pop(i)
        if grid[coords[0]][coords[1]] != 0:
            continue
        grid[coords[0]][coords[1]] = 1
        excring = makering( excfilter, coords, dim )
        for j in range(len(excring)):
            grid[excring[j][0]][excring[j][1]] = 2
        adjs.append( ( coords[0] - 1, coords[1] ) )
        adjs.append( ( coords[0] + 1, coords[1] ) )
        adjs.append( ( coords[0], coords[1] + 1 ) )
        adjs.append( ( coords[0], coords[1] - 1 ) )

    printimg( grid, "chunk.png", None )
    chunkcount = 0
    shadowcount = 0
    for i in range(len(grid)):
        for j in range(len(grid)):
            val = grid[i][j]
            if val == 1:
                chunkcount += 1
            elif val == 2:
                shadowcount += 1

    print(str(chunkcount/shadowcount))

for i in range(40):
    print(i)
    main(gridsize)
    radsqrs += 1
