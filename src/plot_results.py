import os
import matplotlib.pyplot as plt

class Experiment:
    def __init__ (self, name, metrics):
        self.name = name
        self.metrics = metrics


class TestResults:
    def __init__(self, metric_names, experiments):
        self.experiments = experiments
        self.metric_cnt = len(metric_names)
        self.metric_names = metric_names

        for experiment in experiments:
            if len(experiment.metrics) != self.metric_cnt:
                raise ValueError('Each experiment must have the same number of metrics')
        
        self.metric_ranges = []
        for i in range(self.metric_cnt):
            self.metric_ranges.append([min([experiment.metrics[i] for experiment in experiments]), max([experiment.metrics[i] for experiment in experiments])])

    def plot(self):
        os.makedirs('plots', exist_ok=True)
        for i in range(self.metric_cnt):
            plt.figure(figsize=(10, 5))
            plt.bar([experiment.name for experiment in self.experiments], [experiment.metrics[i] for experiment in self.experiments])
            plt.ylim(self.metric_ranges[i][0] * 0.9, self.metric_ranges[i][1] * 1.1)
            plt.title(self.metric_names[i])
            plt.savefig(f'plots/{self.metric_names[i]}.png')
            plt.close()

test_results = TestResults(
     ['metric1', 'metric2', 'metric3'],
    [
        Experiment('experiment1', [1, 2, 3]),
        Experiment('experiment2', [2, 3, 4]),
        Experiment('experiment3', [3, 4, 5]),
    ],
)

test_results.plot()