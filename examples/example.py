from itertools import product
from typing import Callable


class ServerOptimizer:
    """Simulation optmizer."""

    def __init__(self, ciw_network, obj_func: Callable):
        """
        Args:
            ciw_network (ciw.Network): Ciw network to be optimized.
            obj_func (Callable): Objective function to define optimality.

        The objective function should take the simulation class as an argument.
        """
        self.ciw_network = ciw_network
        self.obj_func = obj_func

    def run(
        self,
        sim_time: float,
        server_grid: list[list[int]],
        reps: int = 1,
        sim_kwargs=None,
    ):
        """Run the simulation optimization.

        Args:
            reps (int): Number of replicates to run.
        """
        for server_allocation in product(*server_grid):
            N = self._gen_new_ciw_network(server_allocation)
            for replicate in range(reps):
                S = ciw.Simulation(N, **sim_kwargs)
                S.simulate_until_max_time(sim_time)

    def _gen_new_ciw_network(self, server_alloc: list[int]):
        """Create copy of network with new server allocation.

        Args:
            server_alloc (list[int]): Servers for each.

        The length of server_alloc must be the same as the length
        of the Ciw network's service_centres attribute.
        """
        N = self.ciw_network.copy()
        for sc, s in zip(*N.service_centres, server_alloc):
            sc.number_of_servers = s
        return N
