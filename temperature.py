import glob
import time
import sys, os

def verify_credentials():
    for env_var in ('ADAFRUIT_IO_USERNAME','ADAFRUIT_IO_KEY'):
        if env_var in os.environ:
            print("Checking for",env_var,"found it!")
        else:
            print(env_var,'not found, exiting!')
            sys.exit(1)

def set_credentials():
    # Set to your Adafruit IO username.
    ADAFRUIT_IO_USERNAME = os.getenv("ADAFRUIT_IO_USERNAME")

    # Set to your Adafruit IO key.
    ADAFRUIT_IO_KEY = os.getenv("ADAFRUIT_IO_KEY")


def create_clients():
    '''Create an instance of the REST client.
    this is needed to setup the feeds only.
    Data is transferred via MQTT, not via REST.
    '''
    aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

    '''Create an MQTT client instance. This is for sending data'''
    client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

verify_credentials()

set_credentials()

create_clients()

