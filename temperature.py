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

        # Create an MQTT client instance. This is for sending data
        self.mqtt_client = MQTTClient(self.ADAFRUIT_IO_USERNAME, self.ADAFRUIT_IO_KEY)
        self.mqtt_client.connect()

    def publish(self,feed_name,value):
        # convert C to F for ambient temp only
        if feed_name == 'temperature':
            value = value * 9.0 / 5.0 + 32.0

        value = round(value,2)
        self.mqtt_client.publish(feed_name,value)

class WaterSensor(object):
    def __init__(self,feed_name):
        self.feed_name = feed_name
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
    def get_value(self):
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

            return temp_f

class MultiSensor(object):
    def __init__(self,feed_name):
        self.feed_name = feed_name

        # Create library object using our Bus I2C port
        self.i2c = I2C(board.SCL, board.SDA)
        self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(self.i2c, debug=False)

        # change this to match the location's pressure (hPa) at sea level
        self.bme680.sea_level_pressure = 1013.25 # Raleigh value

    def get_value(self):
        '''
        getattr(object, name[, default]) returns the value of the named attribute of object. 
        Name must be a string. If the string is the name of one of the object’s attributes, 
        the result is the value of that attribute. Also, round it to 2 decimal points.
        '''
        self.reading = getattr(self.bme680,self.feed_name)

        return self.reading


# setup a list of available sensors
water_sensor = WaterSensor('watertemp')
temperature_sensor = MultiSensor('temperature')
pressure_sensor = MultiSensor('pressure')
humidity_sensor = MultiSensor('humidity')
gas_sensor = MultiSensor('gas')

# init the IoT cloud connection object
adafruit = Adafruit()

# create a list of all the sensors
sensors_discovered = []
sensors_discovered.append(water_sensor)
sensors_discovered.append(temperature_sensor)
sensors_discovered.append(pressure_sensor)
sensors_discovered.append(humidity_sensor)
sensors_discovered.append(gas_sensor)

while True:
    for sensor in sensors_discovered:
        current_value = sensor.get_value()
        print(f"Sending {current_value} to {sensor.feed_name}")
        adafruit.publish(sensor.feed_name,current_value)
    time.sleep(11)
