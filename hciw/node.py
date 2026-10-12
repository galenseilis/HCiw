"""Transient node of the queueing network."""

from random import random
from math import isinf, nan
import networkx as nx
from .auxiliary import random_choice, flatten_list
from .data_record import DataRecord
from .server import Server
from .schedules import *


class Node(object):
    """Represent a node in the queueing network.

    The node holds a queue of individuals and, where applicable, the
    servers that process them.
    """

    def __init__(self, id_, simulation):
        """Initialise a node.

        Args:
            id_ (int): Identifier for the node.
            simulation (object): The simulation to which this node belongs.
        """
        self.simulation = simulation
        node = self.simulation.network.service_centres[id_ - 1]
        self.server_priority_function = node.server_priority_function
        self.service_discipline = node.service_discipline
        self.next_event_type = None
        if isinstance(node.number_of_servers, Schedule):
            self.schedule = node.number_of_servers
            self.schedule.initialise()
            self.c = self.schedule.c
            if self.schedule.schedule_type == 'slotted':
                self.slotted = True
                self.next_event_date = self.schedule.next_slot_date
                self.next_event_type = 'slotted_service'
            else:
                self.slotted = False
                self.next_event_date = self.schedule.next_shift_change_date
                self.next_shift_change = self.schedule.next_shift_change_date
                self.next_event_type = 'shift_change'
        else:
            self.c = node.number_of_servers
            self.schedule = None
            self.slotted = False
            self.next_event_date = float("Inf")
            self.next_shift_change = float("Inf")
        self.node_capacity = node.queueing_capacity + self.c
        self.class_change = node.class_change_matrix
        self.individuals = [[] for _ in range(simulation.number_of_priority_classes)]
        self.number_of_individuals = 0
        self.number_in_service = 0
        self.id_number = id_
        self.baulking_functions = {
            clss: self.simulation.network.customer_classes[clss].baulking_functions[id_ - 1]
            for clss in self.simulation.network.customer_class_names
        }
        self.overtime = []
        self.blocked_queue = []
        self.len_blocked_queue = 0
        if not isinf(self.c):
            self.servers = self.create_starting_servers()
        self.highest_id = self.c
        self.simulation.deadlock_detector.initialise_at_node(self)
        self.priority_preempt = node.priority_preempt
        self.interrupted_individuals = []
        self.number_interrupted_individuals = 0
        self.all_servers_total = []
        self.all_servers_busy = []
        self.reneging = node.reneging
        self.dynamic_classes = node.class_change_time
        self.next_class_change_date = float("Inf")
        self.next_individual = None

    @property
    def now(self):
        """Get the current simulation time.

        Returns:
            float: The current simulation time.
        """
        return self.simulation.current_time

    @property
    def all_individuals(self):
        """Get all individuals currently at the node.

        Returns:
            list: Every individual at the node, across all priority classes.
        """
        if self.simulation.number_of_priority_classes == 1:
            return self.individuals[0]
        return flatten_list(self.individuals)

    def __repr__(self):
        """Return a string representation of the node.

        Returns:
            str: The representation of the node.
        """
        return "Node %s" % self.id_number

    def accept(self, next_individual, completed=False):
        """Accept a new individual into the queue.

        Removes any previous exit date and blockage status, begins service
        if possible, records arrival information, and updates the state
        tracker.

        Args:
            next_individual (Individual): The individual to accept.
            completed (bool): Whether the individual has completed service.
        """
        next_individual.node = self.id_number
        next_individual.exit_date = False
        next_individual.is_blocked = False
        next_individual.original_class = next_individual.customer_class
        next_individual.queue_size_at_arrival = self.number_of_individuals
        self.individuals[next_individual.priority_class].append(next_individual)
        self.number_of_individuals += 1
        self.begin_service_if_possible_accept(next_individual)
        self.simulation.statetracker.change_state_accept(self, next_individual)

    def add_new_servers(self, num_servers):
        """Add the appropriate number of servers for the given shift.

        Args:
            num_servers (int): The number of servers to add.
        """
        for i in range(num_servers):
            self.highest_id += 1
            self.servers.append(self.simulation.ServerType(self, self.highest_id, self.now))

    def attach_server(self, server, individual):
        """Attach a server to an individual, and vice versa.

        Args:
            server (Server): The server to attach.
            individual (Individual): The individual to attach.
        """
        server.cust = individual
        server.busy = True
        individual.server = server
        self.simulation.deadlock_detector.action_at_attach_server(self, server, individual)

    def begin_service_if_possible_accept(self, next_individual):
        """Begin service for an individual at the acceptance point.

        Sets the arrival date to the current time, and if a server is free
        or there are infinitely many servers, attaches the server, gets the
        service start time, service time and service end time, and updates
        the server's end date.

        Args:
            next_individual (Individual): The individual to serve.
        """
        next_individual.arrival_date = self.now
        if self.reneging is True:
            next_individual.reneging_date = self.get_reneging_date(next_individual)
        self.decide_class_change(next_individual)

        if isinf(self.c):
            ind = next_individual
        else:
            ind = self.choose_next_customer()

        if ind is not None:
            free_server = self.find_free_server(ind)
            if free_server is None and isinf(self.c) is False and self.c > 0:
                self.decide_preempt(ind)
            if free_server is not None or isinf(self.c):
                if isinf(self.c) is False:
                    self.attach_server(free_server, ind)
                ind.service_start_date = self.now
                ind.service_time = self.get_service_time(ind)
                ind.service_end_date = self.now + ind.service_time
                self.number_in_service += 1
                self.reset_class_change(ind)
                if not isinf(self.c):
                    free_server.next_end_service_date = ind.service_end_date

    def begin_interrupted_individuals_service(self, srvr):
        """Restart an interrupted individual's service.

        The individual's service time is resampled.

        Args:
            srvr (Server): The server to give to the individual.
        """
        ind = [i for i in self.interrupted_individuals][0]
        if ind.is_blocked:
            node_blocked_to = self.simulation.nodes[ind.destination]
            ind.destination = False
            node_blocked_to.blocked_queue.remove((self.id_number, ind.id_number))
            node_blocked_to.len_blocked_queue -= 1
            ind.is_blocked = False
        self.attach_server(srvr, ind)
        self.give_service_time_after_preemption(ind)
        ind.service_start_date = self.now
        ind.service_end_date = self.now + ind.service_time
        ind.interrupted = False
        self.number_in_service += 1
        srvr.next_end_service_date = ind.service_end_date
        self.interrupted_individuals.remove(ind)
        self.number_interrupted_individuals -= 1

    def begin_service_if_possible_change_shift(self):
        """Begin service for customers after a shift change.

        If there are free servers, restarts interrupted customers' services
        and begins service for any waiting customers by giving a start date
        and end date and attaching servers to individuals.
        """
        free_servers = [s for s in self.servers if not s.busy]
        for srvr in free_servers:
            if self.number_interrupted_individuals > 0:
                self.begin_interrupted_individuals_service(srvr)
            else:
                ind = self.choose_next_customer()
                if ind is not None:
                    self.attach_server(srvr, ind)
                    ind.service_start_date = self.now
                    self.give_individual_a_service_time(ind)
                    ind.service_end_date = self.increment_time(ind.service_start_date, ind.service_time)
                    self.number_in_service += 1
                    self.reset_class_change(ind)
                    srvr.next_end_service_date = ind.service_end_date

    def begin_service_if_possible_release(self, next_individual, newly_free_server):
        """Begin service for an individual after a release.

        Checks for interrupted individuals left to restart service, then
        gives an arrival date and service time, gives a start date and end
        date, and attaches the server to the individual.

        Args:
            next_individual (Individual): The individual being released.
            newly_free_server (Server): The server freed by the release.
        """

        if newly_free_server is not None and newly_free_server in self.servers:
            if self.number_interrupted_individuals > 0:
                self.begin_interrupted_individuals_service(newly_free_server)
            else:
                ind = self.choose_next_customer()
                if ind is not None:
                    self.attach_server(newly_free_server, ind)
                    ind.service_start_date = self.now
                    self.give_individual_a_service_time(ind)
                    ind.service_end_date = self.increment_time(ind.service_start_date, ind.service_time)
                    self.number_in_service += 1
                    self.reset_class_change(ind)
                    newly_free_server.next_end_service_date = ind.service_end_date

    def block_individual(self, individual, next_node):
        """Block an individual from entering the next node.

        Changes the blocked status, updates the state tracker, adds
        information to the next node's blocked queue, and updates the
        deadlock detector, informing the simulation that there are unchecked
        blockages for deadlock detection.

        Args:
            individual (Individual): The individual being blocked.
            next_node (Node): The node the individual is blocked from
                entering.
        """
        individual.is_blocked = True
        self.simulation.statetracker.change_state_block(self, next_node, individual)
        next_node.blocked_queue.append((self.id_number, individual.id_number))
        next_node.len_blocked_queue += 1
        self.simulation.deadlock_detector.action_at_blockage(individual, next_node)
        self.simulation.unchecked_blockage = True

    def change_customer_class(self, individual):
        """Change an individual's customer class.

        The new class is chosen according to a probability distribution.

        Args:
            individual (Individual): The individual whose class changes.
        """
        if self.class_change:
            individual.previous_class = individual.customer_class
            individual.customer_class = random_choice(
                self.simulation.network.customer_class_names,
                [self.class_change[individual.previous_class][clss_name] for clss_name in self.simulation.network.customer_class_names],
            )
            individual.prev_priority_class = individual.priority_class
            individual.priority_class = self.simulation.network.priority_class_mapping[individual.customer_class]

    def change_customer_class_while_waiting(self):
        """Change the next queued individual's class while waiting.

        The individual is moved between priority queues and preemption is
        decided if the priority class changes.
        """
        changing_individual = self.next_individual
        changing_individual.customer_class = changing_individual.next_class
        changing_individual.priority_class = self.simulation.network.priority_class_mapping[changing_individual.next_class]
        if changing_individual.priority_class != changing_individual.prev_priority_class:
            self.change_priority_queue(changing_individual)
            self.decide_preempt(changing_individual)
        self.simulation.statetracker.change_state_classchange(self, changing_individual)
        changing_individual.previous_class = changing_individual.next_class
        changing_individual.prev_priority_class = changing_individual.priority_class
        self.decide_class_change(changing_individual)

    def change_priority_queue(self, individual):
        """Move an individual to their new priority queue.

        Args:
            individual (Individual): The individual to move.
        """
        self.individuals[individual.prev_priority_class].remove(individual)
        self.individuals[individual.priority_class].append(individual)

    def change_shift(self):
        """Implement a server shift change.

        Adds or deletes servers, or indicates which servers should go off
        duty, and begins any new services if there are free servers.
        """
        self.schedule.get_next_shift()
        self.next_shift_change = self.schedule.next_shift_change_date
        self.c = self.schedule.c
        self.take_servers_off_duty(preemption=self.schedule.preemption)
        self.add_new_servers(self.schedule.c)
        self.begin_service_if_possible_change_shift()

    def find_number_of_slotted_services(self):
        """Find the number of slotted services to start in this slot.

        Returns:
            int: The number of services to start.
        """
        if self.schedule.capacitated:
            return min(max(self.schedule.slot_size - self.number_in_service, 0), self.number_of_individuals)
        return min(self.schedule.slot_size, self.number_of_individuals)

    def interrupt_slotted_services(self):
        """Interrupt services when there is not enough slot capacity.

        Finds the customers whose slotted services need to be interrupted
        because of insufficient capacity at the current slot, and interrupts
        their services.
        """
        if self.schedule.capacitated and self.schedule.preemption is not False:
            number_to_interrupt = self.number_in_service - self.schedule.slot_size
            if number_to_interrupt > 0:
                inds_to_interrupt = sorted(
                    [ind for ind in self.all_individuals if ind.service_start_date is not False],
                    key=lambda x: (x.priority_class, x.arrival_date),
                    reverse=True
                )[:number_to_interrupt]
                for ind in inds_to_interrupt:
                    self.interrupt_service(ind)

    def slotted_service(self):
        """Serve a set number of customers at the current time.

        Only the number of customers allowed by the current slot may have
        service at the exact time the method is called.
        """
        number_of_slotted_services = self.find_number_of_slotted_services()
        self.interrupt_slotted_services()
        for i in range(number_of_slotted_services):
            if self.number_interrupted_individuals > 0:
                ind = self.interrupted_individuals[0]
                self.interrupted_individuals.remove(ind)
                self.number_interrupted_individuals -= 1
            else:
                ind = self.choose_next_customer()
            if ind is not None:
                ind.service_start_date = self.now
                self.give_individual_a_service_time(ind)
                ind.service_end_date = self.now + ind.service_time
                ind.server = True
                self.number_in_service += 1
                self.reset_class_change(ind)
        self.schedule.get_next_slot()

    def choose_next_customer(self):
        """Choose which customer will be next to be served.

        Returns:
            Individual: The customer chosen by the service discipline, or
                None if no customer is waiting.
        """
        for priority_individuals in self.individuals:
            waiting_individuals = [ind for ind in priority_individuals if not ind.server]
            if len(waiting_individuals) > 0:
                return self.service_discipline(waiting_individuals, self.now)

    def create_starting_servers(self):
        """Initialise the servers.

        Returns:
            list: The newly created starting servers.
        """
        return [self.simulation.ServerType(self, i + 1, 0.0) for i in range(self.c)]

    def decide_class_change(self, next_individual):
        """Decide the next class and class change date for an individual.

        Args:
            next_individual (Individual): The individual to update.
        """
        if self.dynamic_classes is True:
            next_time = float('inf')
            next_class = next_individual.customer_class
            for clss, dist in self.simulation.network.customer_classes[next_individual.customer_class].class_change_time_distributions.items():
                if dist is not None:
                    t = dist.sample()
                    if t < next_time:
                        next_time = t
                        next_class = clss
            next_individual.next_class = next_class
            next_individual.class_change_date = self.increment_time(self.now, next_time)
            self.find_next_class_change()

    def decide_preempt(self, individual):
        """Decide whether priority preemption is needed.

        If needed, finds the individual to preempt and preempts them.

        Args:
            individual (Individual): The individual seeking service.
        """
        if self.priority_preempt != False:
            least_priority = max(s.cust.priority_class for s in self.servers)
            if individual.priority_class < least_priority:
                least_prioritised_individuals = [
                    s.cust
                    for s in self.servers
                    if s.cust.priority_class == least_priority
                ]
                individual_to_preempt = max(
                    [ind for ind in least_prioritised_individuals],
                    key=lambda cust: cust.service_start_date,
                )
                self.preempt(individual_to_preempt, individual)

    def detatch_server(self, server, individual):
        """Detach a server from an individual, and vice versa.

        Args:
            server (Server): The server to detach.
            individual (Individual): The individual to detach.
        """
        self.simulation.deadlock_detector.action_at_detatch_server(server)
        server.cust = False
        server.busy = False
        individual.server = False
        server.busy_time = self.increment_time(server.busy_time, individual.exit_date - individual.service_start_date)
        server.total_time = self.now - server.start_date
        if server.offduty:
            self.kill_server(server)

    def find_free_server(self, ind):
        """Find a free server.

        Args:
            ind (Individual): The individual needing a server.

        Returns:
            Server: A free server, or None if none is available.
        """
        if isinf(self.c):
            return None

        if self.server_priority_function is None:
            all_servers = self.servers
        else:
            all_servers = sorted(self.servers, key=lambda srv: self.server_priority_function(srv, ind))

        for svr in all_servers:
            if not svr.busy:
                return svr
        return None

    def decide_between_simultaneous_individuals(self):
        """Find the next individual that should now finish service.

        Returns:
            Individual: A randomly chosen individual when several finish at
                the same time.
        """
        if len(self.next_individual) > 1:
            next_individual = random_choice(self.next_individual)
        else:
            next_individual = self.next_individual[0]
        return next_individual

    def find_next_class_change(self):
        """Update the next class change date and individual."""
        self.next_class_change_date = float('inf')
        self.next_class_change_ind = None
        for ind in self.all_individuals:
            if (ind.class_change_date < self.next_class_change_date) and not ind.server:
                next_class_change = (ind, ind.class_change_date)
                self.next_class_change_ind = ind
                self.next_class_change_date = ind.class_change_date

    def find_server_utilisation(self):
        """Find the overall server utilisation for the node."""
        if isinf(self.c) or self.c == 0:
            self.server_utilisation = None
        else:
            for server in self.servers:
                self.all_servers_total.append(server.total_time)
                self.all_servers_busy.append(server.busy_time)
            self.server_utilisation = sum(self.all_servers_busy) / sum(self.all_servers_total)

    def finish_service(self):
        """Finish the service of the next individual.

        Finds the individual to finish service, checks whether they need to
        change class, finds their next node, and releases the individual if
        there is capacity at the destination, otherwise causes blockage.
        """
        next_individual = self.decide_between_simultaneous_individuals()
        self.change_customer_class(next_individual)
        next_node = self.next_node(next_individual)
        next_individual.destination = next_node.id_number
        if not isinf(self.c) and self.c > 0:
            next_individual.server.next_end_service_date = float("Inf")
        if next_node.number_of_individuals < next_node.node_capacity:
            self.release(next_individual, next_node)
        else:
            self.block_individual(next_individual, next_node)

    def give_individual_a_service_time(self, individual):
        """Give a service time to an individual.

        Either a new service time, or a service time after pre-emption.

        Args:
            individual (Individual): The individual to serve.
        """
        if individual.service_time is False:
            individual.service_time = self.get_service_time(individual)
        else:
            self.give_service_time_after_preemption(individual)


    def give_service_time_after_preemption(self, individual):
        """Give a service time after preemption.

        Either resamples, restarts, or resumes service time from where it was
        left off.

        Args:
            individual (Individual): The individual to serve.
        """
        if individual.service_time == "resample":
            individual.service_time = self.get_service_time(individual)
        if individual.service_time == "restart":
            individual.service_time = individual.original_service_time
        if individual.service_time == "resume":
            individual.service_time = individual.time_left

    def have_event(self):
        """Trigger the node's next event."""
        if self.next_event_type == 'end_service':
            self.finish_service()
        elif self.next_event_type == 'shift_change':
            self.change_shift()
        elif self.next_event_type == 'renege':
            self.renege()
        elif self.next_event_type == 'class_change':
            self.change_customer_class_while_waiting()
        elif self.next_event_type == 'slotted_service':
            self.slotted_service()

    def increment_time(self, original, increment):
        """Increment the original time by the increment.

        Args:
            original (float): The original time.
            increment (float): The amount to add.

        Returns:
            The incremented time.
        """
        return original + increment

    def kill_server(self, srvr):
        """Kill a server when it goes off duty.

        Args:
            srvr (Server): The server to remove.
        """
        srvr.total_time = self.increment_time(self.next_event_date, -srvr.start_date)
        self.overtime.append(self.increment_time(self.next_event_date, -srvr.shift_end))
        self.all_servers_busy.append(srvr.busy_time)
        self.all_servers_total.append(srvr.total_time)
        indx = self.servers.index(srvr)
        del self.servers[indx]

    def next_node(self, ind):
        """Find the next node according to the routing method.

        Args:
            ind (Individual): The individual being routed.

        Returns:
            Node: The next node.
        """
        return self.simulation.routers[ind.customer_class].next_node(ind, self.id_number)

    def next_node_for_rerouting(self, ind):
        """Find the next node for rerouting according to the routing method.

        Args:
            ind (Individual): The individual being rerouted.

        Returns:
            Node: The next node for rerouting.
        """
        return self.simulation.routers[ind.customer_class].next_node_for_rerouting(ind, self.id_number)

    def next_node_for_jockeying(self, ind):
        """Find the next node for jockeying according to the routing method.

        Args:
            ind (Individual): The jockeying individual.

        Returns:
            Node: The next node for jockeying.
        """
        return self.simulation.routers[ind.customer_class].next_node_for_jockeying(ind, self.id_number)

    def preempt(self, individual_to_preempt, next_individual):
        """Preempt an individual and replace them in service.

        Args:
            individual_to_preempt (Individual): The individual removed from
                service.
            next_individual (Individual): The individual taking their place.
        """
        server = individual_to_preempt.server
        individual_to_preempt.original_service_time = individual_to_preempt.service_time
        if self.priority_preempt == 'reroute':
            self.reroute(individual_to_preempt)
        else:
            self.write_interruption_record(individual_to_preempt)
            individual_to_preempt.service_start_date = False
            individual_to_preempt.time_left = individual_to_preempt.service_end_date - self.now
            individual_to_preempt.service_time = self.priority_preempt
            individual_to_preempt.service_end_date = False
            self.detatch_server(server, individual_to_preempt)
            self.decide_class_change(individual_to_preempt)
        self.attach_server(server, next_individual)
        next_individual.service_start_date = self.now
        next_individual.service_time = self.get_service_time(next_individual)
        next_individual.service_end_date = self.now + next_individual.service_time
        self.reset_class_change(next_individual)
        server.next_end_service_date = next_individual.service_end_date

    def release(self, next_individual, next_node, reroute=False):
        """Release an individual from the node.

        Removes the individual from the queue, records relevant information,
        detaches the server, updates the state tracker, begins service of any
        waiting customers, sends the individual to their next destination, and
        releases any individuals blocked by this node.

        Args:
            next_individual (Individual): The individual to release.
            next_node (Node): The node receiving the individual.
            reroute (bool): Whether the release is due to rerouting.
        """
        self.individuals[next_individual.prev_priority_class].remove(next_individual)
        self.number_of_individuals -= 1
        self.number_in_service -= 1
        next_individual.queue_size_at_departure = self.number_of_individuals
        next_individual.exit_date = self.now
        if not reroute:
            self.write_individual_record(next_individual)
        newly_free_server = None
        if not isinf(self.c) and not self.slotted:
            newly_free_server = next_individual.server
            self.detatch_server(newly_free_server, next_individual)
        if self.slotted:
            next_individual.server = False
        self.reset_individual_attributes(next_individual)
        self.simulation.statetracker.change_state_release(
            self, next_node, next_individual, next_individual.is_blocked
        )
        if not reroute:
            self.begin_service_if_possible_release(next_individual, newly_free_server)
        next_node.accept(next_individual)
        if not reroute:
            self.release_blocked_individual()

    def release_blocked_individual(self):
        """Release an individual blocked by this node.

        Finds the individual who has been blocked the longest, removes them
        from the blocked queue, restores their service if it was interrupted,
        and releases them from their node.
        """
        if (self.len_blocked_queue > 0) and (self.number_of_individuals < self.node_capacity):
            node_to_receive_from = self.simulation.nodes[self.blocked_queue[0][0]]
            individual_to_receive_index = [
                ind.id_number for ind in node_to_receive_from.all_individuals
            ].index(self.blocked_queue[0][1])
            individual_to_receive = node_to_receive_from.all_individuals[individual_to_receive_index]
            self.blocked_queue.pop(0)
            self.len_blocked_queue -= 1
            if individual_to_receive.interrupted:
                individual_to_receive.interrupted = False
                individual_to_receive.service_start_date = individual_to_receive.original_service_start_date
                individual_to_receive.service_end_date = individual_to_receive.service_start_date + individual_to_receive.original_service_time
                node_to_receive_from.interrupted_individuals.remove(individual_to_receive)
                node_to_receive_from.number_interrupted_individuals -= 1
            node_to_receive_from.release(individual_to_receive, self)

    def reset_class_change(self, individual):
        """Reset an individual's class change date when service begins.

        Args:
            individual (Individual): The individual beginning service.
        """
        if self.dynamic_classes:
            individual.class_change_date = float('inf')
            if individual == self.next_class_change_ind:
                self.find_next_class_change()

    def renege(self):
        """Remove an individual from the queue due to reneging.

        Resets the individual's reneging date and sends the individual to
        their reneging destination.
        """
        reneging_individual = self.decide_between_simultaneous_individuals()
        reneging_individual.reneging_date = float("Inf")
        next_node = self.next_node_for_jockeying(reneging_individual)
        self.individuals[reneging_individual.prev_priority_class].remove(reneging_individual)
        self.number_of_individuals -= 1
        reneging_individual.queue_size_at_departure = self.number_of_individuals
        reneging_individual.exit_date = self.now
        self.write_reneging_record(reneging_individual)
        self.reset_individual_attributes(reneging_individual)
        self.simulation.statetracker.change_state_renege(self, next_node, reneging_individual, False)
        next_node.accept(reneging_individual, completed=False)
        self.release_blocked_individual()

    def get_reneging_date(self, ind):
        """Return the reneging date for a given individual.

        Args:
            ind (Individual): The individual.

        Returns:
            float: The reneging date.
        """
        dist = self.simulation.network.customer_classes[ind.customer_class].reneging_time_distributions[self.id_number - 1]
        if dist is None:
            return float("inf")
        return self.now + dist.sample(t=self.now, ind=ind)

    def get_service_time(self, ind):
        """Return a service time for the given customer class.

        Args:
            ind (Individual): The individual being served.

        Returns:
            float: The sampled service time.
        """
        return self.simulation.service_times[self.id_number][ind.customer_class].sample(t=self.now, ind=ind)

    def take_servers_off_duty(self, preemption=False):
        """Gather the servers that should be deleted.

        Args:
            preemption (bool): Whether preemption is active for this shift
                change.
        """
        if preemption == False:
            to_delete = []
            for srvr in self.servers:
                srvr.shift_end = self.next_event_date
                if srvr.busy:
                    srvr.offduty = True
                else:
                    to_delete.append(srvr)
        else:
            to_delete = self.servers[::1]  # copy
            for s in self.servers:
                s.shift_end = self.next_event_date
                if s.cust is not False:
                    self.interrupt_service(s.cust)
            self.sort_interrupted_individuals()
        for obs in to_delete:
            self.kill_server(obs)

    def interrupt_service(self, individual):
        """Interrupt an individual's service.

        Places the individual in the interrupted queue and writes an
        interruption record for them.

        Args:
            individual (Individual): The individual being interrupted.
        """
        individual.original_service_time = individual.service_time
        if self.schedule.preemption == 'reroute':
            self.reroute(individual)
        else:
            self.interrupted_individuals.append(individual)
            individual.interrupted = True
            self.number_interrupted_individuals += 1
            self.write_interruption_record(individual)
            individual.original_service_start_date = individual.service_start_date
            individual.service_start_date = False
            individual.time_left = individual.service_end_date - self.now
            individual.service_time = self.schedule.preemption
            individual.service_end_date = False
            self.number_in_service -= 1

    def sort_interrupted_individuals(self):
        """Sort interrupted individuals by priority class and arrival date."""
        self.interrupted_individuals.sort(key=lambda x: (x.priority_class, x.arrival_date))

    def reroute(self, individual):
        """Reroute a preempted individual.

        Args:
            individual (Individual): The individual being rerouted.
        """
        next_node = self.next_node_for_rerouting(individual)
        self.write_interruption_record(individual, destination=next_node.id_number)
        self.release(individual, next_node, reroute=True)

    def update_next_end_service_without_server(self):
        """Update the next end of a slotted service in `possible_next_events`."""
        if self.slotted or isinf(self.c):
            next_end_service_date = float("Inf")
            for ind in self.all_individuals:
                if not ind.is_blocked and ind.service_end_date >= self.now:
                    if ind.service_end_date < next_end_service_date:
                        self.possible_next_events['end_service'] = ([ind], ind.service_end_date)
                        next_end_service_date = ind.service_end_date
                    elif (ind.service_end_date == next_end_service_date) and (not isinf(next_end_service_date)):
                        self.possible_next_events['end_service'][0].append(ind)

    def update_next_end_service_with_server(self):
        """Update the next end service with a server in `possible_next_events`."""
        if not self.slotted and not isinf(self.c):
            next_end_service_date = float("Inf")
            for s in self.servers:
                if s.next_end_service_date < next_end_service_date:
                    self.possible_next_events['end_service'] = ([s.cust], s.next_end_service_date)
                    next_end_service_date = s.next_end_service_date
                elif (s.next_end_service_date == next_end_service_date) and (not isinf(next_end_service_date)):
                    self.possible_next_events['end_service'][0].append(s.cust)

    def update_next_renege_time(self):
        """Update the next renege time in `possible_next_events`."""
        if not isinf(self.c) and self.reneging is True:
            next_renege_date = float('Inf')
            for ind in self.all_individuals:
                if (ind.reneging_date < next_renege_date) and not ind.server:
                    self.possible_next_events['renege'] = ([ind], ind.reneging_date)
                    next_renege_date = ind.reneging_date
                elif (ind.reneging_date == next_renege_date) and (not ind.server) and (not isinf(next_renege_date)):
                    self.possible_next_events['renege'][0].append(ind)

    def update_next_class_change_while_waiting(self):
        """Update the next class change while waiting in `possible_next_events`."""
        if self.dynamic_classes is True and not isinf(self.c):
            self.possible_next_events['class_change'] = (self.next_class_change_ind, self.next_class_change_date)

    def update_next_shift_change_or_slot_time(self):
        """Update `possible_next_events` with the next shift or slot time."""
        if self.schedule is not None:
            if self.schedule.schedule_type == 'schedule':
                self.possible_next_events['shift_change'] = (None, self.next_shift_change)
            if self.schedule.schedule_type == 'slotted':
                self.possible_next_events['slotted_service'] = (None, self.schedule.next_slot_date)

    def update_next_event_date(self):
        """Find the time of the next event at this node.

        With infinite servers this is the time of the next individual to end
        service, or infinity. Otherwise it is the minimum of the next shift
        change and the time for the next individual (who is not blocked) to
        end service, or infinity.
        """
        self.possible_next_events = {}
        self.update_next_end_service_without_server()
        self.update_next_end_service_with_server()
        self.update_next_renege_time()
        self.update_next_class_change_while_waiting()
        self.update_next_shift_change_or_slot_time()
        if self.reneging or self.dynamic_classes or self.schedule:
            next_event, self.next_event_type = self.decide_next_event()
            self.next_event_date = next_event[1]
            self.next_individual = next_event[0]
        else:
            next_end_service = self.possible_next_events.get('end_service', (None, float('inf')))
            self.next_event_date = next_end_service[1]
            self.next_individual = next_end_service[0]
            self.next_event_type = 'end_service'

    def decide_next_event(self):
        """Decide the next event.

        Chooses the next service end, renege, shift change, or class change.
        In the case of a tie, events are prioritised in the following order:

        1. slotted service
        2. shift change
        3. end service
        4. class change
        5. renege

        Returns:
            tuple: The next event and its event type.
        """
        next_date = float('inf')
        next_event = (None, float('inf'))
        next_event_type = None
        for event_type in ['slotted_service', 'shift_change', 'end_service', 'class_change', 'renege']:
            possible_next_event = self.possible_next_events.get(event_type, (None, float('inf')))
            if possible_next_event[1] < next_date:
                next_event = possible_next_event
                next_event_type = event_type
                next_date = next_event[1]
        return next_event, next_event_type

    def wrap_up_servers(self, current_time):
        """Update server total and busy times at the end of the run.

        Args:
            current_time (float): The simulation end time.
        """
        if not isinf(self.c):
            for srvr in self.servers:
                srvr.total_time = self.increment_time(current_time, -srvr.start_date)
                if srvr.busy:
                    srvr.busy_time += self.increment_time(current_time, -srvr.cust.service_start_date)

    def write_individual_record(self, individual):
        """Write a data record for an individual leaving a node.

        Args:
            individual (Individual): The individual leaving the node.
        """
        if isinf(self.c) or self.slotted:
            server_id = False
        else:
            server_id = individual.server.id_number

        record = DataRecord(
            id_number=individual.id_number,
            customer_class=individual.previous_class,
            original_customer_class=individual.original_class,
            node=self.id_number,
            arrival_date=individual.arrival_date,
            waiting_time=individual.service_start_date - individual.arrival_date,
            service_start_date=individual.service_start_date,
            service_time=individual.service_end_date - individual.service_start_date,
            service_end_date=individual.service_end_date,
            time_blocked=individual.exit_date - individual.service_end_date,
            exit_date=individual.exit_date,
            destination=individual.destination,
            queue_size_at_arrival=individual.queue_size_at_arrival,
            queue_size_at_departure=individual.queue_size_at_departure,
            server_id=server_id,
            record_type="service",
        )
        individual.data_records.append(record)

    def write_incomplete_record(self, individual):
        """Write an incomplete data record at the end of the run.

        Args:
            individual (Individual): The individual still at the node.

        Returns:
            DataRecord: The incomplete data record.
        """
        if not individual.service_time:  # Still in queue
            service_start_date = None
            waiting_time = None
            service_time = None
            service_end_date = None
        else:
            service_start_date = individual.service_start_date
            waiting_time = individual.service_start_date - individual.arrival_date
            if individual.service_end_date > self.now: # Still in service
                service_time = None
                service_end_date = None
            else: # Still blocked
                service_time = individual.service_time
                service_end_date = individual.service_end_date

        record = DataRecord(
            id_number=individual.id_number,
            customer_class=individual.previous_class,
            original_customer_class=individual.original_class,
            node=self.id_number,
            arrival_date=individual.arrival_date,
            waiting_time=waiting_time,
            service_start_date=service_start_date,
            service_time=service_time,
            service_end_date=service_end_date,
            time_blocked=None,
            exit_date=None,
            destination=None,
            queue_size_at_arrival=individual.queue_size_at_arrival,
            queue_size_at_departure=None,
            server_id=False,
            record_type="incomplete",
        )
        return record

    def write_interruption_record(self, individual, destination=nan):
        """Write a data record for an individual being interrupted.

        Args:
            individual (Individual): The interrupted individual.
            destination (int): The destination node number.
        """
        if self.slotted:
            server_id = False
        else:
            server_id = individual.server.id_number

        record = DataRecord(
            id_number=individual.id_number,
            customer_class=individual.previous_class,
            original_customer_class=individual.original_class,
            node=self.id_number,
            arrival_date=individual.arrival_date,
            waiting_time=individual.service_start_date - individual.arrival_date,
            service_start_date=individual.service_start_date,
            service_time=individual.original_service_time,
            service_end_date=nan,
            time_blocked=nan,
            exit_date=self.now,
            destination=destination,
            queue_size_at_arrival=individual.queue_size_at_arrival,
            queue_size_at_departure=individual.queue_size_at_departure,
            server_id=server_id,
            record_type="interrupted service",
        )
        individual.data_records.append(record)

    def write_reneging_record(self, individual):
        """Write a data record for an individual when reneging.

        Args:
            individual (Individual): The reneging individual.
        """
        record = DataRecord(
            id_number=individual.id_number,
            customer_class=individual.previous_class,
            original_customer_class=individual.original_class,
            node=self.id_number,
            arrival_date=individual.arrival_date,
            waiting_time=individual.exit_date - individual.arrival_date,
            service_start_date=nan,
            service_time=nan,
            service_end_date=nan,
            time_blocked=nan,
            exit_date=individual.exit_date,
            destination=individual.destination,
            queue_size_at_arrival=individual.queue_size_at_arrival,
            queue_size_at_departure=individual.queue_size_at_departure,
            server_id=nan,
            record_type="renege",
        )
        individual.data_records.append(record)

    def write_baulking_or_rejection_record(self, individual, record_type):
        """Write a data record for an individual who baulks or is rejected.

        Args:
            individual (Individual): The individual.
            record_type (str): The type of record to write.
        """
        record = DataRecord(
            id_number=individual.id_number,
            customer_class=individual.previous_class,
            original_customer_class=individual.original_class,
            node=self.id_number,
            arrival_date=self.now,
            waiting_time=nan,
            service_start_date=nan,
            service_time=nan,
            service_end_date=nan,
            time_blocked=nan,
            exit_date=self.now,
            destination=nan,
            queue_size_at_arrival=self.number_of_individuals,
            queue_size_at_departure=nan,
            server_id=nan,
            record_type=record_type,
        )
        individual.data_records.append(record)

    def reset_individual_attributes(self, individual):
        """Reset the attributes of an individual.

        Args:
            individual (Individual): The individual to reset.
        """
        individual.arrival_date = False
        individual.service_time = False
        individual.service_start_date = False
        individual.service_end_date = False
        individual.exit_date = False
        individual.queue_size_at_arrival = False
        individual.queue_size_at_departure = False
        individual.destination = False
