from copy import copy
from itertools import product
from typing import Callable

from tqdm import tqdm
import ciw


class ServerOptimizer:
    """Simulation optmizer."""

    def __init__(self, ciw_network: ciw.Network, obj_func: Callable):
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

        Returns:
            best_score, best_allocation
        """
        best_score = None
        best_allocation = None
        sim_kwargs = {} if sim_kwargs is None else sim_kwargs
        for server_allocation in tqdm(product(*server_grid)):
            N = self._gen_new_ciw_network(server_allocation)
            for replicate in range(reps):
                S = ciw.Simulation(N, **sim_kwargs)
                S.simulate_until_max_time(sim_time)
                score = self.obj_func(S)
                if best_score is None:
                    best_score = score
                    best_allocation = server_allocation
                elif score < best_score:
                    best_score = score
                    best_allocation = server_allocation
                else:
                    continue
        return best_score, best_allocation

    def _gen_new_ciw_network(self, server_alloc: list[int]):
        """Create copy of network with new server allocation.

        Args:
            server_alloc (list[int]): Servers for each.

        The length of server_alloc must be the same as the length
        of the Ciw network's service_centres attribute.
        """
        N = copy(self.ciw_network)
        if len(N.service_centres) != len(server_alloc):
            raise ValueError(
                "Number of server allocations does not match the number of service centres."
            )
        for sc, s in zip(N.service_centres, server_alloc):
            sc.number_of_servers = s
        return N


if __name__ == "__main__":
    N = ciw.create_network(
        arrival_distributions=[ciw.dists.Exponential(rate=0.2), ciw.dists.Exponential(rate=0.2)],
        service_distributions=[ciw.dists.Exponential(rate=0.01), ciw.dists.Exponential(rate=0.2)],
        number_of_servers=[3, 3],
        routing=[[0.0] * 2] * 2
    )

    server_grid = [list(range(1, 10))] * 2

    def objective(sim: ciw.Simulation):
        num_servers = [sc.number_of_servers for sc in sim.network.service_centres]
        num_servers = tuple(num_servers)
        neg_completed = -len(sim.get_all_records())
        return (neg_completed,) + num_servers

    SO = ServerOptimizer(N, objective)

    print(SO.run(1440, server_grid, reps=10))
