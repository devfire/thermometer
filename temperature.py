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
    def __init__(self,feed_names):
        self.feed_names = feed_names
        self.device_id = '28-00000b6ecdd7'

        #root folder where all the devices live
        self.base_dir = '/sys/bus/w1/devices/'

        self.device_folder = glob.glob(self.base_dir + self.device_id)[0]
        self.device_file = self.device_folder + '/w1_slave'

    #read_temp_raw fetches the two lines of the message from the interface.
    def read_temp_raw(self):
        try:
            f = open(self.device_file, 'r')
        except:
            print("Failed to open",self.device_file,"for reading. Exiting.")
            exit(1)
        lines = f.readlines()
        f.close()
        return lines

    '''
    The read_temp function wraps read_temp_raw, checking for bad messages and retrying 
    until it gets a message with 'YES' on end of the first line. 
    The function returns two values, the first being the temperature in degrees C and the second in degree F.
    '''
    def get_values(self):
        print("Sending values for",self.device_id,"to",self.feed_names)
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = __read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            #return temp_c, temp_f
            return round(temp_f,2)

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
    print("Received",sensor.get_values(),"for",sensor.feed_names)
