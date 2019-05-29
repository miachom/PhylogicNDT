import numpy as np
import logging
import operator
import collections
from Tree import Tree

logging.basicConfig(filename='build_tree_engine.log',
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    level=getattr(logging, "INFO"))

CLONAL_CLUSTER = 1


class BuildTreeEngine:

    def __init__(self, patient):
        '''
        Args:
            patient:
        '''
        # patient object should have pointer to clustering results object but for now it is two separate objects
        self._patient = patient
        if patient.ClusteringResults:
            self._clustering_results = patient.ClusteringResults
        else:
            logging.error(' Clustering results are not found, need to run clustering first')
        # List of likelihoods for trees at each iteration
        self._ll_trail = []
        # List of trees (list of edges) at each iteration
        self._mcmc_trace = []
        self._top_tree = None

    @property
    def trees_ll(self):
        return self._ll_trail

    @property
    def trees(self):
        return self._mcmc_trace

    @property
    def mcmc_trace(self):
        sorted_edges = map(set, sorted(self._mcmc_trace, key=lambda tup: tup[0]))
        counts = collections.Counter(map(tuple, sorted_edges))
        return sorted(counts.items(), key=operator.itemgetter(1), reverse=True)

    def _initialize_tree(self, edges=None, nodes=None):
        # Create Tree object
        tree = Tree()
        # add nodes to the tree
        if nodes:
            tree.add_nodes(nodes)
        else:
            for cluster_id, cluster in self._clustering_results.clusters.items():
                tree.add_node(cluster.identifier, data=cluster.densities)
            # TODO find clonal cluster and set it as a root
            root = tree.nodes[CLONAL_CLUSTER]
            tree.set_root(root)
        if edges:
            tree.add_edges(edges)
        else:
            # add edges (initially all edges are children of Clonal cluster)
            for identifier, node in tree.nodes.items():
                if identifier != CLONAL_CLUSTER:
                    tree.add_edge(root, node)
        logging.debug('Tree initialized with edges {}'.format(tree.edges))
        return tree

    def build_tree(self, n_iter=1000, burn_in=10):
        '''
        Main function to construct phylogenetic tree
        Returns:

        '''
        tree = self._initialize_tree()
        time_points = self._clustering_results.samples
        for n in range(n_iter + burn_in):
            # check that it is not None
            logging.debug('Iteration number {}'.format(n))
            # Randomly pick any node to move (except root, which is clonal)
            node_to_move = tree.get_random_node()
            logging.debug('Node to move {}'.format(node_to_move.identifier))
            # List of all possible Trees and corresponding likelihoods
            tree_choices, tree_choice_lik = tree.get_all_possible_moves(node_to_move, time_points)
            tree_idx = np.argmax(np.random.multinomial(1, tree_choice_lik))
            logging.debug('np.argmax(np.random.multinomial(1, tree_choice_lik)) = {}'.format(tree_idx))
            tree_edges_selected = tree_choices[tree_idx]
            if n > burn_in:
                self._mcmc_trace.append(tree_edges_selected)
                self._ll_trail.append(tree_choice_lik[tree_idx])
            logging.debug('Tree to choose edges \n{}'.format(tree_edges_selected))
            # TODO Reshuffle mutations
            # Initialize Tree of choice for the next iteration
            # update Nodes pointers to parents and children
            tree.set_new_edges(tree_edges_selected)
        self._set_top_tree()

    def _set_top_tree(self):
        top_tree_edges = self._mcmc_trace[np.argmax(self._ll_trail)]
        self._top_tree = self._initialize_tree(top_tree_edges)

    @property
    def top_tree(self):
        return self._top_tree

    def get_cell_ancestry(self):
        cells_ancestry = {}
        for node_id in self._top_tree.nodes:
            cells_ancestry[node_id] = self._top_tree.get_ancestry(node_id)
        return cells_ancestry
