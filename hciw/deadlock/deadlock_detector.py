"""Deadlock detection mechanisms for queueing networks."""

import networkx as nx


class NoDetection:
    """A generic class for all deadlock detector classes to inherit from.

    Using this class is equivalent to having no deadlock detection
    capabilities.
    """

    def __init__(self):
        """Initialise the detection mechanism class."""
        pass

    def initialise_at_node(self, node):
        """Initialise the detection mechanism when the node is created.

        Args:
            node (hciw.Node): The node being created.
        """
        pass

    def detect_deadlock(self):
        """Return whether deadlock has been reached.

        Returns:
            bool: ``True`` if deadlock is reached, otherwise ``False``.
        """
        return False

    def action_at_attach_server(self, node, server, individual):
        """Take action when the node's ``attach_server`` method is called.

        Args:
            node (hciw.Node): The node the server is attached to.
            server (hciw.Server): The server being attached.
            individual (hciw.Individual): The individual being served.
        """
        pass

    def action_at_blockage(self, individual, next_node):
        """Take action when the node's ``block_individual`` method is called.

        Args:
            individual (hciw.Individual): The individual being blocked.
            next_node (hciw.Node): The node the individual is blocked from
                entering.
        """
        pass

    def action_at_detatch_server(self, server):
        """Take action when the node's ``detatch_server`` method is called.

        Args:
            server (hciw.Server): The server being detached.
        """
        pass


class StateDigraph(NoDetection):
    """Keep track of a directed graph of the simulation state.

    Vertices represent servers. Edges represent blockage relationships,
    such that there is a directed edge from vertex ``j`` to vertex ``k`` if
    and only if the customer at server ``j`` is blocked from entering the
    node that contains ``k``. Deadlock is equivalent to a knot in the
    directed graph.
    """

    def __init__(self):
        """Initialise the state digraph detection mechanism class."""
        self.statedigraph = nx.DiGraph()

    def initialise_at_node(self, node):
        """Initialise the state digraph when the node is created.

        Adds the servers of that node if ``c < Inf``.

        Args:
            node (hciw.Node): The node being created.
        """
        if node.c < float("Inf"):
            self.statedigraph.add_nodes_from([str(s) for s in node.servers])

    def detect_deadlock(self):
        """Detect whether the system is in a deadlocked state.

        That is, whether there is a knot. Note that this code is taken and
        adapted from the NetworkX Developer Zone Ticket #663 knot.py
        (09/06/2015).

        Returns:
            bool: ``True`` if a knot exists, otherwise ``False``.
        """
        knots = []
        for c in nx.strongly_connected_components(self.statedigraph):
            subgraph = self.statedigraph.subgraph(c)
            nodes = set(subgraph.nodes())
            if len(nodes) == 1:
                n = nodes.pop()
                nodes.add(n)
                if set(self.statedigraph.successors(n)) == nodes:
                    knots.append(subgraph)
            else:
                for n in nodes:
                    successors = nx.descendants(self.statedigraph, n)
                    if successors <= nodes:
                        knots.append(subgraph)
                        break
        if len(knots) > 0:
            return True
        return False

    def action_at_attach_server(self, node, server, individual):
        """Take action when the node's ``attach_server`` method is called.

        If a new customer joins a server, and their server is still blocking
        a customer, then that edge needs to remain. However it was removed
        in :meth:`action_at_detatch_server`, so it needs to be added back in.

        Args:
            node (hciw.Node): The node the server is attached to.
            server (hciw.Server): The server being attached.
            individual (hciw.Individual): The individual being served.
        """
        for blq in node.blocked_queue:
            inds = [
                ind for ind in node.simulation.nodes[blq[0]].all_individuals
                if ind.id_number == blq[1]
            ]
            ind = inds[0]
            if ind != individual:
                self.statedigraph.add_edge(str(ind.server), str(server))

    def action_at_blockage(self, individual, next_node):
        """Take action when the node's ``block_individual`` method is called.

        Adds edges between the blocked server and the servers of the next
        node.

        Args:
            individual (hciw.Individual): The individual being blocked.
            next_node (hciw.Node): The node the individual is blocked from
                entering.
        """
        for svr in next_node.servers:
            self.statedigraph.add_edge(str(individual.server), str(svr))

    def action_at_detatch_server(self, server):
        """Take action when the node's ``detatch_server`` method is called.

        Removes any edges of servers that have been detached.

        Args:
            server (hciw.Server): The server being detached.
        """
        self.statedigraph.remove_edges_from(
            list(self.statedigraph.in_edges(str(server)))
            + list(self.statedigraph.out_edges(str(server)))
        )
