import networkx as nx
from customEdge import my_draw_networkx_edge_labels
import flowshop as fs
import matplotlib.pyplot as plt
import argparse

def createParser():
    parser = argparse.ArgumentParser(description='Run Optimisation Model')
    parser.add_argument('--input', '-i',
                        type=str,
                        action='store',
                        help='XML Input File')
    parser.add_argument('--schedule', '-s',
                        type=str,
                        action='store',
                        help='txt Schedule File')
    return parser

def build_graph(instance):
    g = nx.DiGraph()
    i = 0
    #add vertices
    colours = ["lightblue","yellow","lightgreen"]
    for job in range(instance.njobs):
        for op in range(instance.nops):
            # print(job, op)
            # print(instance.njobs)
            # print(instance.start)
            g.add_node(i,
                        pos=(job,-op),
                        label=f"{job},{op}",
                        colour=colours[instance.flowVector[op]],
                        start=instance.start[job][op])
            instance.graphIndex[(job,op)] = i
            i+=1

    #TODO:add correct weights
    #add edges
    setupEdges = []
    dueEdges = []
    sequenceEdges = []
    #add intra job edges
    for job in range(instance.njobs):
        for op in range(instance.nops-1):
            g.add_edge(instance.graphIndex[(job,op)],instance.graphIndex[(job,op+1)],
                        weight=-(instance.processing[job][op] + instance.setup[(job,op)][(job,op+1)]))
            g.add_edge(instance.graphIndex[(job,op+1)],instance.graphIndex[(job,op)],
                        weight=instance.due[(job,op+1)][(job,op)])

            setupEdges.append((instance.graphIndex[(job,op)],instance.graphIndex[(job,op+1)],
                                {'w':-(instance.processing[job][op] + instance.setup[(job,op)][(job,op+1)])}))
            dueEdges.append((instance.graphIndex[(job,op+1)],instance.graphIndex[(job,op)],{'w':instance.due[(job,op+1)][(job,op)]}))
    
    #add inter job edges
    for job in range(instance.njobs-1):
        for op in range(instance.nops):
            g.add_edge(instance.graphIndex[(job,op)],instance.graphIndex[(job+1,op)],
                        weight=-(instance.processing[job][op] + instance.setup[(job,op)][(job+1,op)]))
            setupEdges.append((instance.graphIndex[(job,op)],instance.graphIndex[(job+1,op)],
                                {'w':-(instance.processing[job][op] + instance.setup[(job,op)][(job+1,op)])}))

    #add schedule edges
    sequence = instance.extract_sequence()
    for m in sequence:
        sortedOps = sorted(sequence[m], key=sequence[m].get)
        for index,operation in enumerate(sortedOps[:-1]):
            g.add_edge(instance.graphIndex[sortedOps[index]],instance.graphIndex[sortedOps[index+1]],
                        weight=-(instance.processing[sortedOps[index][0]][sortedOps[index][1]] + instance.setup[sortedOps[index]][sortedOps[index+1]]))
            sequenceEdges.append((instance.graphIndex[sortedOps[index]],instance.graphIndex[sortedOps[index+1]],
                        {'w':-(instance.processing[sortedOps[index][0]][sortedOps[index][1]] + instance.setup[sortedOps[index]][sortedOps[index+1]])}))
    return g,setupEdges,dueEdges,sequenceEdges

def draw_graph(graph,setupEdges,dueEdges,sequenceEdges):
    g = graph
    pos = nx.get_node_attributes(g,'pos')
    pos_start_labels = {k:(v[0], v[1]+0.09) for k, v in pos.items()}
    node_labels = nx.get_node_attributes(g,'label')
    node_colours = nx.get_node_attributes(g,'colour')
    node_start = nx.get_node_attributes(g,'start')
    edge_labels = nx.get_edge_attributes(g,'weight')
    setupEdgeLabels = {(a,b):c['w'] for a,b,c in setupEdges}
    dueEdgeLabels = {(a,b):c['w'] for a,b,c in dueEdges}
    sequenceEdgeLabels = {(a,b):c['w'] for a,b,c in sequenceEdges}

    nx.draw_networkx_nodes(g,pos,node_size=500,node_color=[node_colours[key] for key in node_colours])
    nx.draw_networkx_edges(g,pos,edgelist=setupEdges,edge_color="grey")
    nx.draw_networkx_edges(g,pos,edgelist=dueEdges,connectionstyle="arc3,rad=-0.3",edge_color="grey",style="dashed")
    nx.draw_networkx_edges(g,pos,edgelist=sequenceEdges,edge_color="black",width=2)

    nx.draw_networkx_labels(g, pos, labels=node_labels)
    nx.draw_networkx_labels(g, pos_start_labels, labels=node_start,font_size=10,font_color="purple")
    nx.draw_networkx_edge_labels(g, pos, edge_labels=setupEdgeLabels)
    my_draw_networkx_edge_labels(g, pos, edge_labels=dueEdgeLabels,rad =-0.3)
    nx.draw_networkx_edge_labels(g, pos, edge_labels=sequenceEdgeLabels)
    plt.show()


def run(args):
    instance = fs.extract_instance(args.input,args.schedule)
    graph,setupEdges,dueEdges,sequenceEdges = build_graph(instance)
    draw_graph(graph,setupEdges,dueEdges,sequenceEdges)
    

def main():
    parser = createParser()
    args = parser.parse_args()
    run(args)

if __name__ == "__main__":
    main()



