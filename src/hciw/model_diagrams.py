from typing import List, NoReturn

import graphviz

# Nodes
# Routing matrix / matrices


def graphviz_queue_diagram(
    diagram_name: str,
    routing,
    num_servers: List[int],
    node_names: List[str],
    concise_servers=True,
) -> NoReturn:
    g = graphviz.Digraph(diagram_name, filename=f"{diagram_name}.gv")

    # Prepare nodes
    for i, (servers, node_name) in enumerate(servers, node_names):
        _node_name = "_" + node_name
        _router_name = f"{_node_name}_router"

        g.node(_router_name, shape="diamond", label=None)

        # Design a node
        with g.subgraph(name=_node_name) as diagram_node:
            diagram_node.attr(label=node_node)
            _queue_name = f"{_node_name}_queue"
            diagram_node.node(_queue_name, shape="rectangle", label="Queue")

            if concise_servers:
                _servers_node_name = f"{_node_name}_{servers}"
                diagram_node.node(_servers_node_name, shape="circle")
                diagram_node.edge(_servers_node_name, _router_name)

            else:
                for j in range(servers):
                    _server_name = f"{_node_name}_server{j}"
                    diagram_node.node(
                        _server_name, shape="circle", label=f"Server {j+1}"
                    )
                    diagram_node.edge(_server_name, _router_name)

    # If an element of routing is a matrix, then label the routing diamond with an "M"
    # If a element of routing is a matrix, then label the edges from the nodes with the probabilities.
    # If an element of routing is a function, then label the routing diamond with an "F"
    # Prepare routing
    if isinstance(routing, list):
        ...
    elif callable(routing):
        ...
    else:
        raise NotImplementedError(f"routing={routing} is not currently supported")

    return g
