#!/usr/bin/python3
'''
Copyright (©) 2019 - Randall Simpson
pi-iot

This class is used to run the pi-iot app for gathering and sending metrics from a raspberry pi.
'''
import sys, getopt
import time
import requests
import os
from temp import Temp
from host import Host

def run(delay, sensor_type, pin, webhook, source, metric_prefix, output, format):
    sensor = None
    if sensor_type.startswith('DHT'):
        sensor = Temp(source, metric_prefix, output, sensor_type, pin, format)
    else:
        sensor = Host(source, metric_prefix, output)

    while True:
        metrics = sensor.get_info()
        if webhook is not None:
            try:
                if output == 'WF':
                    path = webhook + "?h=" + source
                    for metric in metrics:
                        requests.post(path + "&d=%d" % (metric['date'].timestamp()), json=metric)
                else:
                    requests.post(webhook, json=metrics)
            except requests.exceptions.ConnectionError:
                print('Connection error to webhook %s' % (webhook))
        else:
            print(metrics)
        time.sleep(delay)

def formatArgs(sentArgs):
   argList = []
   sentArgs = sys.argv[1:]
   for i, arg in enumerate(sentArgs):
      if i + 1 < len(sentArgs):
         nextElement = sentArgs[(i+1) % len(sentArgs)]
         if (nextElement.startswith("-") and arg.startswith("-")) is False:
            argList.append(arg)
      else:
         if not arg.startswith("-"):
            argList.append(arg)
   return argList

def main(argv):
   iot_type = 'HOST'
   webhook = None
   source = ''
   metric_prefix = ''
   output = None
   format = 'c'
   delay = 60
   pin = -1
   try:
      opts, args = getopt.getopt(argv,"hp:t:w:s:m:o:f:d:",["pin=","type=","webhook=","source=","metric=", "output=", "format=", "delay="])
   except getopt.GetoptError:
      print('pi-iot.py -p <pin> -t <type> -w <webhook> -s <source> -m <metric> -o <output> -f <format> -d <delay>')
      sys.exit(2)
   #set default delay for non host metrics to 1 second.
   if "-p" in args or "--pin" in args:
       delay = 1
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
   #check if source was setup.
   if len(source) < 1:
       source = os.popen('hostname').read().replace("\n", "")
   run(delay, iot_type, pin, webhook, source, metric_prefix, output, format)

if __name__ == "__main__":
   argList = formatArgs(sys.argv[1:])
   main(argList)
