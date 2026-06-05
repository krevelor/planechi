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

gridsize = 5
colornum = 7
iters = 500 #here for show lol
radsqrs = 1

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

# compilation to cnf

#matrix = [[ 0, 1, 1, 0, 0, 0, 1 ],
#             [ 1, 0, 1, 1, 0, 0, 0 ],
#             [ 1, 1, 0, 1, 0, 0, 0 ],
#             [ 0, 1, 1, 0, 1, 1, 0 ],
#             [ 0, 0, 0, 1, 0, 1, 1 ],
#             [ 0, 0, 0, 1, 1, 0, 1 ],
#             [ 1, 0, 0, 0, 1, 1, 0 ]]
#colors = 4

#vertices = len(matrix)
lookup = []

def makelookup( vs, cs ):
    global lookup
    lookup = []
    index = 1
    for i in range(vs):
        lookup.append([])
        for j in range(cs):
            lookup[i].append( str(index) )
            index += 1

def iscolored( vs, cs ):
    lines = []
    for i in range(vs):
        line = ""
        for j in range(cs):
            line += lookup[i][j] + " "
        line += "0"
        lines.append(line)
    return lines

def singlecolor( vs, cs ):
    lines = []
    for i in range(vs):
        for j in range(cs):
            for k in range(j+1, cs):
                line = "-"
                line += lookup[i][j]
                line += " -"
                line += lookup[i][k]
                line += " 0"
                lines.append(line)
    return lines

# precon theres an edge from v0 to v1
def edgerule( v0, v1, cs ):
    name = "c edge " + str(v0) + "-" + str(v1)
    lines = [name]
    for i in range(cs):
        line = "-"
        line += lookup[v0][i]
        line += " -"
        line += lookup[v1][i]
        line += " 0"
        lines.append(line)
    return lines

def alledgerules( mat, cs ):
    edgecount = 0
    lines = ["c edges"]
    for i in range(len(mat)):
        for j in range( i+1, len(mat[i]) ):
            if mat[i][j] == 1:
                edgecount += 1
                lines.extend( edgerule( i, j, cs ) )
    return lines, edgecount

def cumpile( mat, vs, cs ):
    makelookup( vs, cs )
    crules1 = iscolored( vs, cs )
    crules2 = singlecolor( vs, cs )
    erules, es = alledgerules( mat, cs )
    clauses = vs + vs * cs * (cs - 1) / 2 + cs * es
    clauses = int(clauses)
    varcount = vs * cs
    lines = []
    lines.append( "p cnf " + str(varcount) + " " + str(clauses) )
    lines.append( "c n is at least one color" )
    lines.extend( crules1 )
    lines.append( "c n is not two colors at once" )
    lines.extend( crules2 )
    # header for edges added in alledgerules
    lines.extend( erules )

    return lines

def compiletofile( filename, matrix, colors ):
    vertices = len(matrix)
    output = cumpile( matrix, vertices, colors )

    with open( filename, "w" ) as file:
        for i in range(len(output)):
            file.write( output[i] )
            file.write( "\n" )




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


def indexify( i, j, d ):
    return i*d + j

#adjs = [index, dim*i + j][ list of (i',j') pairs]
def adjacent( grid, excfilter ):
    adjs = []
    dim = len(grid)
    index = 0
    for i in range(dim):
        for j in range(dim):
            #adjs.append([])
            #excring = makering( excfilter, (i,j), dim )
            adjs.append( makering( excfilter, (i,j), dim ) )
            #for k in range(len(excring)):
                #adjs[index].append( (cowrap(excring[k][0] + i, dim), cowrap(excring[k][1] + j, dim)) )
            index += 1
    return adjs

#translate list of unordered adjacencies
#into adjacency matrix
def adjtomat( adjs, dim ):
    adjacency = np.zeros( (dim**2,dim**2) )
    for i in range(len(adjs)):
        for j in range(len(adjs[i])):
            index = adjs[i][j]
            adjacency[i][indexify( index[0], index[1], dim )] = 1
            adjacency[indexify( index[0], index[1], dim )][i] = 1
    return adjacency

def printadj( adjacency ):
    n = len(adjacency)
    for i in range(n):
        print( str(adjacency[i]) + "," )



def main():
    # init grid
    grid = makerandgrid( gridsize, colornum )
    #printimg( grid, filenames[0], None )
    excfilter = makeexclusion( gridsize, radsqrs )
    #printadj( adjacent( grid, excfilter ) )
    adjacency = adjtomat( adjacent( grid, excfilter ), len(grid) )
    #printadj( adjacency )
    compiletofile( "test.txt", adjacency, colornum )

main()
