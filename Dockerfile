FROM resin/rpi-raspbian:latest

RUN apt-get -q update \
  && apt-get upgrade -qy \
  && apt-get -y install \
    python3 \
    python3-setuptools \
    build-essential \
    python3-dev \
    python3-pip \
    git

WORKDIR /app
RUN git clone https://github.com/adafruit/Adafruit_Python_DHT.git

WORKDIR /app/Adafruit_Python_DHT

RUN python3 setup.py install

RUN pip3 install RPi.GPIO

COPY . /app/

WORKDIR /app

ENV pin=$pin
ENV source=$source
ENV webhook=$webhook
ENV type=$type
ENV metric=$metric
ENV output=$output
ENV format=$format
ENV delay=$delay

CMD python3 pi-iot.py -p $pin -t $type -w $webhook -s $source -m $metric -o $output -f $format -d $delay
