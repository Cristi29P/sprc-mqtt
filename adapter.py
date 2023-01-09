import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from re import match
import json
import logging

def on_connect(client, userdata, flags, rc):
    client.subscribe("#")
    
def on_message(client, userdata, msg):
    if not match(r'^[^/]+/[^/]+$', msg.topic):
        return

    logging.info(f'Received a message by topic [{msg.topic}]')
    process_message(msg)

def process_message(msg):
    location, station = msg.topic.split('/')
    payload = json.loads(msg.payload.decode('utf-8'))




def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("broker", 1883, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()