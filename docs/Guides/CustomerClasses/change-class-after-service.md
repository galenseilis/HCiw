<a id="changeclass-afterservice"></a>

# How to Change Customer Class After Service

HCiw allows customers to probabilistically change their class after service. That is after service at node `k` a customer of class `i` will become class `j` with probability $P(J=j \; | \; I=i, K=k)$. These probabilities are input into the system through the `class_change_matrices` keyword.

Consider a one node system with three classes of customer. After service (at Node 1) customers always change customer class, equally likely between the two other customer classes. The `class_change_matrices` for this system are shown below:

$$
\begin{aligned}
\begin{pmatrix}
0.0 & 0.5 & 0.5 \\
0.5 & 0.0 & 0.5 \\
0.5 & 0.5 & 0.0 \\
\end{pmatrix}
\end{aligned}
$$

Labelling the classes `"C1"`, `"C2"` and `"C3"`, this is input into the simulation model by including `class_change_matrices` keyword when creating a Network object:

``` python
>>> import hciw
>>> N = hciw.create_network(
...     arrival_distributions={'C1': [hciw.dists.Exponential(rate=5)],
...                            'C2': [None],
...                            'C3': [None]},
...     service_distributions={'C1': [hciw.dists.Exponential(rate=10)],
...                            'C2': [hciw.dists.Exponential(rate=10)],
...                            'C3': [hciw.dists.Exponential(rate=10)]},
...     routing={'C1': [[1.0]],
...              'C2': [[1.0]],
...              'C3': [[1.0]]},
...     class_change_matrices=[
...         {'C1': {'C1': 0.0, 'C2': 0.5, 'C3': 0.5},
...          'C2': {'C1': 0.5, 'C2': 0.0, 'C3': 0.5},
...          'C3': {'C1': 0.5, 'C2': 0.5, 'C3': 0.0}}
...     ],
...     number_of_servers=[1]
... )
```

Notice in this network only arrivals from customers of class `'C1'` occur. Running this system, we'll see that the count of the number of records with customers of class `'C2'` and `'C3'` are more than zero, as some `'C1'` customers have changed class after service:

``` python
>>> from collections import Counter
>>> hciw.seed(1)
>>> Q = hciw.Simulation(N)
>>> Q.simulate_until_max_time(50.0)
>>> recs = Q.get_all_records()
>>> Counter([r.customer_class for r in recs])
Counter({'C1': 251, 'C3': 115, 'C2': 107})
```

Note that when more than one node is used, each node requires a class change matrix. This means than difference class change matrices can be used for each node.
