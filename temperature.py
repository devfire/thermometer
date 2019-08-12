import glob
import time
import sys, os
from Adafruit_IO import MQTTClient, Client, RequestError, Feed

def init_adafruit():
    # We need to make sure the env vars are set correctly
    for env_var in ('ADAFRUIT_IO_USERNAME','ADAFRUIT_IO_KEY'):
        if env_var in os.environ:
            print("Checking for",env_var,"found it!")
        else:
            print(env_var,'not found, exiting!')
            sys.exit(1)

    # Set to your Adafruit IO username.
    ADAFRUIT_IO_USERNAME = os.getenv("ADAFRUIT_IO_USERNAME")

    # Set to your Adafruit IO key.
    ADAFRUIT_IO_KEY = os.getenv("ADAFRUIT_IO_KEY")

    '''Create an instance of the REST client.
    this is needed to setup the feeds only.
    Data is transferred via MQTT, not via REST.
    '''
    aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

    # Create an MQTT client instance. This is for sending data
    client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

class Sensor(object):
    def __init__(self,feed_names):
        self.feed_names = feed_names

    def get_values(self):
        pass

    def create_feeds(self):
        for feed in self.feed_names:
            print("Creating feed",feed)

class WaterSensor(Sensor):
    def get_values(self):
        self.device_id = '28-00000b6ecdd7'
        print("Temp for",self.device_id)

class MultiSensor(Sensor):
    pass

water_sensor = WaterSensor(['watertemp'])

multi_sensor = MultiSensor(['airtemp','pressure','humidity','gas'])

init_adafruit()

water_sensor.create_feeds()
multi_sensor.create_feeds()
