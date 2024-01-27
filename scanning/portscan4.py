#!/usr/bin/python

from socket import *
import optparse
import threading
from termcolor import colored

#
# 
#


#    
# Function to open a port
#
def portScan(tgtHost, tgtPorts):
    try:
        tgtIP = gethostbyname(tgtHost)
    except:
        print('[-] Unable to resolve {}}'.format(tgtHost))        
    try:
        tgtName = gethostbyaddr(tgtIP)
        print('[+] Scan results for {}'.formT(tgtName[0]))
    except:
        print('[+] Scan results for {}'.format(tgtIP))
    setdefaulttimeout(1)
    
    for tgtPort in tgtPorts:
        t = threading.Thread(target=connScan, args=(tgtHost, int(tgtPort)))
        t.start()
#
# Scan the port
#
def connScan(host, port):
    # Create a TCP socket
    try:
        # Create a socket
        sock = socket()
        sock.connect((host,port))
        try:
            banner = sock.recv(1024)
            if banner:
                print('[+] {}/tcp'.format(port),colored('open','green'), 'Banner: {}'.format(banner.decode('utf-8').rstrip('\n')))
        except:
            print('[+] {}/tcp'.format(port),colored('open','green'))
    except:
        print('[-] {}/tcp'.format(port),colored('closed','red'))
    finally:
        sock.close()

def main():
    parser = optparse.OptionParser('Usage: ' + ' - H <target host> -p <port>')
    parser.add_option('-H', dest='tgtHost', type='string', help='Specify target host')
    parser.add_option('-p', dest='tgtPort', type='string', help='Specify target ports seperated by comma')
    [options, args] = parser.parse_args()
    tgtHost = options.tgtHost
    tgtPorts = str(options.tgtPort).split(',')

    if (tgtHost == None) | (tgtPorts[0] == None):
        print(parser.usage)
        exit(0)
    else:
        portScan(tgtHost, tgtPorts)
        
if __name__ == '__main__':
    main()