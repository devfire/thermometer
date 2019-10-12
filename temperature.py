import glob
import time
import sys, os
import pprint
import board
import socket
import re,uuid
import hashlib
import json
from busio import I2C
import adafruit_bme680

class Sender(object):
    def __init__(self):

        #define the target IP
        self.host = 'htpc.coontie.com'

        #define the target port
        self.port = 3333
        
        try:
            #attempt to create a socket, exit if failed
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print("Failed to create socket, exiting!")
            sys.exit()

        #get the machine MAC address. This is useful to differentiate between the devices.
        self.mac = str(':'.join(re.findall('..', '%012x' % uuid.getnode())))

    def publish(self,feed_name,value):
        # convert C to F for ambient temp only
        if feed_name == 'temperature':
            value = value * 9.0 / 5.0 + 32.0

        #round to the nearest 2 digits
        value = round(value,2)

        #get the JSON object ready, make it a string
        payload_json = json.dumps({'mac':self.mac, 'feedName':feed_name, 'value':value})

        try:
            self.client_socket.sendto(payload_json.encode(), (self.host, self.port))
        except OSError as msg: 
            print("Error during send!", msg)
            sys.exit()

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
        the result is the value of that attribute.
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
sender = Sender()

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
        sender.publish(sensor.feed_name,current_value)
    time.sleep(10)
