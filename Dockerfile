FROM randysimpson/alpine-rpigpio:armv71

RUN apk add --no-cache --purge -uU git python3-dev gcc linux-headers musl-dev

RUN pip3 install requests

WORKDIR /app
RUN git clone https://github.com/adafruit/Adafruit_Python_DHT.git

WORKDIR /app/Adafruit_Python_DHT

RUN python3 setup.py install

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
