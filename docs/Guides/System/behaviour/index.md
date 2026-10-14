<a id="behaviour-nodes"></a>

# How to Get More Custom Behaviour

Custom behaviour can be obtained by writing new `Node`, `ArrivalNode`, `ExitNode`, `Individual`, and/or `Server` classes, that inherit from the original `hciw.Node`, `hciw.ArrivalNode`, `hciw.Individual` and `hciw.Server` classes respectively, that introduce new beahviour into the system. The classes that can be overwitten are:

- `Node`: the main node class used to represent a service centre.
- `ArrivalNode`: the node class used to generate individuals and route them to a specific `Node`.
- `ExitNode`: the node class used to collect customers as they leave the system.
- `Individual`: the individual class used to represent the individual entities.
- `Server`: the class used to represent the servers that sit at a service centre.

These new classes can be used with the Simulation class by using the keyword arugments `node_class`, `arrival_node_class`, `exit_node_class`, `individual_class`, and `server_class`. These arguments take a class (not an instance of a class), to use throughout the whole simulation. The argument `node_class` can also take a list of classes, indicating which node class to use on each node of the network. This allows for different nodes to exhibit very different behaviours to one another.

## Library of Examples

Here's a library of examples of this functionality:

- [State-dependent Arrivals](custom_arrivals.md)
- [Variable Number of Servers](custom_number_servers.md)
- [Server-dependent Services](server_dependent_dist.md)
- [DES+SD Hybrid Simulation with HCiw](hybrid.md)
