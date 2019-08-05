'''
Copyright (©) 2019 - Randall Simpson
pi-iot

This is a metric class for storing metric information.
'''
class Metric:
    def __init__(self, name, value, date):
        self.name = name
        self.value = value
        self.date = date
