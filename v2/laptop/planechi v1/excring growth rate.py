import numpy as np
import matplotlib.pyplot as plt


def dist( x1, y1, x2, y2 ):
    return ((x1-x2)**2 + (y1-y2)**2)**0.5

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

    radsqrs = int(radsqrs+1)
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

# helper for wrapparound coordinates
# only intended for screen wrapping, doesnt work for more extreme inputs
def cowrap( x, dim ):
    if x < 0:
        x += dim
    if x >= dim:
        x -= dim
    return x

dim = 13
step = 0.01
rad = 10
rads = []
lens = []
while rad < dim:
    rads.append( rad )
    lens.append( len( makeexclusion( dim, rad ) ) )
    rad += step


plt.plot( rads, lens )
plt.show()

#large spikes at each integer
#much smaller spikes  right afterwards, likely do to the quadratic expansions
# go from say 3 to 2.9, not 3.1
