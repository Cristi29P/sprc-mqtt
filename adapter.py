import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from re import match
from json import loads
import logging
from datetime import datetime
from os import getenv

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

def my_log(logged_msg):
    if getenv('DEBUG_DATA_FLOW') == 'true':
        logging.info(logged_msg)

def on_connect(client, userdata, flags, rc):
    client.subscribe("#")

def on_message(client, userdata, msg):
    if match(r'^[^/]+/[^/]+$', msg.topic):
        my_log(f'Received a message by topic [{msg.topic}]')
        process_message(msg, userdata)

def process_message(msg, userdata):
    splitted_msg = msg.topic.split('/')
    if len(splitted_msg) != 2:
        return
    location = splitted_msg[0]
    station = splitted_msg[1]

    payload = loads(msg.payload.decode('utf-8'))
    db_data = []

    try:
        timestamp = datetime.strptime(payload['timestamp'], '%Y-%m-%dT%H:%M:%S%z')
        my_log(f'Data timestamp is : {timestamp}')
    except:
        timestamp = datetime.now()
        my_log('Data timestamp is NOW')

    db_data = [
        {
            'measurement': f'{station}.{key}',
            'tags': {
                'location': location,
                'station': station
            },
            'time': timestamp.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'fields': {
                'value': val # float
            }
        } for key, val in payload.items() if isinstance(val, (int, float))
        if my_log(f'{location}.{station}.{key} {val}')
    ]

    if (len(db_data) != 0):
        userdata.write_points(db_data)


def main():
    db_client = InfluxDBClient(getenv('INFLUX_HOST', 'sprc3_influxdb'))
    db_client.create_database(getenv('DB_NAME', 'influx_db'))
    db_client.switch_database(getenv('DB_NAME', 'influx_db'))
    db_client.create_retention_policy('unlimited', 'INF', 2, default=True)

    client = mqtt.Client(userdata=db_client)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(getenv('BROKER_HOST', 'sprc3_broker'))
    client.loop_forever()

if __name__ == "__main__":
    main()
