# -*- coding: utf-8 -*-
#!/usr/bin/env python

# 199 2345
# 1   DT [0-1]    0 
# ...
# 6   NP [0-2]    1 
#       1 4 ||| 0=-5.342
# ...
    
import sys, os
sys.path.append("../gen_py/")

from protobuf_json import pb2json

from hypergraph_pb2 import *
from features_pb2 import *
from translation_pb2 import *


def load(handle):            
        line = None
        num_sents = 0        

        while True:
            forest = Hypergraph()
            line = handle.readline() 
            if len(line) == 0:
                break
            try:                        
                tag, sent = line.split("\t")   # foreign sentence
                
            except:
                ## no more forests
                yield None
                continue

            num_sents += 1

            ## read in references
            refnum = int(handle.readline().strip())
            for i in xrange(refnum):
                ref = handle.readline().strip()
                forest.Extensions[reference_sentences].append(ref)
                
            forest.Extensions[foreign_sentence] = sent.decode('UTF-8')
            
            ## sizes: number of nodes, number of edges (optional)
            num, nedges = map(int, handle.readline().split("\t"))   


            for i in xrange(1, num+1):
                node = forest.node.add()
                ## '2\tDT* [0-1]\t1 ||| 1232=2 ...\n'
                ## node-based features here: wordedges, greedyheavy, word(1), [word(2)], ...
                line = handle.readline()
                try:
                    keys, fields = line.split(" ||| ")
                except:
                    keys = line
                    fields = ""

                iden, labelspan, size = keys.split("\t") ## iden can be non-ints
                size = int(size)



                
                node.id = int(iden)
                node.label = labelspan

                fpair = node.Extensions[node_fv] =fields.decode("UTF-8")
            
                for j in xrange(size):
                    edge = node.edge.add()
                    
                    ## '\t1 ||| 0=8.86276 1=2 3\n'
                    ## N.B.: can't just strip! "\t... ||| ... ||| \n" => 2 fields instead of 3
                    tails, rule, fields = handle.readline().strip("\t\n").split(" ||| ")


                    tails = tails.split() 
                    tailnodes = []
                    
                    for x in tails:
                        if x[0]=='"': 
                            pass
                        else: 
                            tailnodes.append(int(x))

                    for t in tailnodes:
                        edge.tail_node_ids.append(t)
                    edge.label = rule.decode('UTF-8')
                               
                    edge.Extensions[edge_fv] =fields

            forest.root = node.id
            line = handle.readline()
            yield forest


if __name__ == "__main__":
    for f in load(sys.stdin):
        print f
        print pb2json(f)
