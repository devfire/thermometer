# Import standard python modules.
import random
import sys,os
import time

# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient

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

# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for water temperature changes...')
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe('watertemp')

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print('Feed {0} received new value: {1}'.format(feed_id, payload))


# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

# Connect to the Adafruit IO server.
client.connect()

# This will run a message loop forever, so your program will not get past the loop_blocking call.  This is
# good for simple programs which only listen to events.  For more complex programs
# you probably need to have a background thread loop or explicit message loop like
# the two previous examples above.
client.loop_blocking()
