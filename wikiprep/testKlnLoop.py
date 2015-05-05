import numpy



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
    
    groups_index = numpy.random.randint(0,
                                        high=numpy.random.randint(2, max_groups + 1),
                                        size=n)
    return groups_index


def modularity(A, groups, L):
    """
    Newman modularity.

    :type A: numpy.array, 2d
    :param graph: adjacency matrix

    :type groups: numpy.array
    :param groups: array of length n, where n = graph.number_of_nodes().
    Indicates which nodes belong to which groups, where each node is assigned
    an integer corresponding to the group index

    :type L: float (or int, but force float)
    :param L: lambda
    """

    L = float(L)
    comms = numpy.unique(groups)
    Q = 0
    indx = range(A.shape[0])
    for i in comms:
        x = (groups==i).astype(int)
        Q = Q + numpy.dot(x, bMultiply(x, A, indx, L))
    Q = Q / A.sum()
    return Q


def bMultiply(x, A, indx, L):
    """
    :type x: numpy.array
    :param x: column vector, len n, 1 if node is in the current group,
    0 otherwise

    :type A: numpy.array, 2d; consider switching to scipy.sparse
    :param A: adjacency matrix
    """
    j = A.sum(axis=1)
    jx = numpy.dot(j.reshape((1,j.size)), x) 
    two_m = sum(j)
    x2 = numpy.dot(A, x)
    x3 = (L * jx / two_m) * j
    v = x2 - x3
    v = v[indx]
    return v


def resetGroupNames(groups):
    """

    """
    group_names = numpy.unique(groups)
    new_group_names = numpy.array(range(len(group_names)))
    group_lookup = {k:v for (k,v) in zip(group_names, new_group_names)}
    groups = numpy.array([group_lookup[g] for g in groups])
    return groups


def mKL(groups, A, indx, L, allow_make_new=True):
    """

    """    
    n = A.shape[0]
    k = A.sum(axis=1).reshape((n,))
    kk2m = k * k / float(sum(k)) * L

    groups = resetGroupNames(groups)
    score = modularity(A, groups, L)
    print('Initial score: %s' % score)
    indx_orig = indx[:]
    score_prev = -999
    num_iter = 0
    
    # insert code for timing loops, code

    while score > score_prev:
        score_prev = score
        num_iter += 1
        indx = indx_orig[:]
        group_names = numpy.unique(groups[indx])
        print('group names: %s' % group_names)
        test_groups = groups.copy()
        
        while indx:
            print("test groups: %s" % test_groups)
            
            node_contrib = numpy.zeros((n, len(group_names)))
            for i, g in enumerate(group_names):
                x = (test_groups == i).astype(int)
                node_contrib[:,i] = bMultiply(x, A, range(n), L)
            node_contrib = node_contrib.reshape((node_contrib.size,))            

            curr_contrib_index = (numpy.array(range(n)) * len(group_names)\
                                  + test_groups).astype(int)
            print curr_contrib_index
            curr_contrib = node_contrib[curr_contrib_index] + kk2m

            node_contrib = node_contrib -\
                           numpy.repeat(curr_contrib, len(group_names))
            node_contrib[curr_contrib_index] = -999
            node_contrib = node_contrib.reshape((n, len(group_names)))

            node_contrib = node_contrib[indx,]
            curr_contrib = curr_contrib[indx,]

            max_contrib = node_contrib.max()
            
            make_new = max(-curr_contrib) >= max_contrib

            if make_new and allow_make_new:
                best_node = indx[numpy.random.choice(\
                    numpy.where(-curr_contrib == max(-curr_contrib))[0])]
                best_group = max(test_groups) + 1
                group_names = numpy.resize(group_names,
                                           group_names.size + 1)
                group_names[-1] = best_group
                print("Group names use %s: " % group_names)
            else:    
                (inds, grps) = numpy.where(node_contrib == max_contrib)
                rand_tie_break = numpy.random.randint(0, len(inds))
                best_node = indx[inds[rand_tie_break]]
                best_group = grps[rand_tie_break]

            print('best node %s' % best_node)
            print('best group %s' % best_group)

            test_groups[best_node] = best_group
            indx.remove(best_node)
            new_score = modularity(A, test_groups, L)
            if new_score > score:
                groups = test_groups.copy()
                score = new_score

        groups = resetGroupNames(groups)
        print('groups: %s' % groups)

    return groups, score


def main():
    allow_make_new = True
    n = 8
    indx = range(n)
    A = (numpy.random.uniform(size=n*n) < 0.2).\
        astype(int).\
        reshape((n, n))
    A = A + A.T
    A[A==2] = 1
    A = A - numpy.diag(A.diagonal())
    L = 1
    A = numpy.array([[0,1,0,0,0,0,0,0],
                     [1,0,1,0,0,0,0,0],
                     [0,1,0,1,0,0,0,0],
                     [0,0,1,0,1,0,0,0],
                     [0,0,0,1,0,1,0,0],
                     [0,0,0,0,1,0,1,0],
                     [0,0,0,0,0,1,0,1],
                     [0,0,0,0,0,0,1,0]])
##    groups = numpy.ones(n)
##    while len(numpy.unique(groups)) == 1:
##        groups = spanSpace(n, 3)

##    groups = numpy.array(range(n))
    groups = numpy.array([1,1,2,2,3,3,4,4])

    groups, score = mKL(groups, A, indx, L, allow_make_new=False)
    print("Final groups: %s" % groups)
    print("Final score: %s" % score)


if __name__ == "__main__":
    main()

