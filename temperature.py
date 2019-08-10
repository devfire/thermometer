import glob
import time
import sys, os

# Import Adafruit IO REST client.
from Adafruit_IO import MQTTClient, RequestError, Feed

# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = os.getenv("ADAFRUIT_IO_USERNAME")

# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
ADAFRUIT_IO_KEY = os.getenv("ADAFRUIT_IO_KEY")

# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    pass

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    #print('Feed {0} received new value: {1}'.format(feed_id, payload))
    pass

# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

# Connect to the Adafruit IO server.
client.connect()

'''
############### water temp sensor setup #######################
water_device_folder = glob.glob(base_dir + '28-00000b6ecdd7')[0]
water_device_file = water_device_folder + '/w1_slave'
###############################################################

############### air temp sensor setup #######################
air_device_folder = glob.glob(base_dir + '28-0316a2791cfb')[0]
air_device_file = air_device_folder + '/w1_slave'
#############################################################
'''

class Sensor(object):
    def __init__(self,device_id):
        self.device_id = device_id

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
    def read_temp(self):
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

#class AirSensor(Sensor):
   #device_id ='28-0316a2791cfb'
#   feed_name = 'airtemp'

class WaterSensor(Sensor):
   #device_id = '28-00000b6ecdd7'
   feed_name = 'watertemp'

#setup objects
#air_sensor = AirSensor('28-0316a2791cfb')
water_sensor = WaterSensor('28-00000b6ecdd7')

#Setup the feeds
#for sensor in (air_sensor, water_sensor):
'''
sensor = water_sensor
print ('Setting up',sensor.feed_name)
try:
    sensor.temperature = aio.feeds(sensor.feed_name)
except RequestError:
    feed = Feed(name=sensor.feed_name)
    sensor.temperature = aio.create_feed(feed)
'''

# The first option is to run a thread in the background so you can continue
# doing things in your program.
client.loop_background()

#Start sending values
while True:
    #for sensor in (air_sensor, water_sensor):
    sensor = water_sensor
    current_temp = sensor.read_temp()
    print ("Sending temp",current_temp,"from sensor",sensor.device_id,"to feed",sensor.feed_name)
    try:
       #aio.send_data(sensor.temperature.key,current_temp)
       client.publish('watertemp',current_temp)
    except RequestError:
       print ("ERROR: Failed sending data to adafruit")

    time.sleep(5)
