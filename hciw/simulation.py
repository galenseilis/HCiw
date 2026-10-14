"""The Simulation engine that drives customers through a network."""

import copy
from decimal import getcontext

import tqdm

from hciw import deadlock, trackers

from .arrival_node import ArrivalNode
from .auxiliary import *
from .exactnode import ExactArrivalNode, ExactNode
from .exit_node import ExitNode
from .individual import Individual
from .node import Node
from .server import Server


class Simulation:
    """The engine that runs a queueing network simulation.

    A ``Simulation`` drives customers through the network's nodes over
    simulated time, collecting data records and tracking state.

    Attributes:
        current_time (float): The current simulated time.
        network (Network): The network being simulated.
        name (str): The name of the simulation.
        NodeTypes (list): The node classes used at each service centre.
        ArrivalNodeType (type): The class used for the arrival node.
        ExitNodeType (type): The class used for the exit node.
        IndividualType (type): The class used for individuals.
        ServerType (type): The class used for servers.
        deadlock_detector (object): The detector used to identify deadlocks.
        inter_arrival_times (dict): Inter-arrival distributions by node and
            class.
        service_times (dict): Service distributions by node and class.
        batch_sizes (dict): Batch size distributions by node and class.
        number_of_priority_classes (int): The number of priority classes.
        transitive_nodes (list): The service centre nodes.
        nodes (list): The arrival, transitive and exit nodes.
        active_nodes (list): The nodes that are not the exit node.
        routers (dict): The routing objects by customer class.
        statetracker (StateTracker): The state tracker in use.
        times_dictionary (dict): Maps hashed states to the time first seen.
        times_to_deadlock (dict): The time from each state to deadlock.
        unchecked_blockage (bool): Whether a blockage needs checking.
    """

    def __init__(
        self,
        network,
        exact=False,
        name="Simulation",
        tracker=None,
        deadlock_detector=None,
        node_class=None,
        arrival_node_class=None,
        exit_node_class=None,
        individual_class=None,
        server_class=None,
    ):
        """Initialise a simulation instance.

        Args:
            network (Network): The network to simulate.
            exact (int, optional): If truthy, use exact ``Decimal`` arithmetic
                with this many digits of precision. Defaults to ``False``.
            name (str, optional): The name of the simulation. Defaults to
                ``"Simulation"``.
            tracker (StateTracker, optional): The state tracker to use.
                Defaults to a plain ``StateTracker``.
            deadlock_detector (object, optional): The deadlock detector to
                use. Defaults to ``deadlock.NoDetection()``.
            node_class (type or list, optional): The node class or classes to
                use. Defaults to ``Node``.
            arrival_node_class (type, optional): The arrival node class to use.
                Defaults to ``ArrivalNode``.
            exit_node_class (type, optional): The exit node class to use.
                Defaults to ``ExitNode``.
            individual_class (type, optional): The individual class to use.
                Defaults to ``Individual``.
            server_class (type, optional): The server class to use. Defaults
                to ``Server``.
        """
        self.current_time = 0.0
        self.network = network
        self.set_classes(
            node_class,
            arrival_node_class,
            exit_node_class,
            individual_class,
            server_class,
        )
        if exact:
            self.NodeTypes = [ExactNode for _ in range(network.number_of_nodes)]
            self.ArrivalNodeType = ExactArrivalNode
            getcontext().prec = exact

        self.name = name
        self.deadlock_detector = (
            deadlock.NoDetection() if deadlock_detector is None else deadlock_detector
        )
        self.inter_arrival_times = self.find_arrival_dists()
        self.service_times = self.find_service_dists()
        self.batch_sizes = self.find_batching_dists()
        self.show_simulation_to_distributions()
        self.number_of_priority_classes = self.network.number_of_priority_classes
        self.transitive_nodes = [
            node_type(i + 1, self) for i, node_type in enumerate(self.NodeTypes)
        ]
        self.exit_node = self.ExitNodeType()
        self.nodes = (
            [self.ArrivalNodeType(self), *self.transitive_nodes, self.exit_node]
        )
        self.active_nodes = self.nodes[:-1]
        self.routers = self.find_and_initialise_routers()
        self.nodes[0].initialise()
        if tracker is None:
            self.statetracker = trackers.StateTracker()
        else:
            self.statetracker = tracker
        self.statetracker.initialise(self)
        self.times_dictionary = {self.statetracker.hash_state(): 0.0}
        self.times_to_deadlock = {}
        self.unchecked_blockage = False

    def __repr__(self):
        """Return the name of the simulation.

        Returns:
            str: The simulation's name.
        """
        return self.name

    @property
    def number_of_individuals(self):
        """Return the number of individuals currently in the system.

        Returns:
            int: The number of individuals currently in the system.
        """
        return (self.nodes[0].number_of_individuals - 1) - self.nodes[
            -1
        ].number_of_individuals

    def find_arrival_dists(self):
        """Create the arrival time distribution objects for each node and class.

        Returns:
            dict: Arrival time distributions keyed by node and customer class.
        """
        return {
            node + 1: {
                clss: copy.deepcopy(
                    self.network.customer_classes[clss].arrival_distributions[node]
                )
                for clss in self.network.customer_class_names
            }
            for node in range(self.network.number_of_nodes)
        }

    def find_service_dists(self):
        """Create the service time distribution objects for each node and class.

        Returns:
            dict: Service time distributions keyed by node and customer class.
        """
        return {
            node + 1: {
                clss: copy.deepcopy(
                    self.network.customer_classes[clss].service_distributions[node]
                )
                for clss in self.network.customer_class_names
            }
            for node in range(self.network.number_of_nodes)
        }

    def find_batching_dists(self):
        """Create the batch size distribution objects for each node and class.

        Returns:
            dict: Batch size distributions keyed by node and customer class.
        """
        return {
            node + 1: {
                clss: copy.deepcopy(
                    self.network.customer_classes[clss].batching_distributions[node]
                )
                for clss in self.network.customer_class_names
            }
            for node in range(self.network.number_of_nodes)
        }

    def show_simulation_to_distributions(self):
        """Add the simulation as an attribute of the distribution objects."""
        for clss in self.network.customer_class_names:
            for nd in range(self.network.number_of_nodes):
                if self.inter_arrival_times[nd + 1][clss] is not None:
                    self.inter_arrival_times[nd + 1][clss].simulation = self
                    self.service_times[nd + 1][clss].simulation = self
                    self.batch_sizes[nd + 1][clss].simulation = self

    def find_and_initialise_routers(self):
        """Initialise and return the routing objects.

        Returns:
            dict: Routing objects keyed by customer class.
        """
        routers_dict = {}
        for clss in self.network.customer_class_names:
            routers_dict[clss] = self.network.customer_classes[clss].routing
            routers_dict[clss].initialise(self)
        return routers_dict

    def find_next_active_node(self):
        """Return the active node with the earliest next event date.

        If several nodes share the earliest date, one is chosen at random.

        Returns:
            Node: The next active node.
        """
        mindate = float("Inf")
        next_active_nodes = []
        for nd in self.active_nodes:
            if nd.next_event_date < mindate:
                mindate = nd.next_event_date
                next_active_nodes = [nd]
            elif nd.next_event_date == mindate:
                next_active_nodes.append(nd)
        if len(next_active_nodes) > 1:
            return random_choice(next_active_nodes)
        return next_active_nodes[0]

    def get_all_individuals(self):
        """Return all individuals with at least one data record.

        Returns:
            list: The individuals with at least one data record.
        """
        return [
            individual
            for node in [*self.transitive_nodes, self.exit_node]
            for individual in node.all_individuals
        ]

    def get_all_records(
        self,
        only=None,
        include_incomplete=False,
    ):
        """Get data records from all individuals.

        Args:
            only (list, optional): The record types to include. Defaults to
                service, baulk, rejection, renege and interrupted service
                records.
            include_incomplete (bool, optional): Whether to include records
                for individuals still in the system. Defaults to ``False``.

        Returns:
            list: The collected data records.
        """
        if only is None:
            only = ["service", "baulk", "rejection", "renege", "interrupted service"]
        records = []
        for individual in self.get_all_individuals():
            for record in individual.data_records:
                if record.record_type in only:
                    records.append(record)
            if include_incomplete and individual.node != -1:
                incomplete_record = self.nodes[
                    individual.node
                ].write_incomplete_record(individual)
                records.append(incomplete_record)
        self.all_records = records
        return records

    def set_classes(
        self,
        node_class,
        arrival_node_class,
        exit_node_class,
        individual_class,
        server_class,
    ):
        """Set the node, individual and server classes used by the simulation.

        Args:
            node_class (type or list): The node class or classes to use. If a
                list, it must have one entry per node.
            arrival_node_class (type): The arrival node class to use, or
                ``None`` for the default.
            exit_node_class (type): The exit node class to use, or ``None``
                for the default.
            individual_class (type): The individual class to use, or ``None``
                for the default.
            server_class (type): The server class to use, or ``None`` for the
                default.

        Raises:
            ValueError: If ``node_class`` is a list whose length does not match
                the number of nodes.
        """
        if arrival_node_class is not None:
            self.ArrivalNodeType = arrival_node_class
        else:
            self.ArrivalNodeType = ArrivalNode

        if exit_node_class is not None:
            self.ExitNodeType = exit_node_class
        else:
            self.ExitNodeType = ExitNode

        if node_class is not None:
            if not isinstance(node_class, list):
                self.NodeTypes = [
                    node_class for _ in range(self.network.number_of_nodes)
                ]
            else:
                if len(node_class) != self.network.number_of_nodes:
                    raise ValueError(
                        "Ensure consistant number of nodes is used throughout."
                    )
                self.NodeTypes = node_class
        else:
            self.NodeTypes = [Node for _ in range(self.network.number_of_nodes)]

        if individual_class is not None:
            self.IndividualType = individual_class
        else:
            self.IndividualType = Individual

        if server_class is not None:
            self.ServerType = server_class
        else:
            self.ServerType = Server

    def event_and_return_nextnode(self, next_active_node):
        """Carry out an event and return the next active node.

        Args:
            next_active_node (Node): The node whose event to carry out.

        Returns:
            Node: The next active node.
        """
        next_active_node.have_event()
        for node in self.transitive_nodes:
            node.update_next_event_date()
        return self.find_next_active_node()

    def simulate_until_deadlock(self):
        """Run the simulation until deadlock is reached."""
        deadlocked = False
        next_active_node = self.find_next_active_node()
        self.current_time = next_active_node.next_event_date
        time_of_deadlock = self.current_time
        while not deadlocked:
            next_active_node = self.event_and_return_nextnode(next_active_node)
            current_state = self.statetracker.hash_state()
            if current_state not in self.times_dictionary:
                self.times_dictionary[current_state] = self.current_time
            if self.unchecked_blockage:
                deadlocked = self.deadlock_detector.detect_deadlock()
                self.unchecked_blockage = False
            if deadlocked:
                time_of_deadlock = self.current_time
            self.current_time = next_active_node.next_event_date

        self.wrap_up_servers(time_of_deadlock)
        self.times_to_deadlock = {
            state: time_of_deadlock - self.times_dictionary[state]
            for state in self.times_dictionary
        }

    def simulate_until_max_time(self, max_simulation_time, progress_bar=False):
        """Run the simulation until a maximum simulated time is reached.

        Args:
            max_simulation_time (float): The time to stop the simulation at.
            progress_bar (bool, optional): Whether to display a progress bar.
                Defaults to ``False``.
        """
        next_active_node = self.find_next_active_node()
        self.current_time = next_active_node.next_event_date

        if progress_bar:
            self.progress_bar = tqdm.tqdm(total=max_simulation_time)

        while self.current_time < max_simulation_time:
            next_active_node = self.event_and_return_nextnode(next_active_node)
            self.statetracker.timestamp()

            if progress_bar:
                remaining_time = max_simulation_time - self.progress_bar.n
                time_increment = next_active_node.next_event_date - self.current_time
                self.progress_bar.update(min(time_increment, remaining_time))

            self.current_time = next_active_node.next_event_date
        self.current_time = max_simulation_time

        self.wrap_up_servers(max_simulation_time)
        if progress_bar:
            remaining_time = max(max_simulation_time - self.progress_bar.n, 0)
            self.progress_bar.update(remaining_time)
            self.progress_bar.close()

    def simulate_until_max_customers(
        self, max_customers, progress_bar=False, method="Complete"
    ):
        """Run the simulation until a number of customers is reached.

        Args:
            max_customers (int): The number of customers to stop at.
            progress_bar (bool, optional): Whether to display a progress bar.
                Defaults to ``False``.
            method (str, optional): The measure used to count customers. One
                of:

                - ``'Complete'``: count customers that reach the Exit Node
                  after completing their journey.
                - ``'Finish'``: count customers that reach the Exit Node,
                  whether or not they completed their journey (including
                  baulkers and renegers).
                - ``'Arrive'``: count customers spawned at the Arrival Node.
                - ``'Accept'``: count customers spawned and accepted (not
                  rejected) at the Arrival Node.

                Defaults to ``'Complete'``.

        Raises:
            ValueError: If ``method`` is not one of the valid options.
        """
        next_active_node = self.find_next_active_node()
        self.current_time = next_active_node.next_event_date

        if progress_bar:
            self.progress_bar = tqdm.tqdm(total=max_customers)

        if method == "Complete":
            def check():
                return self.exit_node.number_of_completed_individuals
        elif method == "Finish":
            def check():
                return self.exit_node.number_of_individuals
        elif method == "Arrive":
            def check():
                return self.nodes[0].number_of_individuals
        elif method == "Accept":
            def check():
                return self.nodes[0].number_accepted_individuals
        else:
            raise ValueError("Invalid 'method' for 'simulate_until_max_customers'.")

        previous_time = self.current_time
        while check() < max_customers:
            old_check = check()
            next_active_node = self.event_and_return_nextnode(next_active_node)
            self.statetracker.timestamp()

            if progress_bar:
                remaining_time = max_customers - self.progress_bar.n
                time_increment = check() - old_check
                self.progress_bar.update(min(time_increment, remaining_time))

            previous_time = self.current_time
            self.current_time = next_active_node.next_event_date
        self.current_time = previous_time

        self.wrap_up_servers(self.current_time)

        if progress_bar:
            remaining_time = max(max_customers - self.progress_bar.n, 0)
            self.progress_bar.update(remaining_time)
            self.progress_bar.close()

    def wrap_up_servers(self, current_time):
        """Update server times and find the overall server utilisation.

        Updates each server's total time and busy time at the end of the
        simulation run, and finds the overall server utilisation for each node.

        Args:
            current_time (float): The time at which the run finished.
        """
        for nd in self.transitive_nodes:
            nd.wrap_up_servers(current_time)
            nd.find_server_utilisation()
