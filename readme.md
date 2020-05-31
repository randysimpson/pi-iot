# Pi-IOT

This package can be used to get metrics from a Raspberry PI 3 device.  Current metrics available:
1. [Host](#Host)
2. [Temperature/Humidity (DHT11 or DHT22)](#Temperature/Humidity)
3. [Distance (HC-SRO)](#Distance)
4. [Sound (SSM-1 or Funduino KY-060)](#Sound)
5. [Motion (PIR or HC-SR501)](#Motion)
6. [Tilt switch (IDUINO Knock SEO23)](#tilt)
7. [Vibration sensor (SEO53)](#vibration)

To ingest these metrics there needs to be a webhook available by the IOT device.  To use an ingestor that uses a mongodb backend please see [Ingestor](https://github.com/randysimpson/ingestor), another option could be to use Wavefront or some other product.

*Optional Wavefront Integration*

*For this package to send metrics to [Wavefront](https://wavefront.com) there will need to be a Wavefront proxy installed on the network that the IOT device can send metrics to.  To send metrics in the Wavefront format set the `output` variable to `WF`*

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

#### Docker

```sh
docker run -ti randysimpson/pi-iot:latest
```

#### Kubernetes

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
        image: randysimpson/pi-iot:latest
      nodeSelector:
        host: raspberrypi
```

### Temperature/Humidity

The DHT11 or DHT22 device can be connected to a GPIO pin on Raspberry Pi 3.

An example is to hook the DHT22 up to GPIO23 and the vcc up to 3.3v at PIN 1 and ground at PIN 14.  Please see the image below:

![Raspberry Pi wiring](https://github.com/randysimpson/pi-iot/blob/master/images/pi.PNG "Raspberry Pi wiring")

![DHT 22 Temp sensor](https://github.com/randysimpson/pi-iot/blob/master/images/dht22.PNG "DHT 22 Temp sensor")

Once the device is hooked up to the Raspberry PI there are 2 different ways to run the pi-iot software.  1 option is to use the command line and the other is to use docker.

#### Docker

*For docker to be able to access the GPIO pins the container must be run with the --privileged argument.*

```sh
docker run -ti --privileged -e "pin=23" -e "type=DHT22" -e "source=backyard" -e "format=f" randysimpson/pi-iot:latest
```

#### Kubernetes

To create a pod spec an example yaml file with a labeled node as `location=backyard` is given below:

```json
kind: Pod
metadata:
  name: pi-iot
spec:
  containers:
  - name: pi-iot
    image: randysimpson/pi-iot:latest
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

### Distance

The HC-SRO device can be connected to GPIO pins for trigger and echo on Raspberry Pi 3.  The `pin` parameter must contain the trigger pin, then the echo pin as a comma separated string.

![HC-SRO Distance sensor](https://github.com/randysimpson/pi-iot/blob/master/images/hc-sro.PNG "HC-SRO Distance sensor")

#### Docker

*For docker to be able to access the GPIO pins the container must be run with the --privileged argument.*

```sh
docker run -ti --privileged -e "pin=26,24" -e "type=HC-SRO" -e "source=garage" -e "format=f" randysimpson/pi-iot:latest
```

#### Kubernetes

To create a pod spec an example yaml file with a labeled node as `location=garage` is given below:

```json
kind: Pod
metadata:
  name: pi-iot
spec:
  containers:
  - name: pi-iot
    image: randysimpson/pi-iot:latest
    imagePullPolicy: IfNotPresent
    env:
    - name: pin
      value: "24,26"
    - name: source
      value: "garage"
    - name: type
      value: "HC-SRO"
    - name: webhook
      value: "http://wfproxy:3878/"
    - name: format
      value: "f"
    - name: output
      value: "WF"
    securityContext:
      privileged: true
  nodeSelector:
    location: garage
```

### Sound

The [SSM-1](https://www.allelectronics.com/item/ssm-1/sound-sensor-module/1.html) or [Funduino KY-060](https://www.altronics.com.au/p/z6336-microphone-module-sound-detector-for-arduino/) device can be connected to GPIO pin on Raspberry Pi 3.  The `pin` parameter must contain the pin number attached to the black wire.  The yellow wire connects to the ground and the red wire will connect to +3 or +5.

In the following image the yellow wire is connected to pin #39 ground, and the red wire is connected to 3.3 volts pin #17, and the black wire is connected to pin #15 - GPIO 22.

![Raspberry Pi SSM-1 Wires](https://github.com/randysimpson/pi-iot/blob/master/images/pi-ssm-1.PNG "Raspberry Pi SSM-1 Wires")

And when the pi is powered on there is a LED indicator for power, also sensitivity can be adjusted by rotating the screw.

![SSM-1 Sound Sensor Module](https://github.com/randysimpson/pi-iot/blob/master/images/ssm-1.PNG "SSM-1 Sound Sensor Module")

#### Docker

*For docker to be able to access the GPIO pins the container must be run with the --privileged argument.*

```sh
docker run -ti --privileged -e "pin=15" -e "type=SSM-1" -e "source=room" randysimpson/pi-iot:latest
```

#### Kubernetes

To create a pod spec an example yaml file with a labeled node as `location=room` is given below:

```json
kind: Pod
metadata:
  name: pi-iot
spec:
  containers:
  - name: pi-iot
    image: randysimpson/pi-iot:latest
    imagePullPolicy: IfNotPresent
    env:
    - name: pin
      value: "15"
    - name: source
      value: "room"
    - name: type
      value: "SSM-1"
    - name: webhook
      value: "http://wfproxy:3878/"
    - name: format
      value: "f"
    - name: output
      value: "WF"
    securityContext:
      privileged: true
  nodeSelector:
    location: room
```

### Motion

The [HC-SR501](https://www.allelectronics.com/mas_assets/media/allelectronics2018/spec/PIR-7.pdf) without jumper device can be connected to GPIO pin on Raspberry Pi 3.  The `pin` parameter must contain the pin number attached to the `out` terminal.  There is also a `vcc` terminal to connect to +3 or +5, and a `GND` terminal for ground.

![PIR - HC-SR501](https://github.com/randysimpson/pi-iot/blob/master/images/pir.PNG "PIR - HC-SR501")

![PIR - HC-SR501 back](https://github.com/randysimpson/pi-iot/blob/master/images/pir-sr501.PNG "PIR - HC-SR501 back")

#### Docker

If the out wire is connected to pin #15 - GPIO 22:

*For docker to be able to access the GPIO pins the container must be run with the --privileged argument.*

```sh
docker run -ti --privileged -e "pin=15" -e "type=SSM-1" -e "source=room" randysimpson/pi-iot:latest
```

#### Kubernetes

To create a pod spec an example yaml file with a labeled node as `location=room` is given below:

```json
kind: Pod
metadata:
  name: pi-iot
spec:
  containers:
  - name: pi-iot
    image: randysimpson/pi-iot:latest
    imagePullPolicy: IfNotPresent
    env:
    - name: pin
      value: "15"
    - name: source
      value: "room"
    - name: type
      value: "HC-SR501"
    - name: webhook
      value: "http://wfproxy:3878/"
    - name: format
      value: "f"
    - name: output
      value: "WF"
    securityContext:
      privileged: true
  nodeSelector:
    location: room
```

### Tilt

The [tilt switch sensor (SEO23)](https://www.allelectronics.com/mas_assets/media/allelectronics2018/spec/SE-23.pdf) device can be connected to GPIO pin on Raspberry Pi 3.  The `pin` parameter must contain the pin number attached to the `out` terminal.  There is also a `vcc` terminal to connect to +3 or +5, and a `GND` terminal for ground.

![SEO23 - Tilt Sensor](https://github.com/randysimpson/pi-iot/blob/master/images/SEO23.PNG "SEO23 - Tilt Sensor")

#### Docker

If the out wire is connected to pin #15 - GPIO 22:

*For docker to be able to access the GPIO pins the container must be run with the --privileged argument.*

```sh
docker run -ti --privileged -e "pin=15" -e "type=SEO23" -e "source=room" randysimpson/pi-iot:latest
```

#### Kubernetes

To create a pod spec an example yaml file with a labeled node as `location=room` is given below:

```json
kind: Pod
metadata:
  name: pi-iot
spec:
  containers:
  - name: pi-iot
    image: randysimpson/pi-iot:latest
    imagePullPolicy: IfNotPresent
    env:
    - name: pin
      value: "15"
    - name: source
      value: "room"
    - name: type
      value: "SEO23"
    - name: webhook
      value: "http://wfproxy:3878/"
    - name: format
      value: "f"
    - name: output
      value: "WF"
    securityContext:
      privileged: true
  nodeSelector:
    location: room
```

### Vibration

The [vibration shock module SEO53](https://www.allelectronics.com/mas_assets/media/allelectronics2018/spec/SE-53.pdf) device can be connected to GPIO pin on Raspberry Pi 3.  The `pin` parameter must contain the pin number attached to the `S` terminal.  There is also a `vcc` terminal in the middle to connect to +3 or +5, and a `-` terminal for ground.

![SEO53 Vibration Sensor](https://github.com/randysimpson/pi-iot/blob/master/images/SEO53.PNG "SEO53 Vibration Sensor")

#### Docker

If the `S` wire is connected to pin #15 - GPIO 22:

*For docker to be able to access the GPIO pins the container must be run with the --privileged argument.*

```sh
docker run -ti --privileged -e "pin=15" -e "type=SEO53" -e "source=room" randysimpson/pi-iot:latest
```

#### Kubernetes

To create a pod spec an example yaml file with a labeled node as `location=room` is given below:

```json
kind: Pod
metadata:
  name: pi-iot
spec:
  containers:
  - name: pi-iot
    image: randysimpson/pi-iot:latest
    imagePullPolicy: IfNotPresent
    env:
    - name: pin
      value: "15"
    - name: source
      value: "room"
    - name: type
      value: "SEO53"
    - name: webhook
      value: "http://wfproxy:3878/"
    - name: format
      value: "f"
    - name: output
      value: "WF"
    securityContext:
      privileged: true
  nodeSelector:
    location: room
```

## Variables

variables are defined as follows

##### -p or --pin

Optional parameter for the GPIO pin that has the sensor attached.  This parameter is not valid if gathering host metrics.  In the case that the sensor needs more than 1 pin, the pins should be comma separated like `24,26`.

##### -s or --source

Optional parameter for the source that will be used on the metric that is posted, if no source is provided the hostname will be used.

##### -t or --type

This field is for the type of sensor, default value is `HOST`.  Current possible values are:
* `HOST`
* `DHT11`
* `DHT22`
* `HC-SRO`
* `SSM-1`
* `HC-SR501`

##### -w or --webhook

Optional parameter for the url/webhook that the metrics should be sent to as a post.

##### -m or --metric

Optional parameter for the prefix to the metric that will be posted.

##### -o or --output

Optional parameter that will determine if the metric should be in the Wavefront format.  To have Wavefront format the output needs to be set to `WF`.

##### -f or --format

Optional parameter for the format of
* temperature is `f` to have temperature returned in Fahrenheit or `c` or default for Celsius.
* distance is `f` to have distance returned in feet or `i` to have feet returned in inches, default is meters.

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

Another dependency is RPi.GPIO.  To install the RPi.GPIO package please issue the following command:

```sh
pip install RPi.GPIO
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

Distance example:

```sh
python pi-iot.py -p 24,26 -t "HC-SRO" -s garage -w "http://wfproxy:3878/" -m "IOT" -o WF -f f
```

Sound example:

```sh
python pi-iot.py -p 15 -t "SSM-1" -s room -w "http://wfproxy:3878/" -m "IOT" -o WF
```

Copyright (©) 2019 - Randall Simpson
