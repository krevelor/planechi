"""


def tokenize( line ):
    if line[0] == 'c' or line[0] == 'p':
        return [line]
    return line.split(" ")

def restring( tokens, dictionary ):
    if len(tokens) == 1:
        return tokens[0]
    string = ""
    for i in range(len(tokens) - 1):
        token = tokens[i]
        name = token
        if token[0] == '-':
            string += "-"
            name = token[1:]
        string += dictionary[name]
        string += " "
    string += "0"
    return string

def makedict( tokens ):
    idty = 1
    dictionary = {}
    for i in range(len(tokens)):
        for j in range(len(tokens[i]) - 1):
            token = tokens[i][j]
            if not token in dictionary:
                dictionary[token] = str(idty)
                idty += 1
    return dictionary

text = ("p cnf 12 31\nc n is at least one color\nx00 x01 x02 0\nx10 x11 x12 0\nx20 x21 x22 0\nx30 x31 x32 0\nc n is not two colors at once\n-x00 -x01 0\n-x00 -x02 0\n-x01 -x02 0\n-x10 -x11 0\n-x10 -x12 0\n-x11 -x12 0\n-x20 -x21 0\n-x20 -x22 0\n-x21 -x22 0\n-x30 -x31 0\n-x30 -x32 0\n-x31 -x32 0\nc edges\nc edge 01\n-x00 -x10 0\n-x01 -x11 0\n-x02 -x12 0\nc edge 02\n-x00 -x20 0\n-x01 -x21 0\n-x02 -x22 0\nc edge 12\n-x10 -x20 0\n-x11 -x21 0\n-x12 -x22 0\nc edge 13\n-x10 -x30 0\n-x11 -x31 0\n-x12 -x32 0\nc edge 23\n-x20 -x30 0\n-x21 -x31 0\n-x22 -x32 0")



lines = text.split("\n")
tokens = []
for i in range(len(lines)):
    tokens.append( tokenize( lines[i] ) )
dictionary = makedict( tokens )
for i in range(len(tokens)):
    print( restring( tokens[i], dictionary ) )

"""
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


####################################
#
#       DO NOT EDIT FOR NOW
#
####################################

matrix = [[ 0, 1, 1, 0, 0, 0, 1 ],
             [ 1, 0, 1, 1, 0, 0, 0 ],
             [ 1, 1, 0, 1, 0, 0, 0 ],
             [ 0, 1, 1, 0, 1, 1, 0 ],
             [ 0, 0, 0, 1, 0, 1, 1 ],
             [ 0, 0, 0, 1, 1, 0, 1 ],
             [ 1, 0, 0, 0, 1, 1, 0 ]]
colors = 4

#matrix = [[ 0, 1, 1, 0 ],
#             [ 1, 0, 1, 1 ],
#             [ 1, 1, 0, 1 ],
#             [ 0, 1, 1, 0 ]]
#colors = 3
vertices = len(matrix)
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


output = cumpile( matrix, vertices, colors )
filename = "cnf.txt"

with open( filename, "w" ) as file:
    for i in range(len(output)):
        file.write( output[i] )
        file.write( "\n" )



####################################
#
#       DO NOT EDIT FOR NOW
#
####################################
