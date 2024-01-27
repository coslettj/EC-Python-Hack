#!/usr/bin/python

from socket import *
import optparse
import threading
from termcolor import colored
import os
import sys

#
# Check the Banner file
#
def checkBanner(banner, banFile):
    bFound = False
    try:
        f = open(banFile, "r")
        lines = f.readlines()
        for line in lines:
            if line.strip('\n').find(banner) >-1:
                bFound = True
            else:
                if not bFound:
                    bFound = False
        f.close()
        print(bFound)
        return bFound
    except:
        print("[-] Error reading banner file {}".format(banFile))
        return False
    
#       
# Function to open a port
#
def portScan(tgtHosts, tgtPorts, banFile):
    for tgtHost in tgtHosts:
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
#            t = threading.Thread(target=connScan, args=(tgtHost, int(tgtPort), banFile))
#            t.start()
            connScan(tgtHost, int(tgtPort), banFile)
#
# Scan the port
#
def connScan(host, port, banFile):
    # Create a TCP socket
    try:
        # Create a socket
        sock = socket()
        sock.connect((host,port))
        try:
            banner = sock.recv(1024)
            if banner:
                stripBanner = banner.decode('utf-8').rstrip('\n')
                if checkBanner(stripBanner, banFile) == True:
                    print('[+] {}/tcp'.format(port),colored('open','red'), 'Vulnerable banner: {}'.format(banner.decode('utf-8').rstrip('\n')))
                else:
                    print('[+] {}/tcp'.format(port),colored('open','green'), 'Banner: {}'.format(banner.decode('utf-8').rstrip('\n')))
        except:
            print('[+] {}/tcp'.format(port),colored('open','green'))
    except:
        print('[-] {}/tcp'.format(port),colored('closed','red'))
    finally:
        sock.close()

def main():
    parser = optparse.OptionParser('Usage: ' + ' - H <target host> -p <port> -f <vulnerabilites file>')
    parser.add_option('-H', dest='tgtHost', type='string', help='Specify target host')
    parser.add_option('-p', dest='tgtPort', type='string', help='Specify target ports seperated by comma')
    parser.add_option('-f', dest='banFile', type='string', help='Specify the banners file')
    [options, args] = parser.parse_args()
    tgtHosts = str(options.tgtHost).split(',')
    tgtPorts = str(options.tgtPort).split(',')
    banFile = options.banFile
    
    if (tgtHosts[0] == None) | (tgtPorts[0] == None) | (banFile == None):
        print(parser.usage)
        exit(0)
    else:
        if (not os.path.isfile(banFile)):
            print('[-] {} does not exist.'.format(banFile))
        if (not os.access(banFile, os.R_OK)):
            print('[-] {} is not accessible'.format(banFile))
            exit(0)
        else:
            portScan(tgtHosts, tgtPorts, banFile)
        
if __name__ == '__main__':
    main()