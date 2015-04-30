
import numpy
import time


def KLNLoop(graph, scoreFunction, itt):
    """
    :type graph: networkx.graph
    :param graph: the graph being analyzed

    :type scoreFunction: python function
    :param scoreFunction: evaluation score function to be minimized

    :type itt: int
    :param itt: number of random starting positions to run mKL
    """

    number_of_groups_current = graph.number_of_nodes()
    graph_current = graph.copy()
    span_space_modifier = 0.55

    while number_of_groups_current > 1:
        
        n = graph_current.number_of_nodes()
        groups_start_hold = numpy.zeros((n, itt))
        groups_final_hold = numpy.zeros((n, itt))
        scores = []
        times = []

        for j in range(itt):
            groups_start_hold[:,j] = spanSpace(n, n*span_space_mod)
            nkl_out = newmanklAllownew(groups_current, graph, range(n), scoreFunction)
            groups_current = reassignGroups(nlk_out['groups'])
            groups_final_hold[:,k] = grops_current.T
            scores.append(nkl_out['score'])
            times.append(nkl_out['time'])


def mKL(groups, graph, indx, scoreFunc, contribFunc):
    """

    """
    group_names = numpy.unique(groups)
    differences = numpy.diff(group_names)
    cuts = len(numpy.unique(differences))
    
    num_nodes = graph.number_of_nodes()
    num_edges = graph.number_of_edges()
    
    score = scoreFunc(groups, graph)
    indx_orig = indx
    score_prev = -9999
    num_iter = 0
    # insert code for timing loops, code

    while score > score_prev:
        score = score_prev
        num_iter += 1
        group_names_use = numpy.unique(groups[indx])
        test_groups = groups

        while indx:
            # need to clean this up; Should return nodes as row, groups as col
            node_contrib_current = calcNodeContributions(graph,
                                                         test_groups,
                                                         group_names_use,
                                                         contribCalc)
            ## Purpose: determine which node will switch groups,
            ## and where it will go
            max_contrib = node_contrib_current.max()
            
            make_new = - node_contrib_current_group[i] > max_contrib
            if make_new and allow_make_new:
                ## Determine if any node's negative contribution to it's group
                ## is larger in magnitude than max_contrib;
                ## if so, move to its own group in leui of moving the previously
                ## selected node
            else:
                i = numpy.where(node_contrib_current==max_contrib)
                i = (numpy.array(i[0]).reshape(numpy.array(i[0]).size,),
                    numpy.array(i[0]).reshape(numpy.array(i[0]).size,))
                j = numpy.floor(len(i[0]) * numpy.random.uniform())
                node_to_move = i[0][j]
                group_to_move_to = i[1][j]

            testgroups[node_to_move] = group_to_move_to
            indx.remove(node_to_move)
            best_score = scoreFunc(graph, test_groups)
            if best_score > score:
                groups = test_groups
                score = best_score

    score = scoreFunc(graph, groups)
            
            
            
            
                                                              
            
            
    


def spanSpace(n, max_groups):
    """
    Randomly assigns nodes to a random number of groups (less than
    or equal to 'max_groups')

    :type n: int
    :param n: number of nodes in the graph

    :type max_groups: numeric
    :param max groups: indicates the maximum number of groups the nodes
    are to be split into
    """
    num_groups = numpy.ceil(numpy.random.uniform()*max_groups)
    groups_index = numpy.random.randint(0, high=num_groups, size=n)
    return groups_index



def reassignGroups(groups):
    """Renumbers groups so numbers start at '0' and no gaps"""
    group_names = numpy.unique(groups)
    num_groups = len(group_names)
    groups += group_names[-1]
    group_names += group_names[-1]

    pos_index = numpy.ones((num_groups,), dtype=int) * -1
    for i, g in enumerate(group_names):
        pos_index[i] = numpy.where(groups==g)[0][0]
    pos_index.sort()
    for i in range(num_groups):
        groups[numpy.where(groups==groups[pos_index[i]])] = i
    return groups


def calcNodeContributions():
    nodecontributions=zeros(length(A),length(gpart));
    for ig=1:length(gpart),
        nodecontributions(:,ig)=...
            BMultiply((testgroups==gpart(ig))',A,1:length(A),L);
    end
    glookup(gpart)=1:length(gpart);
    currcontribindex=[1:N]'+(glookup(testgroups)'-1)*N;
    currcontrib=nodecontributions(currcontribindex)+kk2m;
    nodecontributions=nodecontributions-...
        currcontrib*ones(1,length(gpart));
    nodecontributions(currcontribindex)=-999; %Ignore current placement
    nodecontributions=nodecontributions(indx,:); %Restrict to available nodes
    currcontrib=currcontrib(indx,:); %Restrict to available nodes
    

def main():
    """

    """
    scoreFunc = lambda groups, graph : modularity(groups, graph, L)
    contribFunc = lambda group_members, graph, indx : \
                  bMultiply(group_members, graph, indx, L)
