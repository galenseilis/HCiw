'''Initial waitlist construction.'''

import math
import ciw

def begin_service_if_possible_accept(node, next_individual):
    """
    Begins the service of the next individual (at acceptance point):
        - Sets the arrival date as the current time
        - If there is a free server or there are infinite servers:
            - Attach the server to the individual (only when servers are not infinite)
        - Get service start time, service time, service end time
        - Update the server's end date (only when servers are not infinite)
    """
    free_server = node.find_free_server(next_individual)
    if free_server is None and math.isinf(node.c) is False:
        node.decide_preempt(next_individual)
    if free_server is not None or math.isinf(node.c):
        if math.isinf(node.c) is False:
            node.attach_server(free_server, next_individual)
        next_individual.service_start_date = 0
        next_individual.service_time = node.get_service_time(next_individual)
        next_individual.service_end_date = next_individual.service_time
        if not math.isinf(node.c):
            free_server.next_end_service_date = next_individual.service_end_date


# from the ciw source code; needs to be adapted to accommodate the pre-existing wait list
def accept(individual_id, individual_class, arrival_date, node, simulation):
    """
    Accepts a new customer to the queue:
      - record all other information at arrival point
      - update state tracker
    """
    simulation.current_time = arrival_date
    next_individual = ciw.Individual(id_number=individual_id, customer_class=individual_class, priority_class=simulation.network.priority_class_mapping[individual_class], simulation=simulation)
    next_individual.node = node.id_number
    next_individual.queue_size_at_arrival = 'Unknown'
    node.individuals[next_individual.priority_class].append(next_individual)
    node.number_of_individuals += 1
    node.simulation.statetracker.change_state_accept(node, next_individual)
    next_individual.arrival_date = arrival_date
    begin_service_if_possible_accept(node, next_individual)
   
    simulation.nodes[0].number_of_individuals += 1
    simulation.nodes[0].number_of_individuals_per_class[next_individual.customer_class] += 1
    simulation.nodes[0].number_accepted_individuals += 1
    simulation.nodes[0].number_accepted_individuals_per_class[next_individual.customer_class] += 1

def create_existing_customers_from_list(backlog, Q):
    '''Occupies instance of simulation with individuals.


    PARAMETERS
    ----------
    backlog (list): List of data for each individual to be added.
    Q (ciw.Simulation): Instance of simulation.
    '''
    customer_count = 1
    for row in backlog:
        customer_id = row[0]
        customer_class = row[1]
        customer_arrival_date = row[2]
        customer_node = row[3]
        accept(customer_id, customer_class, customer_arrival_date, Q.nodes[customer_node], Q)
        customer_count += 1
