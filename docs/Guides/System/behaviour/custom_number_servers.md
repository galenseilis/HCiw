# Variable Number of Servers

In this example we will consider a network where servers are added and removed depending on the system state. We will look at a system without this behaviour first, and then the system with the desired behaviour, for comparison.

## Without desired behaviour

Consider an M/M/1 queue with $\Lambda = 1$ and $\mu = 0.4$. Here the traffic intensity of the system is greater than one, that is we have customers arriving faster than can be served, and so the queue size will increase over time. Let's see this:

``` python
>>> import hciw

>>> N = hciw.create_network(
...     arrival_distributions=[hciw.dists.Exponential(rate=1)],
...     service_distributions=[hciw.dists.Exponential(rate=0.4)],
...     number_of_servers=[1]
... )

>>> hciw.seed(0)
>>> Q = hciw.Simulation(N, tracker=hciw.trackers.SystemPopulation())
>>> Q.simulate_until_max_time(100)
```

Now let's plot the system population over time:

``` python
>>> plt.plot(
...     [row[0] for row in Q.statetracker.history],
...     [row[1] for row in Q.statetracker.history]
... ); # doctest:+SKIP
```

<img src="../../../_static/custom_number_servers_without.svg" class="align-center" alt="Plot of system population increasing over time." />

## With desired behaviour

We will now create a `AdaptiveNode` that will add two servers if the population exceeds 10 individuals, and then drop back down to one server if the population drops back down to 3 individuals. First create the `AdaptiveNode` that inherits from the `hciw.Node` class, and overwrite the `have_event` methods so it first checks the population size and adds / removes servers as needed:

``` python
>>> class AdaptiveNode(hciw.Node):
...     def have_event(self):
...         if (len(self.all_individuals) > 10) and (len(self.servers) == 1):
...             print(f'Adding servers at {self.now:.3f}')
...             self.add_new_servers(2)
...         elif (len(self.all_individuals) < 4) and (len([s for s in self.servers if not s.offduty]) == 3):
...             print(f'Removing servers at {self.now:.3f}')
...             self.take_servers_off_duty()
...             self.add_new_servers(1)
...         super().have_event()
```

Here print statements have also been added to record when the changes in the numbers of servers occur.

Now rerun the same system, telling HCiw to use the new `node_class`. We'll still begin with just one server:

``` python
>>> hciw.seed(0)
>>> Q = hciw.Simulation(N, node_class=AdaptiveNode, tracker=hciw.trackers.SystemPopulation())
>>> Q.simulate_until_max_time(100)
Adding servers at 12.279
Removing servers at 43.344
Adding servers at 89.848
```

Now let's plot the system population over time:

``` python
>>> plt.plot(
...     [row[0] for row in Q.statetracker.history],
...     [row[1] for row in Q.statetracker.history]
... ); # doctest:+SKIP
```

<img src="../../../_static/custom_number_servers_with.svg" class="align-center" alt="Plot of system population over time." />

We see the system population is now better under control. Furthermore, large changes in the system population tends occur at the times where servers were added and removed.
