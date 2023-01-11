FROM python:latest

COPY ./adapter/requirements.txt /tmp

RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt
RUN apt-get update && apt-get install -y netcat

WORKDIR /adapter
COPY ./adapter/adapter.py /adapter
COPY ./adapter/start.sh /adapter

RUN chmod +x /adapter/start.sh

CMD ["./start.sh"]