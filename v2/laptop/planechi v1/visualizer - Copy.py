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

#####################################3

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
            r,g,b = pixels[i%h][offset:offset+3]
            rgb = [r,g,b]
            c = colorid(codex, rgb)
            if c == -1:
                c = len(codex)
                codex.append(rgb)
            grid[i][j] = c
            offset = (offset+3) % w

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

# precon - grid is all 1's for shape or 0's for blank
# postcon - newgrid is same, but 2 is shadow and 3 is Bad
def applyshadow( grid, excfilter ):
    dim = len(grid)
    newgrid = np.zeros(shape=(dim,dim))
    for i in range(dim):
        for j in range(dim):
            if grid[i][j] == 1:
                excring = makering( excfilter, (i,j), dim )
                for k in len(excring):
                    newgrid[excring[k][0]][excring[k][1]] = 2
    for i in range(dim):
        for j in range(dim):
            newgrid[i][j] += grid[i][j]
    return newgrid

def main():
    # init grid
    grid = loadgrid( gridsize, inputname )
    #printimg( grid, filenames[0], None )
    excfilter = makeexclusion( gridsize, radsqrs )
    #colgrid = countcollisions( grid, excfilter )
    #printfrqimg( colgrid, filenames[1], len(excfilter) )
    newgrid = applyshadow( grid, excfilter )
