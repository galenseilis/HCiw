def summarize_individuals(simulation, t, agg_f, desc_f, filter_f=None):
    filter_f = filter_f or (lambda x,t: True)
    result = {}
    for node in simulation.nodes[1:-1]:
        if node.all_individuals:
            pub = agg_f(
                [
                    desc_f(ind, t) for ind in node.all_individuals if filter_f(ind, t)
                ]
            )
            result[str(node)] = pub if np.isfinite(pub) else 1
        else:
            result[str(node)] = 1
    return result

def is_under_benchmark(ind, t):
    return t <= (ind.arrival_date + ind.customer_class.benchmark) 

def least_percent_underbenchmark(simulation, t=None):
    t = t or simulation.current_time
    return min(summarize_individuals(simulation, t=t, agg_f=np.mean, desc_f=is_under_benchmark).values())

def is_urgent(ind, t=None):
    return ind.customer_class.priority == 0

def least_percent_urgent_underbenchmark(simulation, t=None):
    t = t or simulation.current_time
    return min(
        summarize_individuals(
            simulation, 
            t=t, 
            agg_f=np.mean, 
            desc_f=is_under_benchmark, 
            filter_f=is_urgent
        ).values()
    )

def fiscal_year(date_time):
    year = date_time.year
    if date_time.month > 3:
        year += 1
    return year

def convert_simtime_to_datetime(datetime, t:float):
    return datetime + pd.Timedelta(t, 'D')

def convert_datetime_to_simtime(start_time, datetime):
    return (datetime - start_time).days

def filter_to_cover_time(df, t):
    return df[(df.arrival_date <= t) & (df.exit_date >= t)]

def fiscal_year_date_range(start_date, end_date):
    return [pd.to_datetime(f'{d}-03-31') for d in range(start_date.year, end_date.year+1)]

def fiscal_year_simtimes(start_date, end_date):
    return [convert_datetime_to_simtime(start_date, date) for date in fiscal_year_date_range(start_date, end_date)]

class WeekDayServe(ciw.dists.Distribution):

    def __init__(self, dist, offset=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dist = dist
        self.offset = offset

    def sample(self, t=None, ind=None):
        tau = (np.floor(t) - self.offset + 7) % 7
        if tau < 5:
            return self.dist.sample(t, ind)
        elif tau == 5:
            return 2
        else:
            return 1
            
