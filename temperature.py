import glob
import time
import sys, os
import pprint
import board
from busio import I2C
import adafruit_bme680
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
    
    def publish(self,feed,value):
        print('Sending',value,'to',feed,'feed')

class Sensor(object):
    def __init__(self,feed_names):
        self.feed_names = feed_names

    # empty method. Subclasses implement this for real.
    def get_values(self):
        pass

    def create_feeds(self):
        for feed in self.feed_names:
            pass
            #print("Creating feed",feed)

class WaterSensor(Sensor):
    def __init__(self,feed_names_watersensor):
        self.feed_names = feed_names_watersensor
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
    NOTE: disabled two values, only returning F for now.
    '''
    def get_values(self):
        #print("Sending values for",self.device_id,"to",self.feed_names)
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

            #init an empty dictionary
            sensor_values = {}

            #assign a value to the feed
            sensor_values[self.feed_names[0]] = round(temp_f,2)

            #return [round(temp_f,2)]
            #this will return a dictionary of "feed_name":"value"
            return sensor_values

class MultiSensor(Sensor):
    def __init__(self,feed_names_multisensor):
        self.feed_names = feed_names_multisensor
        #print("Creating multisensor with",self.feed_names,"names")

        # Create library object using our Bus I2C port
        self.i2c = I2C(board.SCL, board.SDA)
        self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(self.i2c, debug=False)

        # change this to match the location's pressure (hPa) at sea level
        self.bme680.sea_level_pressure = 1013.25 # Raleigh value

    def get_values(self):
        '''init the dict to an empty value.
        This houses the dictionary that will be returned.
        '''
        sensor_values = {}
        '''this iterates over all the feed names.
        For example, if an instance is given temperature,pressure,humidity,gas
        it will iterate over all of these.
        NOTE: the names must match the sensor instance attributes, o/w this will not work.
        '''
        for sensor_reading in self.feed_names:
            '''getattr(object, name[, default])
            Return the value of the named attribute of object. 
            Name must be a string. If the string is the name of one of the object’s attributes, 
            the result is the value of that attribute.
            '''
            reading = getattr(self.bme680,sensor_reading)

            # build up the dict with the feed_name | sensor reading key-value pair
            # round down to 2 decimal places
            sensor_values[sensor_reading] = round(reading,2)

        return sensor_values


# setup a list of available readings
water_sensor = WaterSensor(['watertemp'])
multi_sensor = MultiSensor(['temperature','pressure','humidity','gas'])

# init the IoT cloud connection object
adafruit = Adafruit()

# create a list of all the sensors
sensors_discovered = []
sensors_discovered.append(water_sensor)
sensors_discovered.append(multi_sensor)

for sensor in sensors_discovered:
    #first, lets make sure the feeds exist
    sensor.create_feeds()

    '''ok, the feeds have been created, let's get the values
    current_value_dict will contain a {"feed name":"feed value"}
    '''
    current_value_dict = sensor.get_values()
    for feed in current_value_dict:
        print(f"Sending {current_value_dict[feed]} to {feed}")
