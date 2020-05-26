'''
Copyright (©) 2020 - Randall Simpson
pi-iot

This class is used to gather sound sensor metrics from a raspberry pi.
'''
from sensor import Sensor
from metric import Metric
import datetime
import sys
import RPi.GPIO as GPIO
import time

class Sound(Sensor):
    def __init__(self, source, metric_prefix, output, code, pin):
        Sensor.__init__(self, source, metric_prefix, output)

        self.pin = pin
        self.tag_label = code
        self.initPins()

    def __del__(self):
        #destructor to clean up Pins.
        GPIO.cleanup()

    def initPins(self):
        #init pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.IN)

        #allow pin to initialize
        time.sleep(2)

        GPIO.add_event_detect(self.pin, GPIO.BOTH, bouncetime=100)
        GPIO.add_event_callback(self.pin, self.callback)

    def reset(self):
        #clean up first
        try:
            GPIO.cleanup()
        finally:
            self.initPins()

    def callback(self, channel):
        date = datetime.datetime.utcnow()
        name = self.metric_prefix + 'sound'
        if self.output == 'WF':
            name = 'Sound'
            if len(self.metric_prefix) > 0:
                name = self.metric_prefix + '.' + name
        self.metrics.append(Metric(name, 1.0, date))

    def get_info(self):
        pass

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
