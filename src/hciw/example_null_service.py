import ciw
import pandas as pd


def just_none(individuals):
    print(len(individuals))
    return None


N = ciw.create_network(
    arrival_distributions=[ciw.dists.Exponential(rate=5)],
    service_distributions=[ciw.dists.Exponential(rate=5)],
    service_disciplines=[just_none],
    number_of_servers=[1],
)

ciw.seed(2018)
Q = ciw.Simulation(N)
Q.simulate_until_max_time(1)

df = pd.DataFrame(Q.get_all_records())

print(df.to_markdown(index=False))
