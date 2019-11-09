import socket,sys,time,uuid

host = '172.16.1.66'
port = 3333

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print("Failed to create socket, exiting!")
    sys.exit()

#round to the nearest 2 digits
value = 0


while True:
    print("sending..")
    #convert to a string
    valueStr = str(value)
    print (uuid.getnode())
    try:
        client_socket.sendto(valueStr.encode(), (host, port))
    except OSError as msg: 
        print("Error during send!", msg)
        sys.exit()
    time.sleep(.1)
    value = value + 1
