# pi-iot

** This is not an official wavefront package. **
This package can be used to get metrics from a Raspberry PI 3 device with a DHT11 or DHT22 device attached to a GPIO pin.

## Optional Wavefront Integration

For this package to send metrics to [Wavefront](https://wavefront.com) there will need to be a Wavefront proxy installed on the network that is available to send metrics to.  To send metrics in the Wavefront format set the `output` variable to `WF`

## Usage

You can hook up the DHT11 or DHT22 device to a GPIO pin.

An example is to hook the DHT22 up to GPIO23 and the vcc up to 3.3v at PIN 1 and ground at PIN 14.  Please see the image below:

Once the device is hooked up to the Raspberry PI there are 2 different ways to run the pi-iot software.  1 option is to use the command line and the other is to use docker.

### Variables

variables are defined as follows

##### -p or --pin

The GPIO pin that has the sensor attached.

##### -s or --source

The source that will be used on the metric that is posted.

##### -t or --type

This field is for the type of sensor, current possible values are `DHT11` or `DHT22`.  The default value is `DHT22`.

##### -w or --webhook

Optional parameter for the url/webhook that the metrics should be sent to as a post.

##### -m or --metric

Optional parameter for the prefix to the metric that will be posted.

##### -o or --output

This is optional variable that will determine if the metric should be in the Wavefront format.  To have Wavefront format the output needs to be set to `WF`.

##### -f or --format

The optional format is `f` to have temperature returned in Fahrenheit or `c` or default for Celsius.

##### -d or --delay

Optional parameter that will adjust the delay of the metric measured by seconds.  The default is 1 second.

### Command line

#### Download

On a Raspberry PI 3 download this source code by using the following command:

```sh
git clone https://gitbub.com/randysimpson/pi-iot.git
```

#### Prerequisites

The package will only work if the Adafruit_DHT library is installed.  To install the Adafruit_DHT package please download the code by using:

```sh
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
```

then run:

```sh
cd Adafruit_Python_DHT
python3 setup.py install
```

#### Examples

Example:

```sh
python3 pi-iot.py -p 23 -s backyard -f f
```

Webhook Example:

```sh
python3 pi-iot.py -p 23 -s backyard -w "http://localhost:3000/data" -f f
```

Wavefront proxy example:

```sh
python3 pi-iot.py -p 23 -s backyard -w "http://wfproxy:3878/" -m "IOT" -o WF -f f
```

### Docker

For docker to be able to access the GPIO pins the container must be run with the --privileged argument.

```sh
docker run -ti --privileged -e "pin=23" -e "type=DHT22" -e "source=backyard" -e "format=f" randysimpson/pi-iot:1.0
```

### Kubernetes

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
