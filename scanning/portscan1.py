#!/usr/bin/python

import socket
from termcolor import colored

# Create a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Set timeout to 2 seconds
socket.setdefaulttimeout(2)

# Get the host and port from the command line

host = input('Enter host to scan: ')
# port = int(input('Enter port to scan: '))

#
# Function to open a port
#
def portscanner(host, port):
    if sock.connect_ex((host,port)):
        print(colored('Port {} is CLOSED', 'red').format(port))
    else:
        print(colored('Port {} is OPEN', 'green').format(port))

for port in range(1,1000):
    portscanner(host, port)