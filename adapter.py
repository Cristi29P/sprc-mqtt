import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from re import match
from json import loads, dumps
import logging
from datetime import datetime
from os import getenv

INFLUX_HOST = "sprc3_influxdb"
INFLUX_PORT = 8086
BROKER_HOST = "sprc3_broker"
BROKER_PORT = 1883
DB_NAME = "influx_db"

def on_connect(client, userdata, flags, rc):
    client.subscribe("#")
    
def on_message(client, userdata, msg):
    if not match(r'^[^/]+/[^/]+$', msg.topic):
        return

    if getenv('DEBUG_DATA_FLOW') == 'true':
        logging.info(f'Received a message by topic [{msg.topic}]')
    
    process_message(msg, userdata)

def process_message(msg, userdata):
    location, station = msg.topic.split('/')
    payload = loads(msg.payload.decode('utf-8'))

    db_data = []

    try:
        tstamp = datetime.strptime(payload['timestamp'], '%Y-%m-%dT%H:%M:%S%z')

        if getenv('DEBUG_DATA_FLOW') == 'true':
            logging.info(f'Data timestamp is : {tstamp}')
        
    except:
        tstamp = datetime.now()
        
        if getenv('DEBUG_DATA_FLOW') == 'true':
            logging.info('Data timestamp is NOW')

    for key, val in payload.items():
        if type(val) != int and type(val) != float:
            continue

        db_data.append({
			'measurement': f'{station}.{key}',
			'tags': {
				'location': location,
				'station': station
			},
			'time': tstamp.strftime('%Y-%m-%dT%H:%M:%S%z'),
			'fields': {
				'value': float(val)
			}
		})

        if getenv('DEBUG_DATA_FLOW') == 'true':
            logging.info(f'{location}.{station}.{key} {val}')


    if (len(db_data) != 0):
        userdata.write_points(db_data)

def main():
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

    db_client = InfluxDBClient(INFLUX_HOST, INFLUX_PORT)
    db_client.create_database(DB_NAME)
    
    db_client.switch_database(DB_NAME)
    db_client.create_retention_policy('unlimited', 'INF', 2, default=True)

    client = mqtt.Client(userdata=db_client)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()
