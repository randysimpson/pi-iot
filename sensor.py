'''
Copyright (©) 2019 - Randall Simpson
pi-iot

This base sensor class.
'''
class Sensor:
    def __init__(self, source, metric_prefix, output):
        self.source = source
        self.metric_prefix = metric_prefix
        self.output = output
        self.metrics = []

    def get_info():
        return None

    def format_metrics():
        return None
