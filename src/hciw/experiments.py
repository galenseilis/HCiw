import ciw

N = ciw.create_network(
    arrival_distributions=[ciw.dists.Exponential(rate=0.2)],
    service_distributions=[ciw.dists.Exponential(rate=0.1)],
    number_of_servers=[3]
)


Q = ciw.Simulation(N)
Q.simulate_until_max_time(1440)

print(Q.get_all_records())
