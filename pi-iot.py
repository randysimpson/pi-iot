#!/usr/bin/python3

import sys, getopt
import Adafruit_DHT
import time
import datetime
import requests

def getInfo(sensor, pin, format):
    date = datetime.datetime.utcnow()
    humidity, temp = Adafruit_DHT.read_retry(sensor, pin)
    if temp is not None:
        result = {}
        result['date'] = date
        result['humidity'] = humidity
        if format == 'f':
            result['temperature'] = (temp * 9/5) + 32
        else:
            result['temperature'] = temp
        return result
    else:
        return None

def formatMetric(result, pin, sensor, source, metric_prefix):
    tags = {}
    tags['pin'] = pin
    tags['sensor'] = sensor
    humidity = {}
    humidity['date'] = result['date'].isoformat() + 'Z'
    humidity['metric'] = metric_prefix + 'humidity'
    humidity['value'] = result['humidity']
    humidity['tags'] = tags
    humidity['source'] = source
    temp = {}
    temp['date'] = result['date'].isoformat() + 'Z'
    temp['metric'] = metric_prefix + 'temperature'
    temp['value'] = result['temperature']
    temp['tags'] = tags
    temp['source'] = source
    metrics = [ humidity, temp ]
    return metrics

def formatWFMetric(value, tags, name):
    detail = {}
    detail['value'] = value
    detail['tags'] = tags
    metric = {}
    metric[name] = detail
    return metric

def formatWFTags(pin, sensor):
    tags = {}
    tags['Pin'] = pin
    tags['Sensor'] = sensor
    return tags

def run(delay, sensor, pin, webhook, source, metric_prefix, output, format):
    code = Adafruit_DHT.DHT22
    if sensor == 'DHT11':
        code = Adafruit_DHT.DHT11
    while True:
        time.sleep(delay)
        result = getInfo(code, pin, format)
        if webhook is not None:
            try:
                if output == 'WF':
                    tags = formatWFTags(pin, sensor)
                    humidity = formatWFMetric(result['humidity'], tags, metric_prefix + '.Humidity')
                    temp = formatWFMetric(result['temperature'], tags, metric_prefix + '.Temperature')
                    path = webhook + "?h=" + source + "&d=%d" % (result['date'].timestamp())
                    requests.post(path, json=humidity)
                    requests.post(path, json=temp)
                else:
                    metrics = formatMetric(result, pin, sensor, source, metric_prefix)
                    requests.post(webhook, json=metrics)
            except requests.exceptions.ConnectionError:
                print('Connection error to webhook %s' % (webhook))
        else:
            print(result)

def main(argv):
   iot_type = 'DHT22'
   webhook = None
   source = ''
   metric_prefix = ''
   output = None
   format = 'c'
   delay = 1
   try:
      opts, args = getopt.getopt(argv,"hp:t:w:s:m:o:f:d:",["pin=","type=","webhook=","source=","metric=", "output=", "format=", "delay="])
   except getopt.GetoptError:
      print('pi-iot.py -p <pin> -t <type> -w <webhook> -s <source> -m <metric> -o <output> -f <format> -d <delay>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('pi-iot.py -p <pin> -t <type> -w <webhook> -s <source> -m <metric> -o <output> -f <format> -d <delay>')
         sys.exit()
      elif opt in ("-p", "--pin"):
         pin = int(arg)
      elif opt in ("-s", "--source"):
         source = arg
      elif opt in ("-w", "--webhook"):
         webhook = arg
      elif opt in ("-t", "--type"):
          iot_type = arg
      elif opt in ("-m", "--metric"):
          metric_prefix = arg
      elif opt in ("-o", "--output"):
          output = arg
      elif opt in ("-f", "--format"):
          format = arg
      elif opt in ("-d", "--delay"):
          delay = arg
   #print('pin is %d and type is %s and webhook is %s and source is %s' % (pin, iot_type, webhook, source))
   run(delay, iot_type, pin, webhook, source, metric_prefix, output, format)

if __name__ == "__main__":
   main(sys.argv[1:])
