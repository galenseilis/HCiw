"""Information stores describing the nodes and classes of a network."""


class ServiceCentre:
    """Store the class-independent information for a service centre.

    Attributes:
        number_of_servers (int or Schedule): The number of servers, or a
            schedule describing how it varies over time.
        queueing_capacity (int or float): The maximum queue length.
        class_change_matrix (dict): Matrix describing class changes, if any.
        priority_preempt (bool): Whether priority classes preempt service.
        ps_threshold (int): Threshold used by the processor-sharing discipline.
        server_priority_function (callable): Function assigning server priority.
        service_discipline (callable): The service discipline used at the node.
        class_change_time (bool): Whether class change times are modelled.
    """

    def __init__(  # noqa: PLR0913, PLR0917 - public configuration API
        self,
        number_of_servers,
        queueing_capacity,
        class_change_matrix=None,
        priority_preempt=False,
        ps_threshold=1,
        server_priority_function=None,
        service_discipline=None,
    ):
        """Initialise a ``ServiceCentre`` object.

        Args:
            number_of_servers (int or Schedule): The number of servers, or a
                schedule describing how it varies over time.
            queueing_capacity (int or float): The maximum queue length.
            class_change_matrix (dict, optional): Matrix describing class
                changes, if any.
            priority_preempt (bool, optional): Whether priority classes
                preempt service. Defaults to ``False``.
            ps_threshold (int, optional): Threshold used by the
                processor-sharing discipline. Defaults to ``1``.
            server_priority_function (callable, optional): Function assigning
                server priority.
            service_discipline (callable, optional): The service discipline
                used at the node.
        """
        self.number_of_servers = number_of_servers
        self.queueing_capacity = queueing_capacity
        self.class_change_matrix = class_change_matrix
        self.priority_preempt = priority_preempt
        self.ps_threshold = ps_threshold
        self.server_priority_function = server_priority_function
        self.service_discipline = service_discipline
        self.class_change_time = False


class CustomerClass:
    """Store the class-dependent information for a customer class.

    Attributes:
        arrival_distributions (dict): Arrival distributions for each node.
        service_distributions (dict): Service distributions for each node.
        batching_distributions (dict): Batching distributions for each node.
        routing (Routing): The routing object for the class.
        priority_class (int): The priority class of the customer class.
        baulking_functions (dict): Baulking functions for each node.
        reneging_time_distributions (dict): Reneging time distributions for
            each node.
        class_change_time_distributions (dict): Class change time
            distributions for each pair of customer classes.
    """

    def __init__(  # noqa: PLR0913, PLR0917 - public configuration API
        self,
        arrival_distributions,
        service_distributions,
        routing,
        priority_class,
        baulking_functions,
        batching_distributions,
        reneging_time_distributions,
        class_change_time_distributions,
    ):
        """Initialise a ``CustomerClass`` object.

        Args:
            arrival_distributions (dict): Arrival distributions for each node.
            service_distributions (dict): Service distributions for each node.
            routing (Routing): The routing object for the class.
            priority_class (int): The priority class of the customer class.
            baulking_functions (dict): Baulking functions for each node.
            batching_distributions (dict): Batching distributions for each node.
            reneging_time_distributions (dict): Reneging time distributions for
                each node.
            class_change_time_distributions (dict): Class change time
                distributions for each pair of customer classes.
        """
        self.arrival_distributions = arrival_distributions
        self.service_distributions = service_distributions
        self.batching_distributions = batching_distributions
        self.routing = routing
        self.priority_class = priority_class
        self.baulking_functions = baulking_functions
        self.reneging_time_distributions = reneging_time_distributions
        self.class_change_time_distributions = class_change_time_distributions


class Network:
    """Store the queueing network.

    Holds a list of ``ServiceCentre`` objects for each service centre and
    a dictionary of ``CustomerClass`` objects keyed by class name.

    Attributes:
        service_centres (list): The service centres of the network.
        customer_classes (dict): The customer classes, keyed by class name.
        number_of_nodes (int): The number of service centres.
        number_of_classes (int): The number of customer classes.
        customer_class_names (list): The sorted names of the customer classes.
        number_of_priority_classes (int): The number of distinct priority
            classes.
        priority_class_mapping (dict): Maps class names to priority classes.
        system_capacity (float): The total capacity of the system.
    """

    system_capacity: float

    def __init__(self, service_centres, customer_classes):
        """Initialise a ``Network`` object.

        Args:
            service_centres (list): The service centres of the network.
            customer_classes (dict): The customer classes, keyed by class name.
        """
        self.service_centres = service_centres
        self.customer_classes = customer_classes
        self.number_of_nodes = len(service_centres)
        self.number_of_classes = len(customer_classes)
        self.customer_class_names = sorted(customer_classes.keys())
        self.number_of_priority_classes = len(
            {clss.priority_class for clss in customer_classes.values()}
        )
        self.priority_class_mapping = {
            clss: customer_classes[clss].priority_class for clss in customer_classes
        }
        for nd_id, node in enumerate(self.service_centres):
            if all(
                clss.reneging_time_distributions[nd_id] is None
                for clss in self.customer_classes.values()
            ):
                node.reneging = False
            else:
                node.reneging = True
        if any(
            dist is not None
            for clss in customer_classes.values()
            for dist in clss.class_change_time_distributions.values()
        ):
            for node in self.service_centres:
                node.class_change_time = True
