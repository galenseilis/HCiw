"""Limited processor-sharing node."""

from .node import Node


class PSNode(Node):
    """Represent a limited processor-sharing node.

    In processor-sharing systems the service load is shared equally between
    all customers at the node. While there are ``x`` customers present, the
    service slows down ``x``-fold, so the service time increases ``x``-fold.

    ``number_of_servers`` represents the node capacity, the maximum number of
    customers allowed to share the service load at a time. Customers arriving
    when the node is overcapacity wait in line.
    """

    def __init__(self, id_, simulation):
        """Initialise the node.

        Differs from `Node` by setting ``last_occupancy`` to 0, required to
        calculate service times for the current period, setting
        ``ps_capacity`` to the node capacity, and setting ``c`` to infinity,
        as within capacity the code logic behaves more like an infinite
        server queue.

        Args:
            id_ (int): Identifier for the node.
            simulation (object): The simulation to which this node belongs.
        """
        self.last_occupancy = 0
        super().__init__(id_, simulation)
        self.ps_threshold = self.simulation.network.service_centres[id_ - 1].ps_threshold
        self.ps_capacity = self.c
        self.c = float("inf")

    def update_all_service_end_dates(self):
        """Update projected service end dates for customers in service.

        For each individual receiving service, calculates the projected end
        service dates if the system state remains constant.
        """
        next_occupancy = min(self.number_of_individuals, self.ps_capacity)
        inds_in_service = [ind for ind in self.all_individuals if ind.with_server]
        for ind in inds_in_service:
            current_period = self.simulation.current_time - ind.date_last_update
            if self.last_occupancy > 0:
                share_completed = (self.ps_threshold * current_period) / max(self.last_occupancy, self.ps_threshold)
            else:
                share_completed = 0
            ind.time_left -= share_completed
            ind.service_end_date = self.simulation.current_time + ((ind.time_left * max(next_occupancy, self.ps_threshold)) / self.ps_threshold)
            ind.date_last_update = self.simulation.current_time

        self.last_occupancy = next_occupancy
        self.date_last_update = self.simulation.current_time

    def begin_service_if_possible_accept(self, next_individual):
        """Begin service for an individual at the acceptance point.

        Gives an arrival date and service time, gives a start date and a
        service time to complete if there is free capacity, marks the
        individual as 'with server', and updates all customers' service
        times.

        Args:
            next_individual (Individual): The individual to serve.
        """
        next_individual.arrival_date = self.now
        next_individual.with_server = False
        if self.number_of_individuals <= self.ps_capacity:
            next_individual.service_start_date = self.now
            next_individual.date_last_update = self.now
            next_individual.service_time = self.get_service_time(next_individual)
            next_individual.time_left = next_individual.service_time
            next_individual.with_server = True
            self.update_all_service_end_dates()

    def begin_service_if_possible_release(self, ind=None, server=None):
        """Begin service for an individual at a release point.

        Checks for individuals waiting for capacity, gives a start date and
        'last update' date, samples a service time and uses it as the time
        left, and updates all customers' service times.

        Args:
            ind (Individual): The individual being released.
            server (Server): The server freed by the release.
        """
        if self.number_of_individuals >= self.ps_capacity:
            ind = self.all_individuals[self.ps_capacity - 1]
            ind.service_start_date = self.now
            ind.date_last_update = self.now
            ind.service_time = self.get_service_time(ind)
            ind.time_left = ind.service_time
            ind.with_server = True
        self.update_all_service_end_dates()
