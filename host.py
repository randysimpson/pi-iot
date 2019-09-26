'''
Copyright (©) 2019 - Randall Simpson
pi-iot

This class is used to gather host metrics from a raspberry pi.
'''
from sensor import Sensor
from metric import Metric
import os
import datetime

class Host(Sensor):
    def __init__(self, source, metric_prefix, output):
        Sensor.__init__(self, source, metric_prefix, output)

    def get_info(self):
        date = datetime.datetime.utcnow()
        result = {}
        result['date'] = date
        freedata = os.popen('free').read()
        dfdata = os.popen('df').read()
        uptime = os.popen('uptime').read()

        self.convertFree(freedata, date)
        self.convertDF(dfdata, date)
        self.convertUptime(uptime, date)

        return self.format_metrics()

    def convertFree(self, data, date):
        data = self.convertStringToList(data)
        length = len(data)
        for i in range(length):
            if i == 0:
                data[i].insert(0, '')
            else:
                #remove the ":"
                if not data[i][0].endswith(":"):
                    #then 0 and 1 should be combined.
                    del data[i][0]
                data[i][0] = data[i][0][:-1].replace("/", "_")
                colLength = len(data[i])
                for c in range(colLength):
                    if c > 0:
                        name = data[i][0] + "." + data[0][c].replace("/", "-")
                        value = int(data[i][c])
                        self.metrics.append(Metric(name, value, date))

    def convertDF(self, data, date):
        data = self.convertStringToList(data)
        length = len(data)
        for i in range(length):
            if i > 0:
                colLength = len(data[i])
                for c in range(colLength):
                    if c > 0 and c < 4:
                        name = 'disk.' + data[0][c]
                        tag = {}
                        tag['filesystem'] = data[i][0]
                        tag['mount'] = data[i][5]
                        value = int(data[i][c])
                        metric = Metric(name, value, date)
                        metric.tags = tag
                        self.metrics.append(metric)

    def convertUptime(self, data, date):
        data = list(data.replace(",", "").split('  '))
        if len(data) > 1:
            for i in range(len(data)):
                data[i] = list(filter(None, data[i].split(' ')))
        else:
            data = list(filter(None, data[0].split(' ')))
            data = [[data[0], data[1]], [data[2]], [data[4], data[5]], [data[6], data[7], data[8], data[9], data[10]]]
        #check if uptime has days
        uptime = 0
        i = 0
        if len(data) > 3:
            if(len(data[0]) > 2):
                uptime += int(data[i][2]) * 24 * 60
            i+=1
            uptime += self.convertDurationToInt(data[i][0])
        else:
            if len(data) == 3:
                if len(data[i]) == 5:
                    uptime = int(data[i][2]) * 24 * 60
                    uptime += self.convertDurationToInt(data[i][4])
                else:
                    uptime += self.convertDurationToInt(data[i][2])
            else:
                #days
                uptime = int(data[i][2]) * 24 * 60
                if(len(data[i]) > 5):
                    #minutes
                    uptime += int(data[i][4])
                else:
                    uptime += self.convertDurationToInt(data[i][4])
        self.metrics.append(Metric("uptime", uptime, date))
        i+=1
        #users
        users = int(data[i][0])
        self.metrics.append(Metric("users", users, date))
        i+=1
        #load
        minMean = float(data[i][2])
        fiveMinMean = float(data[i][3])
        fifteenMean = float(data[i][4])
        self.metrics.append(Metric("load1min.mean", minMean, date))
        self.metrics.append(Metric("load5min.mean", fiveMinMean, date))
        self.metrics.append(Metric("load15min.mean", fifteenMean, date))

    def convertDurationToInt(self, duration):
        items = duration.split(":")
        if len(items) > 1:
            return (int(items[0]) * 60) + int(items[1])
        else:
            return int(items[0])

    def convertStringToList(self, data):
        data = data.splitlines()
        length = len(data)
        for i in range(length):
            data[i] = list(filter(None, data[i].split(' ')))
        return data

    def format_metrics(self):
        rtnMetrics = []
        hasPrefix = False
        if len(self.metric_prefix) > 0:
            hasPrefix = True
        while len(self.metrics) > 0:
            metric = self.metrics.pop()
            if self.output == 'WF':
                tags = {}
                if hasattr(metric, 'tags'):
                    tags = metric.tags
                detail = {}
                detail['value'] = metric.value
                detail['tags'] = tags
                m = {}
                if hasPrefix:
                    m[self.metric_prefix + '.' + metric.name] = detail
                else:
                    m[metric.name] = detail
                rtnMetrics.append(m)
            else:
                m = {}
                m['date'] = metric.date.isoformat() + 'Z'
                if hasPrefix:
                    m['metric'] = self.metric_prefix + metric.name
                else:
                    m['metric'] = metric.name
                m['value'] = metric.value
                m['source'] = self.source
                if hasattr(metric, 'tags'):
                    m['tags'] = metric.tags
                rtnMetrics.append(m)
        return rtnMetrics
