"""State tracker classes that record the state of a simulation over time."""


class StateTracker:
    """A generic class to record a system's state."""

    def initialise(self, simulation):
        """Initialise the state tracker class.

        Args:
            simulation (hciw.Simulation): The simulation being tracked.
        """
        self.simulation = simulation
        self.state = None
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node, ind):
        """Change the state of the system when a customer is accepted.

        Args:
            node (hciw.Node): The node at which the individual is accepted.
            ind (hciw.Individual): The individual being accepted.
        """
        pass

    def change_state_block(self, node, destination, ind):
        """Change the state of the system when a customer gets blocked.

        Args:
            node (hciw.Node): The node at which the individual is blocked.
            destination (hciw.Node): The node the individual is blocked from
                entering.
            ind (hciw.Individual): The individual being blocked.
        """
        pass

    def change_state_release(self, node, destination, ind, blocked):
        """Change the state of the system when a customer is released.

        Args:
            node (hciw.Node): The node at which the individual is released.
            destination (hciw.Node): The node the individual was blocked from
                entering.
            ind (hciw.Individual): The individual being released.
            blocked (bool): Whether the individual was blocked.
        """
        pass

    def change_state_renege(self, node, destination, ind, blocked):
        """Change the state of the system when a customer reneges.

        Args:
            node (hciw.Node): The node at which the individual reneges.
            destination (hciw.Node): The node the individual was blocked from
                entering.
            ind (hciw.Individual): The individual reneging.
            blocked (bool): Whether the individual was blocked.
        """
        self.change_state_release(node, destination, ind, blocked)

    def change_state_classchange(self, node, ind):
        """Change the state of the system when a customer changes class.

        Args:
            node (hciw.Node): The node at which the individual changes class.
            ind (hciw.Individual): The individual changing class.
        """
        pass

    def hash_state(self) -> object:
        """Return a hashable state.

        Returns:
            Hashable: A hashable representation of the state.
        """
        return None

    def timestamp(self):
        """Record the current state in the history if it has changed."""
        current_hash_state = self.hash_state()
        if current_hash_state != self.history[-1][1]:
            self.history.append([self.simulation.current_time, current_hash_state])

    def state_probabilities(self, observation_period=(0, float("Inf"))):
        """Get the state probabilities from the history.

        Args:
            observation_period (tuple, optional): A ``(start, end)`` tuple
                identifying the observation period over which the
                probabilities are computed. Defaults to ``(0, float('Inf'))``.

        Returns:
            dict: A dictionary of states as keys and probabilities as values.

        Raises:
            ValueError: If the observation period is not a positive interval
                above zero.
        """
        start = observation_period[0]
        end = observation_period[1]
        steady_state_dictionary = {}
        prev_date = self.history[0][0]
        prev_state = self.history[0][1]
        date_diff = 0.0

        if start < 0 or end <= start:
            raise ValueError("Observation period need to be a positive interval above zero")

        for event in self.history:
            date = event[0]
            state = event[1]
            if date > end:
                break
            date_diff = self.simulation.nodes[1].increment_time(date, -max(prev_date, start))
            if start < date < end:
                if prev_state not in steady_state_dictionary:
                    steady_state_dictionary[prev_state] = date_diff
                else:
                    steady_state_dictionary[prev_state] += date_diff
            prev_date = date
            prev_state = state

        if end != float("Inf"):
            date_diff = self.simulation.nodes[1].increment_time(end, -prev_date)
        if prev_state not in steady_state_dictionary:
            steady_state_dictionary[prev_state] = date_diff
        else:
            steady_state_dictionary[prev_state] += date_diff

        tot = sum(steady_state_dictionary.values())
        for state in steady_state_dictionary:
            steady_state_dictionary[state] /= tot

        return steady_state_dictionary


class SystemPopulation(StateTracker):
    """Record the number of customers in the system, regardless of node.

    Example:
        3
        This denotes 3 customers in the whole system.
    """

    def initialise(self, simulation):
        """Initialise the state tracker class.

        Args:
            simulation (hciw.Simulation): The simulation being tracked.
        """
        self.simulation = simulation
        self.state = 0
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node, ind):
        """Change the state of the system when a customer is accepted.

        Args:
            node (hciw.Node): The node at which the individual is accepted.
            ind (hciw.Individual): The individual being accepted.
        """
        self.state += 1

    def change_state_block(self, node, destination, ind):
        """Change the state of the system when a customer gets blocked.

        Args:
            node (hciw.Node): The node at which the individual is blocked.
            destination (hciw.Node): The node the individual is blocked from
                entering.
            ind (hciw.Individual): The individual being blocked.
        """
        pass

    def change_state_release(self, node, destination, ind, blocked):
        """Change the state of the system when a customer is released.

        Args:
            node (hciw.Node): The node at which the individual is released.
            destination (hciw.Node): The node the individual was blocked from
                entering.
            ind (hciw.Individual): The individual being released.
            blocked (bool): Whether the individual was blocked.
        """
        self.state -= 1

    def hash_state(self):
        """Return a hashable state.

        Returns:
            int: The number of customers in the system.
        """
        return self.state


class NodePopulation(StateTracker):
    """Record the number of customers at each node.

    Example:
        (3, 1)
        This denotes 3 customers at the first node, and 1 customer at the
        second node.
    """

    def initialise(self, simulation):
        """Initialise the state tracker class.

        Args:
            simulation (hciw.Simulation): The simulation being tracked.
        """
        self.simulation = simulation
        self.state = [0 for i in range(self.simulation.network.number_of_nodes)]
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node, ind):
        """Change the state of the system when a customer is accepted.

        Args:
            node (hciw.Node): The node at which the individual is accepted.
            ind (hciw.Individual): The individual being accepted.
        """
        self.state[node.id_number - 1] += 1

    def change_state_block(self, node, destination, ind):
        """Change the state of the system when a customer gets blocked.

        Args:
            node (hciw.Node): The node at which the individual is blocked.
            destination (hciw.Node): The node the individual is blocked from
                entering.
            ind (hciw.Individual): The individual being blocked.
        """
        pass

    def change_state_release(self, node, destination, ind, blocked):
        """Change the state of the system when a customer is released.

        Args:
            node (hciw.Node): The node at which the individual is released.
            destination (hciw.Node): The node the individual was blocked from
                entering.
            ind (hciw.Individual): The individual being released.
            blocked (bool): Whether the individual was blocked.
        """
        self.state[node.id_number - 1] -= 1

    def hash_state(self):
        """Return a hashable state.

        Returns:
            tuple: The number of customers at each node.
        """
        return tuple(self.state)


class NodePopulationSubset(StateTracker):
    """Record the number of customers at each node in a given set.

    Example:
        (3, 1)
        This denotes 3 customers at the first node, and 1 customer at the
        second node.
    """

    def __init__(self, observed_nodes):
        """Pre-initialise the object with the observed nodes.

        Args:
            observed_nodes (list): The indices of the nodes to observe.
        """
        self.observed_nodes = observed_nodes

    def initialise(self, simulation):
        """Initialise the state tracker class.

        Args:
            simulation (hciw.Simulation): The simulation being tracked.
        """
        self.simulation = simulation
        self.state = [0 for i in self.observed_nodes]
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node, ind):
        """Change the state of the system when a customer is accepted.

        Args:
            node (hciw.Node): The node at which the individual is accepted.
            ind (hciw.Individual): The individual being accepted.
        """
        if node.id_number - 1 in self.observed_nodes:
            state_index = self.observed_nodes.index(node.id_number - 1)
            self.state[state_index] += 1

    def change_state_block(self, node, destination, ind):
        """Change the state of the system when a customer gets blocked.

        Args:
            node (hciw.Node): The node at which the individual is blocked.
            destination (hciw.Node): The node the individual is blocked from
                entering.
            ind (hciw.Individual): The individual being blocked.
        """
        pass

    def change_state_release(self, node, destination, ind, blocked):
        """Change the state of the system when a customer is released.

        Args:
            node (hciw.Node): The node at which the individual is released.
            destination (hciw.Node): The node the individual was blocked from
                entering.
            ind (hciw.Individual): The individual being released.
            blocked (bool): Whether the individual was blocked.
        """
        if node.id_number - 1 in self.observed_nodes:
            state_index = self.observed_nodes.index(node.id_number - 1)
            self.state[state_index] -= 1

    def hash_state(self):
        """Return a hashable state.

        Returns:
            tuple: The number of customers at each observed node.
        """
        return tuple(self.state)


class GroupedNodePopulation(StateTracker):
    """Record the number of customers at each group of nodes.

    Node groups are defined by the user.

    Example:
        (3, 1)
        This denotes 3 customers at the first node group, and 1 customer at
        the second node group.
    """

    def __init__(self, groups):
        """Pre-initialise the object with the observed node groups.

        Args:
            groups (list): A list of node groups, each a list of node indices.
        """
        self.groups = groups
        self.observed_nodes = [nd for group in groups for nd in group] 

    def initialise(self, simulation):
        """Initialise the state tracker class.

        Args:
            simulation (hciw.Simulation): The simulation being tracked.
        """
        self.simulation = simulation
        self.state = [0 for i in self.groups]
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node, ind):
        """Change the state of the system when a customer is accepted.

        Args:
            node (hciw.Node): The node at which the individual is accepted.
            ind (hciw.Individual): The individual being accepted.
        """
        if node.id_number - 1 in self.observed_nodes:
            node_in_group = [(node.id_number - 1) in group for group in self.groups]
            group_index = node_in_group.index(True)
            self.state[group_index] += 1

    def change_state_block(self, node, destination, ind):
        """Change the state of the system when a customer gets blocked.

        Args:
            node (hciw.Node): The node at which the individual is blocked.
            destination (hciw.Node): The node the individual is blocked from
                entering.
            ind (hciw.Individual): The individual being blocked.
        """
        pass

    def change_state_release(self, node, destination, ind, blocked):
        """Change the state of the system when a customer is released.

        Args:
            node (hciw.Node): The node at which the individual is released.
            destination (hciw.Node): The node the individual was blocked from
                entering.
            ind (hciw.Individual): The individual being released.
            blocked (bool): Whether the individual was blocked.
        """
        if node.id_number - 1 in self.observed_nodes:
            node_in_group = [(node.id_number - 1) in group for group in self.groups]
            group_index = node_in_group.index(True)
            self.state[group_index] -= 1

    def hash_state(self):
        """Return a hashable state.

        Returns:
            tuple: The number of customers at each node group.
        """
        return tuple(self.state)


class NodeClassMatrix(StateTracker):
    """Record the number of customers of each class at each node.

    Example:
        ::

            ((3, 1),
             (0, 1))
            This denotes 4 customers at the first node (3 of Class 0, 1 of
            Class 0), and 1 customer at the second node (0 of Class 0, 1 of
            Class 1).
    """

    def __init__(self, class_ordering=None):
        """Pre-initialise the object with the class ordering.

        Args:
            class_ordering (list, optional): The order of the customer
                classes. Defaults to ``None``.
        """
        self.class_ordering: dict = {}
        self._class_ordering_input = class_ordering

    def initialise(self, simulation):
        """Initialise the state tracker class.

        Args:
            simulation (hciw.Simulation): The simulation being tracked.
        """
        self.simulation = simulation

        if self._class_ordering_input is not None:
            self.class_ordering = {clss: i for i, clss in enumerate(self._class_ordering_input)}
        else:
            self.class_ordering = {clss: i for i, clss in enumerate(self.simulation.network.customer_class_names)}

        self.state = [
            [0 for cls in range(self.simulation.network.number_of_classes)]
            for i in range(self.simulation.network.number_of_nodes)
        ]
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node, ind):
        """Change the state of the system when a customer is accepted.

        Args:
            node (hciw.Node): The node at which the individual is accepted.
            ind (hciw.Individual): The individual being accepted.
        """
        self.state[node.id_number - 1][self.class_ordering[ind.customer_class]] += 1

    def change_state_block(self, node, destination, ind):
        """Change the state of the system when a customer gets blocked.

        Args:
            node (hciw.Node): The node at which the individual is blocked.
            destination (hciw.Node): The node the individual is blocked from
                entering.
            ind (hciw.Individual): The individual being blocked.
        """
        pass

    def change_state_release(self, node, destination, ind, blocked):
        """Change the state of the system when a customer is released.

        Args:
            node (hciw.Node): The node at which the individual is released.
            destination (hciw.Node): The node the individual was blocked from
                entering.
            ind (hciw.Individual): The individual being released.
            blocked (bool): Whether the individual was blocked.
        """
        self.state[node.id_number - 1][self.class_ordering[ind.customer_class]] -= 1

    def change_state_classchange(self, node, ind):
        """Change the state of the system when a customer changes class.

        Args:
            node (hciw.Node): The node at which the individual changes class.
            ind (hciw.Individual): The individual changing class.
        """
        self.state[node.id_number - 1][self.class_ordering[ind.previous_class]] -= 1
        self.state[node.id_number - 1][self.class_ordering[ind.customer_class]] += 1

    def hash_state(self):
        """Return a hashable state.

        Returns:
            tuple: The number of customers of each class at each node.
        """
        return tuple(tuple(obs) for obs in self.state)


class NaiveBlocking(StateTracker):
    """Record the number of customers and blocked customers at each node.

    Example:
        ((3, 0), (1, 4))
        This denotes 3 customers at the first node, 0 of which
        are blocked, 5 customers at the second node, 4 of which
        are blocked.
    """

    def initialise(self, simulation):
        """Initialise the naive blocking tracker class.

        Args:
            simulation (hciw.Simulation): The simulation being tracked.
        """
        self.simulation = simulation
        self.state = [[0, 0] for i in range(self.simulation.network.number_of_nodes)]
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node, ind):
        """Change the state of the system when a customer is accepted.

        Args:
            node (hciw.Node): The node at which the individual is accepted.
            ind (hciw.Individual): The individual being accepted.
        """
        self.state[node.id_number - 1][0] += 1

    def change_state_block(self, node, destination, ind):
        """Change the state of the system when a customer gets blocked.

        Args:
            node (hciw.Node): The node at which the individual is blocked.
            destination (hciw.Node): The node the individual is blocked from
                entering.
            ind (hciw.Individual): The individual being blocked.
        """
        self.state[node.id_number - 1][1] += 1
        self.state[node.id_number - 1][0] -= 1

    def change_state_release(self, node, destination, ind, blocked):
        """Change the state of the system when a customer is released.

        Args:
            node (hciw.Node): The node at which the individual is released.
            destination (hciw.Node): The node the individual was blocked from
                entering.
            ind (hciw.Individual): The individual being released.
            blocked (bool): Whether the individual was blocked.
        """
        if blocked:
            self.state[node.id_number - 1][1] -= 1
        else:
            self.state[node.id_number - 1][0] -= 1

    def hash_state(self):
        """Return a hashable state.

        Returns:
            tuple: The number of customers and blocked customers at each node.
        """
        return tuple(tuple(obs) for obs in self.state)


class MatrixBlocking(StateTracker):
    """Record the order and destination of blockages, and node populations.

    The blockages are recorded in the form of a matrix, alongside the number
    of customers at each node.

    Example:
        ::

            ((((1, 4), (2)),
               (3),    ())),
               (5, 8))
            This denotes 5 customers at the first node, 8 customers at the
            second; 2 customers blocked from the first node to the first,
            one from the first node to the second, and one from the second
            node to the first. The numbers denote the order at which they
            became blocked.
    """

    def initialise(self, simulation):
        """Initialise the matrix blocking tracker class.

        Args:
            simulation (hciw.Simulation): The simulation being tracked.
        """
        self.simulation = simulation
        self.state = [
            [
                [
                    [] for i in range(self.simulation.network.number_of_nodes)
                ] for i in range(self.simulation.network.number_of_nodes)
            ],
            [0 for i in range(self.simulation.network.number_of_nodes)],
        ]
        self.increment = 1
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node, ind):
        """Change the state of the system when a customer is accepted.

        Args:
            node (hciw.Node): The node at which the individual is accepted.
            ind (hciw.Individual): The individual being accepted.
        """
        self.state[-1][node.id_number - 1] += 1

    def change_state_block(self, node, destination, ind):
        """Change the state of the system when a customer gets blocked.

        Args:
            node (hciw.Node): The node at which the individual is blocked.
            destination (hciw.Node): The node the individual is blocked from
                entering.
            ind (hciw.Individual): The individual being blocked.
        """
        self.state[0][node.id_number - 1][destination.id_number - 1].append(self.increment)
        self.increment += 1

    def change_state_release(self, node, destination, ind, blocked):
        """Change the state of the system when a customer is released.

        Args:
            node (hciw.Node): The node at which the individual is released.
            destination (hciw.Node): The node the individual was blocked from
                entering.
            ind (hciw.Individual): The individual being released.
            blocked (bool): Whether the individual was blocked.
        """
        if blocked:
            self.state[-1][node.id_number - 1] -= 1
            self.increment -= 1
            position = self.find_blocked_position_and_pop(node, destination)
            self.adjust_positions(position)
        else:
            self.state[-1][node.id_number - 1] -= 1

    def find_blocked_position_and_pop(self, node, destination):
        """Find the position of the next customer to unblock.

        Args:
            node (hciw.Node): The node the individual is blocked at.
            destination (hciw.Node): The node the individual is blocked from
                entering.

        Returns:
            int: The order position of the blocked customer.
        """
        position = self.state[0][node.id_number - 1][destination.id_number - 1].pop(0)
        return position

    def adjust_positions(self, position):
        """Reduce any positions greater than ``position`` by one.

        Loops through the whole matrix.

        Args:
            position (int): The order position that was removed.
        """
        for r in range(len(self.state[0])):
            for c in range(len(self.state[0][r])):
                for o in range(len(self.state[0][r][c])):
                    if self.state[0][r][c][o] > position:
                        self.state[0][r][c][o] -= 1

    def hash_state(self):
        """Return a hashable state.

        Returns:
            tuple: The blockage matrix and the number of customers at each
                node.
        """
        naive = tuple(self.state[-1])
        matrix = tuple(
            tuple(
                tuple(obs for obs in col) for col in row
            ) for row in self.state[0]
        )
        return (matrix, naive)
