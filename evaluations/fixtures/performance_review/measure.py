import cProfile
import json
import platform
from statistics import median
from time import perf_counter_ns

from sales import baseline, candidate


def measure():
    rows = [{'product': f'P{index % 200}', 'quantity': 1} for index in range(3000)]
    requested = [f'P{index}' for index in range(150)]
    expected = baseline(rows, requested)
    if candidate(rows, requested) != expected:
        raise ValueError('Candidate changed results')
    samples = {'baseline_ns': [], 'candidate_ns': []}
    for repetition in range(7):
        order = [('baseline_ns', baseline), ('candidate_ns', candidate)]
        if repetition % 2:
            order.reverse()
        for name, function in order:
            start = perf_counter_ns()
            result = function(rows, requested)
            elapsed = perf_counter_ns() - start
            if result != expected:
                raise ValueError('Measured candidate changed results')
            samples[name].append(elapsed)
    work = {}
    profile = cProfile.Profile()
    for name, function in [('baseline', baseline), ('candidate', candidate)]:
        metrics = {}
        profile.runcall(function, rows, requested, metrics)
        work[name] = metrics['rows_examined']
    return {'python': platform.python_version(), 'platform': platform.system(),
            'rows': len(rows), 'requests': len(requested), 'repetitions': 7,
            'samples': samples, 'median_ns': {name: median(values) for name, values in samples.items()},
            'rows_examined': work, 'profile_total_calls': sum(entry.callcount for entry in profile.getstats()),
            'scope': 'Local synthetic microbenchmark; no agent, I/O, concurrency or production claim'}


if __name__ == '__main__':
    print(json.dumps(measure(), indent=2))
