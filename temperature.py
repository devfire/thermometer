import glob
import time
import sys, os
import pprint
from Adafruit_IO import MQTTClient, Client, RequestError, Feed

class Adafruit(object):
    def __init__(self):
        # We need to make sure the env vars are set correctly
        for env_var in ('ADAFRUIT_IO_USERNAME','ADAFRUIT_IO_KEY'):
            if env_var in os.environ:
                print("Checking for",env_var,"found it!")
            else:
                print(env_var,'not found, exiting!')
                sys.exit(1)

        # Set to your Adafruit IO username.
        self.ADAFRUIT_IO_USERNAME = os.getenv("ADAFRUIT_IO_USERNAME")

        # Set to your Adafruit IO key.
        self.ADAFRUIT_IO_KEY = os.getenv("ADAFRUIT_IO_KEY")

        '''
        Create an instance of the REST client. This is needed to setup the feeds only.
        Data is transferred via MQTT, not via REST.
        '''
        self.http_client = Client(self.ADAFRUIT_IO_USERNAME, self.ADAFRUIT_IO_KEY)

        # Create an MQTT client instance. This is for sending data
        self.mqtt_client = MQTTClient(self.ADAFRUIT_IO_USERNAME, self.ADAFRUIT_IO_KEY)

    def get_http_client():
        return self.http_client

    def get_mqtt_client():
        return self.mqtt_client

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
        print("Sending values for",self.device_id,"to",self.feed_names)

class MultiSensor(Sensor):
    pass

water_sensor = WaterSensor(['watertemp'])

multi_sensor = MultiSensor(['airtemp','pressure','humidity','gas'])

adafruit = Adafruit()

# get a list of all the sensors
sensors_discovered = []
sensors_discovered.append(water_sensor)
sensors_discovered.append(multi_sensor)

for sensor in sensors_discovered:
    sensor.create_feeds()
    sensor.get_values()
