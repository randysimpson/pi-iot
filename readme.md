# pi-iot

** This is not an official wavefront package. **

This package can be used to get metrics from a Raspberry PI 3 device.  Currently you can gather host metrics, or you can gather temperature/humidity metrics with a DHT11 or DHT22 device attached to a GPIO pin.

## Optional Wavefront Integration

For this package to send metrics to [Wavefront](https://wavefront.com) there will need to be a Wavefront proxy installed on the network that is available to send metrics to.  To send metrics in the Wavefront format set the `output` variable to `WF`

## Usage

### Host

To get raspberry pi host information you only need to call the script:

```
python pi-iot.py
```

To send information to a webhook:

```
python pi-iot.py -w "http://localhost:3000/data"
```

### Temperature/Humidity

You can hook up the DHT11 or DHT22 device to a GPIO pin.

An example is to hook the DHT22 up to GPIO23 and the vcc up to 3.3v at PIN 1 and ground at PIN 14.  Please see the image below:

![alt text](https://github.com/randysimpson/pi-iot/blob/master/images/pi.PNG "Raspberry Pi wiring")

![alt text](https://github.com/randysimpson/pi-iot/blob/master/images/dht22.PNG "DHT 22 Temp sensor")

Once the device is hooked up to the Raspberry PI there are 2 different ways to run the pi-iot software.  1 option is to use the command line and the other is to use docker.

## Variables

variables are defined as follows

##### -p or --pin

Optional parameter for the GPIO pin that has the sensor attached.  This parameter is not valid if gathering host metrics.

##### -s or --source

Optional parameter for the source that will be used on the metric that is posted, if no source is provided the hostname will be used.

##### -t or --type

This field is for the type of sensor, current possible values are `HOST`, `DHT11` or `DHT22`.  The default value is `HOST`.

##### -w or --webhook

Optional parameter for the url/webhook that the metrics should be sent to as a post.

##### -m or --metric

Optional parameter for the prefix to the metric that will be posted.

##### -o or --output

Optional parameter that will determine if the metric should be in the Wavefront format.  To have Wavefront format the output needs to be set to `WF`.

##### -f or --format

Optional parameter for the format of temperature is `f` to have temperature returned in Fahrenheit or `c` or default for Celsius.

##### -d or --delay

Optional parameter that will adjust the delay of the metric measured by seconds.  The default is 60 seconds for host metrics and 1 second for other sensors.

### Command line

#### Download

On a Raspberry PI 3 download this source code by using the following command:

```sh
git clone https://gitbub.com/randysimpson/pi-iot.git
```

#### Prerequisites

If you are not using Docker or Kubernetes then you must install the Adafruit_DHT library.  To install the Adafruit_DHT package please download the code by using:

```sh
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
```

then run:

```sh
cd Adafruit_Python_DHT
python setup.py install
```

#### pi-iot Examples

Example:

```sh
python pi-iot.py -p 23 -t "DHT22" -s backyard -f f
```

Webhook Example:

```sh
python pi-iot.py -p 23 -t "DHT22" -s backyard -w "http://localhost:3000/data" -f f
```

Wavefront proxy example:

```sh
python pi-iot.py -p 23 -t "DHT22" -s backyard -w "http://wfproxy:3878/" -m "IOT" -o WF -f f
```

### Docker

To run raspberry pi host metrics then issue the following command:

```sh
docker run -ti randysimpson/pi-iot:1.1
```

For docker to be able to access the GPIO pins the container must be run with the --privileged argument.

```sh
docker run -ti --privileged -e "pin=23" -e "type=DHT22" -e "source=backyard" -e "format=f" randysimpson/pi-iot:1.1
```

### Kubernetes

Creating a deployment for raspberry pi host metrics onto a labeled node as `host=raspberrypi`:

```json
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pi-iot
  labels:
    app: pi-iot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pi-iot
  template:
    metadata:
      labels:
        app: pi-iot
    spec:
      containers:
      - name: pi-iot
        image: randysimpson/pi-iot:1.1
      nodeSelector:
        host: raspberrypi
```

To create a pod spec an example yaml file with a labeled node as `location=backyard` is given below:

```json
kind: Pod
metadata:
  name: pi-iot
spec:
  containers:
  - name: pi-iot
    image: randysimpson/pi-iot:1.0
    imagePullPolicy: IfNotPresent
    env:
    - name: pin
      value: "23"
    - name: source
      value: "backyard"
    - name: type
      value: "DHT22"
    - name: webhook
      value: "http://wfproxy:3878/"
    - name: format
      value: "f"
    - name: output
      value: "WF"
    securityContext:
      privileged: true
  nodeSelector:
    location: backyard
```


Copyright (©) 2019 - Randall Simpson
