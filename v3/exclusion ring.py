##########################
# program for investigation of the hadwiger-nelson problem
# by eden carrier, 2026
#
# v 2.0
#
# 1.0 - original able to generate improved grids
# 1.1 - added diagnostics and tweaked improvement function
# 1.2 - fixed issue with excring generation for rsq/gsz > 0.5
#       setup diagnostics to pipe to file
#       added ability to run multiple trials in one session
# 1.3 - smoothness criterion
#
##########################
#
# 2.0 - reunified versions and cleaned up layout
#       implemented read from file
#
##########################
#
# 3.0 - yeahhhh babey its 3ddddddddddd XDDDDD
#
#


import numpy as np
import png        # pip install pypng, for some reason
import random as rand
import matplotlib.pyplot as plt

# program params
trials = 1              # number of full runs to perform
TRUERANDCHNG = False    # picks new colors fully at random rather than based on what colors are in its ring
PRINTTOFILE = True      # toggle for printing diagnostics to a file or command line
SMOOTHCRIT = False       # enables smoothness criterion. see smoothness() for details
NEWINPUT = True        # toggle for using a generated grid vs an inputed one
DIAGNOSTICS = False
GRAPHS = True

# sim params
gridsize = 30
colornum = 14
iters = 4000
radsqrs = 10

clumping = 2


# in order:
# inital layout and density map
# final layout and density map
# best layout and density map
# sample exclusion ring
# diagnostics text dump
# et al as needed
filenames = [ 'before.png', 'predensity.png', 'after.png', 'postdensity.png', 'best.png', 'bestdensity.png', 'ring.png', 'output.txt' ]
# input file if set input
inputname = 'input.png'

###############################
###
###     Helper Functions
###
###############################



# creates a random starting grid with the specified parameters
# used whenever a preexisting input is not supplied (NEWINPUT = True)
def makerandgrid( dim, colorcount ):
    if dim % clumping != 0:
        print( "invalid clumping" )
        exit()
    grid = np.zeros(shape=(dim,dim,dim))
    for i in range(0,dim,clumping):
        for j in range(0,dim,clumping):
            for k in range(0,dim,clumping):
                color = rand.randint(1,colorcount)
                for a in range(clumping):
                    for b in range(clumping):
                        for c in range(clumping):
                            grid[i+a][j+b][k+c] = color
    return grid

def dist( x1, y1, z1, x2, y2, z2 ):
    return ((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)**0.5

# helper for wrapparound coordinates
# only intended for screen wrapping, doesnt work for more extreme inputs
def cowrap( x, dim ):
    if x < 0:
        x += dim
    if x >= dim:
        x -= dim
    return x

######################################################################################################################################
def colorid( codex, rgb ):
    for i in range(len(codex)):
        if (codex[i][0] == rgb[0] and
                codex[i][1] == rgb[1] and
                codex[i][2] == rgb[2]):
            return i
    return -1


###############################
###
###     Graphical I/O
###
###############################


# codex to visually show number of collisions from green (0) to red (>32%)
def badnesscodex():
    codex = []
    for i in range(32):
        codex.append( ( 8*i, 255 - 8*i, 0 ) )
    codex.append( (255,0,0) )
    return codex

# png helper which specifies a sixteen color codex for convenience
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
    codex.append( (128,128,128) )
    codex.append( (255,0,192) )
    codex.append( (255,128,0) )
    codex.append( (0,192,128) )
    codex.append( (192,0,0) )
    codex.append( (0,192,0) )
    codex.append( (0,0,192) )
    codex.append( (192,192,192) )
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


def printimg3d( grid, filename, colorcodex ):
    if colorcodex == None:
        colorcodex = defaultcodex()
    depth = len(grid)
    for i in range(depth):
        pieces = filename.split('.')
        number = "0000" + str(i)
        number = number[-4:]
        name = pieces[0] + number + "." + pieces[1]
        printimg( grid[i], name, colorcodex )

# uses badnesscodex to create a map of which pixels have more or less collisions
def printfrqimg( grid, filename, maxamount ):
    codex = badnesscodex()
    height = len(grid)
    width = len(grid[0])
    img = []
    for y in range(height):
        row = ()
        for x in range(width):
            row = row + codex[ min( 32, int( 200 * grid[y,x] / maxamount ) ) ]
        img.append(row)
    with open( filename, 'wb' ) as f:
        w = png.Writer( width, height, greyscale=False )
        w.write(f, img)


def printfrq3d( grid, filename, maxamount ):
    depth = len(grid)
    for i in range(depth):
        pieces = filename.split('.')
        number = "0000" + str(i)
        number = number[-4:]
        name = pieces[0] + number + "." + pieces[1]
        printfrqimg( grid[i], name, maxamount )

######################################################################################################################################
# utility to load a starting grid from a source image, usually a previous output
# if gridsize > 0, tile inname to specified dims
# if it's zero, just load inname's dims
# assumed inname is square
def loadgrid( dim, inname ):
    global colornum, gridsize
    reader = png.Reader(filename = inname)
    w, h, pix, meta = reader.asRGBA8()
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
            r,g,b = pix[i%h][offset:offset+3]
            rgb = [r,g,b]
            c = colorid(codex, rgb)
            if c == -1:
                c = len(codex)
                codex.append(rgb)
            grid[i][j] = c
            offset = (offset+4) % (4*w)

    # adjust parameters as appropriate
    if len(codex) > colornum + 1:
        colornum = len(codex)
    gridsize = dim
    
    return grid






###############################
###
###     Text I/O
###
###############################


# prints all diagnostics to a file when PRINTTOFILE is set
def dumptext( text, filename ):
    with open( filename, 'w' ) as f:
        f.write( text )

# arranges stats into an output string   
def printcolstats( stats, maxcol ):
    printstr = "average number of collisions: "
    printstr += str(stats[0])
    printstr += " ("
    printstr += str(stats[0] / maxcol)
    printstr += ")\nsmallest count: "
    printstr += str(stats[1])
    printstr += "\nlargest count: "
    printstr += str(stats[2])
    return printstr

# handles text output, either to a file or command line
def printdiagnostics( diagnostics, maxcol, filename ):
    printstr = ""
    for i in range(len(diagnostics)):
        printstr += "generation "
        printstr += str(diagnostics[i][0])
        printstr += "\n\n"
        printstr += printcolstats( diagnostics[i][1], maxcol )
        printstr += "\n\n"
    if PRINTTOFILE:
        dumptext( printstr, filename )
    else:
        print(printstr)
        

###############################
###
###     Processing
###
###############################


# function to check if two pixels overlap
# checks all sixteen pairs of corners # EDIT 64!!!!!!
# if there exists a pair whose distance is >= 1 and
# one whose distance is <=1, then the two collide
def check_pair( x1, y1, z1, x2, y2, z2, squarelen ):
    testdist = dist(x1,y1,z1,x2,y2,z2) * squarelen
    if abs(testdist - 1) > 2*squarelen:     #cull condition
        return False
    maxd = 0
    mind = 2
    for i in range(2):
        for j in range(2):
            for k in range(2):
                for l in range(2):
                    for m in range(2):
                        for n in range(2):
                            cornerdist = dist( x1+i, y1+j, z1+k, x2+l, y2+m, z2+n ) * squarelen
                            if cornerdist < mind:
                                mind = cornerdist
                            if cornerdist > maxd:
                                maxd = cornerdist
    if maxd > 1 and mind < 1:
        return True
    return False


# function to construct a list of offsets constituting the
# "exclusion ring" for the given parameters
# this list of offsets can then be used with any particular
# pixel to find all pixels it collides with
def makeexclusion( dim, radsqrs, filename ):
    #dim = 100
    grid = np.zeros(shape=(dim,dim,dim))

    #radsqrs = 16
    squarelen = 1/radsqrs


    exclusionring = []

    #test center
    cx = dim//2
    cy = dim//2
    cz = dim//2
    grid[cx][cy][cz] = 3

    #measuring from top left so only need to go one further on upper and right sides
    for i in range( cx - radsqrs - 3, cx + radsqrs + 2 ):
        for j in range( cy - radsqrs - 3, cy + radsqrs + 2 ):
            for k in range( cz - radsqrs - 3, cz + radsqrs + 2 ):
                if check_pair( cx, cy, cz, i, j, k, squarelen ):
                    x = cowrap( i, dim )
                    y = cowrap( j, dim )
                    z = cowrap( k, dim )
                    exclusionring.append( (x,y,z) )
                    grid[x][y][z] = 1
    
    for i in range(dim):
        grid[i][cy][cz] += 2
        
    printimg3d( grid, filename, None )
    
    #generecize ring to get placable filter
    for i in range(len(exclusionring)):
        x = exclusionring[i][0] - cx
        y = exclusionring[i][1] - cy
        z = exclusionring[i][2] - cz
        exclusionring[i] = (x,y,z)

    return exclusionring


# takes a list of offsets and applies them to a specific pixel
def makering( excfilter, offset, dim ):
    ring = []
    for i in range(len(excfilter)):
        x = cowrap( excfilter[i][0] + offset[0], dim )
        y = cowrap( excfilter[i][1] + offset[1], dim )
        z = cowrap( excfilter[i][2] + offset[2], dim )
        ring.append( (x,y,z) )
    return ring

# calls makering on every point and stores them for later
def makerings( excfilter, dim ):
    rings = []
    for i in range(dim):
        rings.append([])
        for j in range(dim):
            rings[i].append([])
            for k in range(dim):
                rings[i][j].append( makering( excfilter, (i,j,k), dim ) )
    return rings

# makes another grid with entries counting number of collisions given specified exclusion
# used to determine how likely each entry is to change color
def countcollisions( grid, excrings, baddata ):
    dim = len(grid)
    colgrid = np.zeros(shape=(dim,dim,dim))

    badcount = 0
    
    for x in range(dim):
        for y in range(dim):
            for z in range(dim):
                excring = excrings[x][y][z]
                val = grid[x][y][z]
                count = 0

                for i in range(len(excring)):
                    v2 = grid[ excring[i][0] ][ excring[i][1] ][ excring[i][2] ]
                    if val == v2:
                        count += 1
                colgrid[x][y][z] = count
                badcount += count

    if baddata != None:
        baddata.append( badcount / dim**3 / len(excring) )
        
    return colgrid


# the core of the logical loop
# at each iteration, each pixel computes how many other pixels 1 unit away match it
# then it probabilistically changes color
# the more collisions it has, the more likely it is to change
# if it does change, it makes a weighted choice based on other colors in its ring
def changecolor( grid, excring, x, y, z, colornum ):
    
    # if smoothness criterion is enabled, shortcut rest when triggered
    if SMOOTHCRIT and smoothness( grid, x, y, z ):
        return grid[x][cowrap(y+1,len(grid))][z]
    
    if TRUERANDCHNG:
        offset = rand.randint(1, colornum - 1)
        color = grid[x][y][z]
        grid[x][y][z] = ( color + offset ) % colornum
        return

    # weight each number inverse its frequency in the ring
    counts = np.zeros(colornum)
    for i in range(len(excring)):
        color = grid[ excring[i][0] ][ excring[i][1] ][ excring[i][2] ]
        counts[ int(color - 1) ] += 1
        
    total = 0
    for i in range(colornum):
        total += counts[i]
        
    totalprob = 0
    for i in range(colornum):
        if i == grid[x][y][z] - 1:
            continue
        if counts[i] != 0:
            counts[i] = total / counts[i]
            totalprob += counts[i]
        # if a color does not appear in the exclusion ring, shortcut and change to it
        else:
            return i+1
        
    # pick a random number in a weighted range and then pick the one whose segment that is
    r = rand.random() * totalprob
    for i in range(colornum):
        if i == grid[x][y][z] - 1:
            continue
        if r < counts[i]:
            return i+1
        else:
            r -= counts[i]

    print( "uh oh" )


# uses changecolor to determine what each pixel does at next time step
# once all are determined, all changes are made at once
def changegrid( grid, colgrid, excrings, colornum, tempdata ):
    dim = len(grid)
    newgrid = np.zeros(shape=(dim,dim,dim))
    temps = 0
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                # decide probabalistically whether to change space color
                ratio = colgrid[i][j][k] / len(excrings[i][j][k]) 
                r = rand.random()
                temp = 3 * colornum**2 * ratio**3
                temps += temp
                if r < temp:
                    newgrid[i][j][k] = changecolor( grid, excrings[i][j][k], i, j, k, colornum )
                else:
                    newgrid[i][j][k] = grid[i][j][k]
    #print( str( temps / dim**3 ) )
    if tempdata != None:
        tempdata.append( temps / dim**3 )
    # apply grid all at once
    return newgrid


# utility to measure how well the grid is doing at minimizing collisions
def collisionstats( colgrid ):
    dim = len(colgrid)
    total = 0
    maxi = 0
    mini = 10**8
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                val = colgrid[i][j][k]
                total += val
                if val < mini:
                    mini = val
                if val > maxi:
                    maxi = val
    average = total / dim**2
    return ( average, mini, maxi )

######################################################################################################################################
# the smoothness criterion; enabled by setting SMOOTHCRIT
# since a region has the same exclusion shadow whether the interior of that region is filled in or not
# there is no reason *not* to fill it in
# as such this criterion acts as a small optimization
# if all four adjacent pixels are the same color as each other,
# the pixel in the middle is automatically set to that color
# this bypasses the normal, much more time consuming execution of changecolor
def smoothness( grid, x, y, z ):
    dim = len(grid)
    xp = cowrap( x+1, dim )
    xm = cowrap( x-1, dim )
    yp = cowrap( y+1, dim )
    ym = cowrap( y-1, dim )
    return (grid[xp][y] == grid[xm][y] and
            grid[xp][y] == grid[x][yp] and
            grid[x][yp] == grid[x][ym])



###############################
###
###     Main
###
###############################



def main():
    # some parameters defined at top of file for convenience
    # in particular see top of file for file name references

    # init grid
    if NEWINPUT:
        grid = makerandgrid( gridsize, colornum )
    else:
        grid = loadgrid( gridsize, inputname )

    tempdata, baddata = None, None
    if GRAPHS:
        tempdata = []
        baddata = []

    printimg3d( grid, filenames[0], None )
    excfilter = makeexclusion( gridsize, radsqrs, filenames[6] )
    excrings = makerings( excfilter, gridsize )
    colgrid = countcollisions( grid, excrings, baddata )
    printfrq3d( colgrid, filenames[1], len(excfilter) )

    #for i in range(len(colgrid)):
    #    print(colgrid[i])
    diagnostics = [ (0, collisionstats( colgrid )) ]
    best = 10**8
    lasti = 0
    bestgrid = []
    percent = iters // 100
    percenter = iters // 1000
    for i in range(iters):
        if iters > 2000 and i%percenter == 0:
            print( str(i/percenter/10) + "% done" )
        elif iters > 200 and i%percent == 0:
            print( str(i/percent) + "% done" )
        grid = changegrid( grid, colgrid, excrings, colornum, tempdata )
        colgrid = countcollisions( grid, excrings, baddata )
        if DIAGNOSTICS:
            # collect diagnostics
            if i - lasti > 9:
                stats = collisionstats( colgrid )
                if stats[0] < best:
                    lasti = i
                    best = stats[0]
                    diagnostics.append( (i, stats) )

    # final output
    printimg3d( grid, filenames[2], None )
    printfrq3d( colgrid, filenames[3], len(excfilter) )
    if DIAGNOSTICS:
        printdiagnostics( diagnostics, len(excfilter), filenames[7] )
    if GRAPHS:
        # all graphs intentionally have their first entries removed
        # to better frame the data, rather than accomidating transients
        xs = []
        for i in range(len(tempdata)):
            xs.append(i)
        change = []
        for i in range(1,len(tempdata)):
            change.append( 100 * ( tempdata[i] - tempdata[i-1] ) / tempdata[i-1] )
        fig, axs = plt.subplots(2,2)
        axs[0,0].plot( xs[3:], tempdata[3:] )
        axs[0,1].plot( tempdata[3:], baddata[3:-1] )
        axs[1,0].plot( xs[3:], baddata[3:-1] )
        axs[1,1].plot( xs[4:], change[3:] )
        axs[0,0].set_title("temp over time")
        axs[0,1].set_title("temp v badness")
        axs[1,0].set_title("badness over time")
        axs[1,1].set_title("temp percent change")
        fig.savefig("graphs.png")
        plt.show()

print( "gsz " + str(gridsize)
       + " cn " + str(colornum)
       + " n " + str(iters)
       + " rsq " + str(radsqrs)
       + " x" + str(trials) )


# if multiple trials are specified, the whole of main is run repeatedly
# possibly with different parameters
if trials == 1:
    main()
elif trials < 1:
    print( "invalid number of trials, must be >= 1" )
else:
    originalnames = filenames
    for i in range(trials):
        print( "trial " + str(i+1) )
        # modify filenames to be distinct so they dont get overwritten
        filenames = []
        for j in range(len(originalnames)):
            filenames.append( "trial " + str(i+1) + " - " + originalnames[j] )
        main()
        radsqrs += 20
        
