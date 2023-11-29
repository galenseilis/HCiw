import ciw

N = ciw.create_network(
    arrival_distributions={
        "C1": [ciw.dists.Exponential(rate=5)],
        "C2": [None],
        "C3": [None],
    },
    service_distributions={
        "C1": [ciw.dists.Exponential(rate=10)],
        "C2": [ciw.dists.Exponential(rate=10)],
        "C3": [ciw.dists.Exponential(rate=10)],
    },
    routing={"C1": [[1.0]], "C2": [[1.0]], "C3": [[1.0]]},
    class_change_matrices=[
        {
            "C1": {"C1": 0.0, "C2": 0.5, "C3": 0.5},
            "C2": {"C1": 0.5, "C2": 0.0, "C3": 0.5},
            "C3": {"C1": 0.5, "C2": 0.5, "C3": 0.0},
        }
    ],
    number_of_servers=[1],
)


from collections import Counter

ciw.seed(1)

Q = ciw.Simulation(N)

Q.simulate_until_max_time(50.0)

recs = Q.get_all_records()

Counter([r.customer_class for r in recs])
