'''
Copyright (©) 2019 - Randall Simpson
pi-iot

This class is used to gather temperature sensor metrics from a raspberry pi.
'''
from sensor import Sensor
from metric import Metric
import datetime
import Adafruit_DHT

class Temp(Sensor):
    def __init__(self, source, metric_prefix, output, code, pin, format):
        Sensor.__init__(self, source, metric_prefix, output)
        if code == 'DHT22':
            self.code = Adafruit_DHT.DHT22
        else:
            self.code = Adafruit_DHT.DHT11
        self.pin = pin
        self.format = format
        self.tag_label = code

    def get_info(self):
        date = datetime.datetime.utcnow()
        humidity, temp = Adafruit_DHT.read_retry(self.code, self.pin)
        if temp is not None:
            name = self.metric_prefix + 'humidity'
            if self.output == 'WF':
                name = 'Humidity'
                if len(self.metric_prefix) > 0:
                    name = self.metric_prefix + '.' + name
            self.metrics.append(Metric(name, humidity, date))
            if self.format == 'f':
                temp = (temp * 9/5) + 32
            name = self.metric_prefix + 'temperature'
            if self.output == 'WF':
                name = 'Temperature'
                if len(self.metric_prefix) > 0:
                    name = self.metric_prefix + '.' + name
            self.metrics.append(Metric(name, temp, date))
            return self.format_metrics()
        else:
            return None

    def format_metrics(self):
        rtnMetrics = []
        while len(self.metrics) > 0:
            metric = self.metrics.pop()
            if self.output == 'WF':
                tags = {}
                tags['Pin'] = self.pin
                tags['Sensor'] = self.tag_label
                detail = {}
                detail['value'] = metric.value
                detail['tags'] = tags
                m = {}
                m[metric.name] = detail
                rtnMetrics.append(m)
            else:
                m = {}
                m['date'] = metric.date.isoformat() + 'Z'
                m['metric'] = metric.name
                m['value'] = metric.value
                m['source'] = self.source
                tags = {}
                tags['pin'] = self.pin
                tags['sensor'] = self.tag_label
                m['tags'] = tags
                rtnMetrics.append(m)
        return rtnMetrics
