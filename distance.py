'''
Copyright (©) 2019 - Randall Simpson
pi-iot

This class is used to gather distance sensor metrics from a raspberry pi.
'''
from sensor import Sensor
from metric import Metric
import datetime
import sys
import RPi.GPIO as GPIO
import time

class Distance(Sensor):
    def __init__(self, source, metric_prefix, output, code, pin_trigger, pin_echo, format):
        Sensor.__init__(self, source, metric_prefix, output)
        
        self.pin_trigger = pin_trigger
        self.pin_echo = pin_echo
        self.format = format
        self.tag_label = code
        #init pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin_trigger, GPIO.OUT)
        GPIO.setup(pin_echo, GPIO.IN)

        GPIO.output(pin_trigger, GPIO.LOW)
        #allow pins to initialize
        time.sleep(2)

    def get_info(self):
        try:
            date = datetime.datetime.utcnow()

            GPIO.output(self.pin_trigger, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(self.pin_trigger, GPIO.LOW)

            while GPIO.input(self.pin_echo) == 0:
                pulse_start_time = time.time()
            while GPIO.input(self.pin_echo) == 1:
                pulse_end_time = time.time()

            pulse_duration = pulse_end_time - pulse_start_time

            distance = round(pulse_duration * 17150, 2)
        finally:
            GPIO.cleanup()

        if distance is not None:
            name = self.metric_prefix + 'distance'
            if self.output == 'WF':
                name = 'Distance'
                if len(self.metric_prefix) > 0:
                    name = self.metric_prefix + '.' + name
            if self.format == 'f':
                distance = distance / 30.48
            if self.format == 'i':
                distance = distance / 30.48 * 12;
            self.metrics.append(Metric(name, distance, date))
        else:
            return None

    def format_metrics(self):
        rtnMetrics = []
        while len(self.metrics) > 0:
            metric = self.metrics.pop()
            if self.output == 'WF':
                tags = {}
                tags['Pin-Trigger'] = self.pin_trigger
                tags['Pin-Echo'] = self.pin_echo
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
                tags['pin-trigger'] = self.pin_trigger
                tags['pin-echo'] = self.pin_echo
                tags['sensor'] = self.tag_label
                m['tags'] = tags
                rtnMetrics.append(m)
        return rtnMetrics
