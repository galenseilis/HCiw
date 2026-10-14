"""Routing classes that determine the next node an individual visits."""

import itertools

import hciw


class NetworkRouting:
    """Hold a number of routing objects, one for each node."""

    def __init__(self, routers):
        """Set up the router objects for each node.

        Args:
            routers (list): The routing objects, one for each node.
        """
        self.routers = routers

    def initialise(self, simulation):
        """Give the simulation and node attributes to the routing objects.

        Args:
            simulation (hciw.Simulation): The simulation the routers belong
                to.
        """
        self.simulation = simulation
        for router, node in zip(self.routers, self.simulation.transitive_nodes, strict=False):
            router.initialise(self.simulation, node)

    def initialise_individual(self, ind):
        """Run at the arrival node when the individual is spawned.

        Args:
            ind (hciw.Individual): The individual being spawned.
        """
        pass

    def next_node(self, ind, node_id):
        """Choose the next node.

        Args:
            ind (hciw.Individual): The individual being routed.
            node_id (int): The id number of the node the individual is at.

        Returns:
            hciw.Node: The next node.
        """
        return self.routers[node_id - 1].next_node(ind)

    def next_node_for_rerouting(self, ind, node_id):
        """Choose the next node when rerouting a preempted customer.

        Args:
            ind (hciw.Individual): The individual being routed.
            node_id (int): The id number of the node the individual is at.

        Returns:
            hciw.Node: The next node.
        """
        return self.routers[node_id - 1].next_node_for_rerouting(ind)

    def next_node_for_jockeying(self, ind, node_id):
        """Choose the next node when jockeying to another node after reneging.

        Args:
            ind (hciw.Individual): The individual being routed.
            node_id (int): The id number of the node the individual is at.

        Returns:
            hciw.Node: The next node.
        """
        return self.routers[node_id - 1].next_node_for_jockeying(ind)


class TransitionMatrix(NetworkRouting):
    """Hold a number of probabilistic routing objects."""

    def __init__(self, transition_matrix):
        """Set up the relevant probabilistic router objects for each node.

        Args:
            transition_matrix (list): A square matrix where the entry in row
                ``i`` and column ``j`` is the probability of moving from node
                ``i + 1`` to node ``j + 1``.
        """
        n_destinations = len(transition_matrix)
        self.routers = [
            Probabilistic(
                destinations=[i for i in range(1, n_destinations + 1)], probs=row
            )
            for row in transition_matrix
        ]

    def initialise(self, simulation):
        """Give the simulation to the routing objects.

        Args:
            simulation (hciw.Simulation): The simulation the routers belong
                to.

        Raises:
            ValueError: If the number of rows in the transition matrix does
                not equal the number of nodes in the network.
        """
        super().initialise(simulation)
        if len(self.routers) != simulation.network.number_of_nodes:
            raise ValueError(
                "Ensure a transition matrix is given, and that the number of rows is equal to the number of nodes in the network."
            )


class ProcessBased(NetworkRouting):
    """Route an individual based on a pre-defined process."""

    def __init__(self, route_function):
        """Initialise the routing object.

        Args:
            route_function (callable): A function that returns a pre-defined
                route for an individual.
        """
        self.route_function = route_function

    def initialise(self, simulation):
        """Give the simulation and node attributes to the routing objects.

        Args:
            simulation (hciw.Simulation): The simulation the routers belong
                to.
        """
        self.simulation = simulation

    def initialise_individual(self, ind):
        """Set the route of the individual when they are spawned.

        Args:
            ind (hciw.Individual): The individual being spawned.
        """
        ind.route = self.route_function(ind, self.simulation)

    def next_node(self, ind, node_id):
        """Choose the next node from the process-based pre-defined route.

        Args:
            ind (hciw.Individual): The individual being routed.
            node_id (int): The id number of the node the individual is at.

        Returns:
            hciw.Node: The next node.
        """
        node_index = -1 if len(ind.route) == 0 else ind.route.pop(0)
        return self.simulation.nodes[node_index]

    def next_node_for_rerouting(self, ind, node_id):
        """Choose the next node when rerouting a preempted customer.

        Args:
            ind (hciw.Individual): The individual being routed.
            node_id (int): The id number of the node the individual is at.

        Returns:
            hciw.Node: The next node.
        """
        return self.next_node(ind, node_id)

    def next_node_for_jockeying(self, ind, node_id):
        """Choose the next node when jockeying to another node after reneging.

        Args:
            ind (hciw.Individual): The individual being routed.
            node_id (int): The id number of the node the individual is at.

        Returns:
            hciw.Node: The exit node.
        """
        return self.simulation.nodes[-1]


class FlexibleProcessBased(ProcessBased):
    """Route an individual based on a pre-defined process.

    The route is flexible: each step may be a subset of nodes from which the
    next node is chosen according to a rule and a choice method.
    """

    def __init__(self, route_function, rule, choice):
        """Initialise the routing object.

        Args:
            route_function (callable): A function that returns a pre-defined
                route for an individual.
            rule (str): Either ``'any'`` or ``'all'``.
            choice (str): Either ``'random'``, ``'jsq'`` or ``'lb'``.

        Raises:
            ValueError: If ``rule`` is not ``'any'`` or ``'all'``.
            ValueError: If ``choice`` is not ``'random'``, ``'jsq'`` or
                ``'lb'``.
        """
        self.route_function = route_function
        if rule not in ["any", "all"]:
            raise ValueError("Flexible routing rules must be one of 'any' or 'all'.")
        if choice not in ["random", "jsq", "lb"]:
            raise ValueError(
                "Flexible routing choices must be one of 'random', 'jsq', or 'lb'."
            )
        self.rule = rule
        self.choice = choice

    def find_next_node_from_subset(self, subset, ind):
        """Find the next node within a subset according to ``choice``.

        Args:
            subset (list): The subset of node indices to choose from.
            ind (hciw.Individual): The individual being routed.

        Returns:
            int: The id number of the chosen node.
        """
        if self.choice == "random":
            return hciw.random_choice(subset)
        if self.choice == "jsq":
            temp_router = JoinShortestQueue(destinations=subset)
            temp_router.initialise(self.simulation, None)
            nd = temp_router.next_node(ind)
            assert nd is not None
            return nd.id_number
        if self.choice == "lb":
            temp_router = LoadBalancing(destinations=subset)
            temp_router.initialise(self.simulation, None)
            nd = temp_router.next_node(ind)
            assert nd is not None
            return nd.id_number

    def update_individual_route(self, ind, next_node_id):
        """Remove chosen nodes from the individual's route according to ``rule``.

        Args:
            ind (hciw.Individual): The individual being routed.
            next_node_id (int): The id number of the chosen next node.
        """
        if self.rule == "any":
            ind.route = ind.route[1:]
        if self.rule == "all":
            ind.route[0].remove(next_node_id)
            if len(ind.route[0]) == 0:
                ind.route = ind.route[1:]

    def next_node(self, ind, node_id):
        """Choose the next node from the process-based pre-defined route.

        Args:
            ind (hciw.Individual): The individual being routed.
            node_id (int): The id number of the node the individual is at.

        Returns:
            hciw.Node: The next node.
        """
        if len(ind.route) == 0:
            node_index = -1
        else:
            node_index = self.find_next_node_from_subset(ind.route[0], ind)
            self.update_individual_route(ind, node_index)
        return self.simulation.nodes[node_index]


class NodeRouting:
    """A generic routing class to determine next sampled node."""

    def initialise(self, simulation, node):
        """Give the simulation and node attributes to the routing object.

        Args:
            simulation (hciw.Simulation): The simulation the router belongs
                to.
            node (hciw.Node): The node the router belongs to.
        """
        self.simulation = simulation
        self.node = node
        self.error_check_at_initialise()

    def error_check_at_initialise(self):
        """Check the routing object is valid when it is initialised."""
        pass

    def next_node(self, ind):
        """Choose the next node for an individual.

        Args:
            ind (hciw.Individual): The individual being routed.

        Returns:
            hciw.Node: The next node.
        """
        raise NotImplementedError

    def next_node_for_rerouting(self, ind):
        """Choose the next node when rerouting a preempted customer.

        By default, the next node for rerouting uses the same method as
        :meth:`next_node`.

        Args:
            ind (hciw.Individual): The individual being routed.

        Returns:
            hciw.Node: The next node.
        """
        return self.next_node(ind)

    def next_node_for_jockeying(self, ind):
        """Choose the next node when jockeying to another node after reneging.

        Args:
            ind (hciw.Individual): The individual being routed.

        Returns:
            hciw.Node: The exit node.
        """
        return self.simulation.nodes[-1]


class Probabilistic(NodeRouting):
    """A router that probabilistically chooses the next node."""

    def __init__(self, destinations, probs):
        """Initialise the routing object.

        Args:
            destinations (list): A list of node indices.
            probs (list): A list of probabilities associated with each
                destination.

        Raises:
            ValueError: If any probability is not a float.
            ValueError: If any probability is less than 0 or greater than 1.
            ValueError: If the probabilities sum to more than 1.
        """
        for p in probs:
            if not isinstance(p, float):
                raise ValueError("Routing probabilities must be a float.")
            if p < 0 or p > 1:
                raise ValueError("Routing probabilities must be between 0 and 1.")
        if sum(probs) > 1.0:
            raise ValueError("Routing probabilities must sum to 1 or less.")
        self.destinations = [*destinations, -1]
        self.probs = [*probs, 1 - sum(probs)]

    def error_check_at_initialise(self):
        """Check the probabilities and destinations are valid.

        Raises:
            ValueError: If the probabilities and destinations differ in
                length.
            ValueError: If the destinations are not a subset of the nodes in
                the network.
        """
        if len(self.probs) != len(self.destinations):
            raise ValueError(
                "Routing probabilities should correspond to destinations, and so should be lists of the same length."
            )
        if not set(self.destinations).issubset(
            set([nd.id_number for nd in self.simulation.nodes[1:]])
        ):
            raise ValueError(
                "Routing destinations should be a subset of the nodes in the network."
            )

    def next_node(self, ind):
        """Probabilistically choose the next node from the destinations.

        Args:
            ind (hciw.Individual): The individual being routed.

        Returns:
            hciw.Node: The next node.
        """
        node_index = hciw.random_choice(self.destinations, self.probs)
        return self.simulation.nodes[node_index]


class Direct(NodeRouting):
    """A router that sends the individual directly to another node."""

    def __init__(self, to):
        """Initialise the routing object.

        Args:
            to (int): The node index to send to.
        """
        self.to = to

    def next_node(self, ind):
        """Choose the node ``to`` with probability 1.

        Args:
            ind (hciw.Individual): The individual being routed.

        Returns:
            hciw.Node: The destination node.
        """
        return self.simulation.nodes[self.to]


class Leave(NodeRouting):
    """A router that sends the individual directly to the exit node."""

    def next_node(self, ind):
        """Choose the exit node with probability 1.

        Args:
            ind (hciw.Individual): The individual being routed.

        Returns:
            hciw.Node: The exit node.
        """
        return self.simulation.nodes[-1]


class JoinShortestQueue(NodeRouting):
    """A router that sends the individual to the node with the shortest queue.

    The node is chosen from a list of destinations.
    """

    def __init__(self, destinations, tie_break="random"):
        """Initialise the routing object.

        Args:
            destinations (list): A list of node indices.
            tie_break (str, optional): The method to deal with ties. One of
                ``'random'`` (randomly choose between ties) or ``'order'``
                (prioritise nodes in the order given by ``destinations``).
                Defaults to ``'random'``.
        """
        self.destinations = destinations
        self.tie_break = tie_break

    def error_check_at_initialise(self):
        """Check the destinations are a subset of the network's nodes.

        Raises:
            ValueError: If the destinations are not a subset of the nodes in
                the network.
        """
        if not set(self.destinations).issubset(
            set([nd.id_number for nd in self.simulation.nodes[1:]])
        ):
            raise ValueError(
                "Routing destinations should be a subset of the nodes in the network."
            )

    def get_queue_size(self, node_index):
        """Get the size of the queue at ``node_index``.

        Args:
            node_index (int): The index of the node.

        Returns:
            int: The number of waiting individuals.
        """
        return (
            self.simulation.nodes[node_index].number_of_individuals
            - self.simulation.nodes[node_index].number_in_service
        )

    def next_node(self, ind):
        """Choose the destination node with the shortest queue.

        Args:
            ind (hciw.Individual): The individual being routed.

        Returns:
            hciw.Node: The next node.
        """
        shortest_queues = []
        shortest_queue_size = float("inf")
        for node_index in self.destinations:
            queue_size = self.get_queue_size(node_index)
            if queue_size == shortest_queue_size:
                shortest_queues.append(node_index)
            if queue_size < shortest_queue_size:
                shortest_queues = [node_index]
                shortest_queue_size = queue_size
        if self.tie_break == "random":
            next_node_index = hciw.random_choice(shortest_queues)
            return self.simulation.nodes[next_node_index]
        if self.tie_break == "order":
            next_node_index = shortest_queues[0]
            return self.simulation.nodes[next_node_index]


class LoadBalancing(JoinShortestQueue):
    """A version of JoinShortestQueue that also counts customers in service."""

    def get_queue_size(self, node_index):
        """Get the size of the queue at ``node_index``.

        Args:
            node_index (int): The index of the node.

        Returns:
            int: The number of individuals at the node.
        """
        return self.simulation.nodes[node_index].number_of_individuals


class Cycle(NodeRouting):
    """A router that cycles through destinations, repeating the cycle once ended."""

    def __init__(self, cycle):
        """Initialise the routing object.

        Args:
            cycle (list): An ordered sequence of node indices.
        """
        self.cycle = cycle
        self.generator = itertools.cycle(self.cycle)

    def error_check_at_initialise(self):
        """Check the cycle is a subset of the network's nodes.

        Raises:
            ValueError: If the cycle is not a subset of the nodes in the
                network.
        """
        if not set(self.cycle).issubset(
            set([nd.id_number for nd in self.simulation.nodes[1:]])
        ):
            raise ValueError(
                "Routing destinations should be a subset of the nodes in the network."
            )

    def next_node(self, ind):
        """Choose the next node in the cycle.

        Args:
            ind (hciw.Individual): The individual being routed.

        Returns:
            hciw.Node: The next node.
        """
        next_node_index = next(self.generator)
        return self.simulation.nodes[next_node_index]
